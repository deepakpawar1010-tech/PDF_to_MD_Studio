"""
PDF_to_MD_Studio v1.0 - Post-Processing / Auto-Cleanup
========================================================
Regex-based fixes for common, well-understood Marker conversion mistakes.

This module is intentionally conservative: every fix here targets a specific,
verified pattern rather than trying to "guess" at general formatting issues.
Each fix returns a count of how many times it fired, so the UI can show
exactly what changed before anything gets saved.
"""

import re
from typing import Dict, List, Tuple


def fix_trailing_question_numbers(content: str) -> Tuple[str, int]:
    """
    Fixes the reading-order mistake where a question number lands AFTER the
    question text instead of before it, e.g.:

        Which of the following is a polynomial? 1.
        Degree of the polynomial x^3 is 3.

    becomes:

        1. Which of the following is a polynomial?
        3. Degree of the polynomial x^3 is

    APPROACH: tracks the document's actual question sequence (1, 2, 3, 4...)
    and only treats a trailing number as misplaced when it EXACTLY matches the
    next expected question number - a much stronger signal than a bare
    "ends in a number" pattern, since a coincidental match to the specific
    next-expected value is very unlikely.

    Scans LINE BY LINE rather than by paragraph block, since in practice the
    misplaced number often sits on a line immediately followed (no blank
    line) by the first answer option - a paragraph-level scan can't see past
    that. The trailing pattern specifically requires a literal "." right
    before the line end, which naturally excludes "N) value" style answer
    option lines (no trailing period), so there's no collision risk there.
    """
    lines = content.split("\n")
    leading_re = re.compile(r"^(\d{1,3})\.\s+\S")
    trailing_re = re.compile(r"^(.*\S)\s+(\d{1,3})\.\s*$")
    # This specific worksheet structure has TWO independent numbering runs:
    # one for the main question set, and a second one that restarts exactly
    # once - the first time a "JEE MAIN & ADVANCED" heading appears - then
    # continues WITHOUT further resets through every subsequent Level/Type
    # subsection. Only the first occurrence resets; later occurrences of the
    # same heading (before Level 2, Level 3, etc.) must NOT reset again.
    section_restart_re = re.compile(r"jee\s+main\s*(&|and)\s*advanced", re.IGNORECASE)

    expected = 1
    count = 0
    seen_restart_heading = False
    fixed_lines: List[str] = []

    for line in lines:
        stripped = line.strip()

        if not stripped:
            fixed_lines.append(line)
            continue

        # Strip stray markdown formatting (bold/italic markers) before
        # checking for the section-reset heading - Marker's bolding is
        # often inconsistent (e.g. "**JEE MAIN** **& ADVANCED**" split
        # across separate bold spans), which would otherwise hide the
        # heading from a plain text search.
        stripped_for_heading_check = re.sub(r"[*_]", "", stripped)
        if not seen_restart_heading and section_restart_re.search(stripped_for_heading_check):
            seen_restart_heading = True
            expected = 1
            fixed_lines.append(line)
            continue

        leading_match = leading_re.match(stripped)
        if leading_match:
            leading_num = int(leading_match.group(1))
            if leading_num == expected or (expected < leading_num <= expected + 3):
                expected = leading_num + 1
                fixed_lines.append(line)
                continue

        trailing_match = trailing_re.match(stripped)
        if trailing_match:
            text, number = trailing_match.group(1), trailing_match.group(2)
            number_int = int(number)
            # Exact match, OR a small forward gap (up to 3) - this handles
            # cases where an earlier question's number was lost entirely
            # (not misplaced, just missing), which would otherwise permanently
            # desync the counter for everything that follows.
            if number_int == expected or (expected < number_int <= expected + 3):
                text_clean = re.sub(r"^[-*]\s+", "", text.strip())
                fixed_lines.append(f"{number}. {text_clean}")
                count += 1
                expected = number_int + 1
                continue

        fixed_lines.append(line)

    return "\n".join(fixed_lines), count


def strip_bullet_before_question_number(content: str) -> Tuple[str, int]:
    """
    Fixes a stray bullet marker sitting in front of an already-correct
    question number, e.g.:

        - 5. The degree of a monomial '108' is

    becomes:

        5. The degree of a monomial '108' is

    This is purely cosmetic (the number itself is already in the right
    place) but the redundant "- " prefix renders as a bullet dot in front
    of the visible number, making it look like "• 5. Text" instead of a
    clean numbered question.
    """
    pattern = re.compile(r"(?m)^[ \t]*[-*]\s+(\d{1,3}\.\s+\S.*)$")
    count = len(pattern.findall(content))
    fixed = pattern.sub(r"\1", content)
    return fixed, count


def strip_bullet_before_option_letter(content: str) -> Tuple[str, int]:
    """
    Fixes a stray bullet marker sitting in front of an already-correct
    lettered answer option, e.g.:

        - B)  $A = \\pi / 2$

    becomes:

        B)  $A = \\pi / 2$

    Same idea as strip_bullet_before_question_number, but for multiple-choice
    option letters (A/B/C/D/E/F) instead of question numbers - very common
    in exam-paper style documents where each option got its own bullet.
    """
    pattern = re.compile(r"(?m)^[ \t]*[-*]\s+([A-F]\)\s*\S.*)$")
    count = len(pattern.findall(content))
    fixed = pattern.sub(r"\1", content)
    return fixed, count


def convert_simple_display_math_to_inline(content: str) -> Tuple[str, int]:
    """
    Converts $$...$$ (display/block math) to $...$ (inline math) when the
    equation is simple - Marker often wraps even short expressions like
    $$x^2 - 6x + 4$$ in display-math delimiters when they'd read better
    inline with the surrounding text.

    Leaves $$...$$ UNTOUCHED when it contains:
    - A line break (\\\\) - likely a matrix, aligned block, or system of
      equations that genuinely needs display-mode rendering
    - \\begin{...} environments (pmatrix, bmatrix, cases, aligned, vmatrix,
      etc.) - same reason, these break if forced inline

    This distinction matters: blindly converting every $$ to $ would mangle
    matrices and multi-line equation systems, which need the extra vertical
    space and centering that only display mode provides.
    """
    pattern = re.compile(r"\$\$(.+?)\$\$", re.DOTALL)
    count = 0

    def _replacer(match: re.Match) -> str:
        nonlocal count
        inner = match.group(1)
        if "\\begin{" in inner or "\\\\" in inner:
            return match.group(0)  # needs display mode - leave untouched
        count += 1
        return f"${inner.strip()}$"

    fixed = pattern.sub(_replacer, content)
    return fixed, count


def strip_bullet_before_numbered_option(content: str) -> Tuple[str, int]:
    """
    Fixes a stray bullet marker sitting in front of an already-correct
    NUMBERED answer option (as opposed to a lettered one), e.g.:

        - 1) Backward direction
        - 2) Forward direction

    becomes:

        1) Backward direction
        2) Forward direction

    Distinct from strip_bullet_before_question_number, which targets
    question numbers in "N. " (period) format - this targets answer
    OPTIONS in "N) " (closing paren) format, which is a different,
    non-overlapping pattern.
    """
    pattern = re.compile(r"(?m)^[ \t]*[-*]\s+(\d{1,2}\)\s*\S.*)$")
    count = len(pattern.findall(content))
    fixed = pattern.sub(r"\1", content)
    return fixed, count


def collapse_excess_blank_lines(content: str) -> Tuple[str, int]:
    """Collapses 3+ consecutive blank lines down to exactly 2 (one visual gap)."""
    pattern = re.compile(r"\n{4,}")
    count = len(pattern.findall(content))
    fixed = pattern.sub("\n\n\n", content)
    return fixed, count


def strip_trailing_whitespace(content: str) -> Tuple[str, int]:
    """Removes trailing spaces/tabs at the end of each line."""
    pattern = re.compile(r"[ \t]+$", re.MULTILINE)
    count = len(pattern.findall(content))
    fixed = pattern.sub("", content)
    return fixed, count


def fix_corrupted_math_subscripts(content: str) -> Tuple[str, int]:
    """
    Fixes common OCR glitches in mathematical combinations and permutations:
        ${}^nC_{\\cdot \\cdot}$ -> ${}^nC_r$
        ${}^nC_{.}$ -> ${}^nC_r$
        ${}^nP =$ -> ${}^nP_r =$
        ${}^4C x^{4-r}$ -> ${}^4C_r x^{4-r}$
    """
    count = 0

    # Fix ^{n}C. or ^{n}C.. or ^{n}C_{\\cdot \\cdot} -> ^{n}C_r
    pattern_c = re.compile(r"\^\{?n\}?C[_\s]*\{?(?:\\cdot\s*|\.|\s)+\}?", re.IGNORECASE)
    matches_c = len(pattern_c.findall(content))
    if matches_c:
        content = pattern_c.sub(r"^{n}C_r", content)
        count += matches_c

    # Fix ^{n}P = -> ^{n}P_r =
    pattern_p = re.compile(r"\^\{?n\}?P\s*(=|:)", re.IGNORECASE)
    matches_p = len(pattern_p.findall(content))
    if matches_p:
        content = pattern_p.sub(r"^{n}P_r \1", content)
        count += matches_p

    # Fix ^{4}C x^{4-r} -> ^{4}C_r x^{4-r}
    pattern_num_c = re.compile(r"\^\{?(\d{1,2})\}?C\s+([a-zA-Z])\^", re.IGNORECASE)
    matches_num_c = len(pattern_num_c.findall(content))
    if matches_num_c:
        content = pattern_num_c.sub(r"^{\1}C_r \2^", content)
        count += matches_num_c

    return content, count


def fix_split_inline_math(content: str) -> Tuple[str, int]:
    """
    Fixes fragmented math blocks where operators are outside delimiters:
        $x$ $+$ $2$ -> $x + 2$
        $n$ $-$ $r$ -> $n - r$
    """
    pattern = re.compile(r"\$([a-zA-Z0-9\(\)\{\}\\]+)\$\s*([\+\-\=\<\>\*\/])\s*\$([a-zA-Z0-9\(\)\{\}\\]+)\$")
    count = len(pattern.findall(content))
    if count:
        content = pattern.sub(r"$\1 \2 \3$", content)
    return content, count


def fix_replacement_characters(content: str) -> Tuple[str, int]:
    """
    Fixes replacement characters (U+FFFD ) produced by OCR or font encoding issues:
        n -> $n$
         -> '
    """
    count = 0
    p1 = re.compile(r"\ufffd([a-zA-Z0-9])\ufffd")
    m1 = len(p1.findall(content))
    if m1:
        content = p1.sub(r"$\1$", content)
        count += m1

    p2 = re.compile(r"\ufffd")
    m2 = len(p2.findall(content))
    if m2:
        content = p2.sub(r"'", content)
        count += m2

    return content, count


# Registry of available fixes - each is (id, label, function).
# Kept as a list of tuples (not a dict) to preserve a deterministic run order:
# question-number fix first (most impactful), math fixes, whitespace cleanup last.
AVAILABLE_FIXES = [
    ("trailing_question_numbers", "Fix misplaced question numbers", fix_trailing_question_numbers),
    ("corrupted_math_subscripts", "Repair corrupted math formulas (combinations & permutations)", fix_corrupted_math_subscripts),
    ("split_inline_math", "Join split inline math expressions ($x$ + $y$)", fix_split_inline_math),
    ("fix_replacement_characters", "Fix unicode replacement characters ()", fix_replacement_characters),
    ("strip_bullet_before_number", "Remove stray bullet before question numbers", strip_bullet_before_question_number),
    ("strip_bullet_before_option", "Remove stray bullet before answer options (A/B/C/D)", strip_bullet_before_option_letter),
    ("strip_bullet_before_numbered_option", "Remove stray bullet before numbered options (1/2/3/4)", strip_bullet_before_numbered_option),
    ("simple_display_to_inline_math", "Convert simple $$ display math to inline $", convert_simple_display_math_to_inline),
    ("collapse_blank_lines", "Collapse excess blank lines", collapse_excess_blank_lines),
    ("strip_trailing_whitespace", "Strip trailing whitespace", strip_trailing_whitespace),
]


def run_cleanup(content: str, enabled_fix_ids: List[str] = None) -> Tuple[str, Dict[str, int]]:
    """
    Run the selected cleanup fixes over content, in a fixed safe order.

    Args:
        content: The raw markdown/text content to clean.
        enabled_fix_ids: List of fix ids to run (from AVAILABLE_FIXES). If None,
            runs all available fixes.

    Returns:
        (cleaned_content, {fix_id: number_of_fixes_applied})
    """
    if enabled_fix_ids is None:
        enabled_fix_ids = [fix_id for fix_id, _, _ in AVAILABLE_FIXES]

    results: Dict[str, int] = {}
    current = content

    for fix_id, _label, fix_fn in AVAILABLE_FIXES:
        if fix_id not in enabled_fix_ids:
            continue
        current, count = fix_fn(current)
        results[fix_id] = count

    return current, results