"""
Centralized Input Sanitization & Safe Coercion Layer
Phase 4: Enterprise Hardening & Defensive Ingestion Guard

Provides bulletproof coercion for all numeric, categorical, and boolean inputs,
safeguarding the ML feature pipeline and prediction engines against malformed,
adversarial, or corrupted types (e.g., string representations of numbers,
word numbers like 'thirty-five', missing nested fields, and fuzz attacks).
"""

import re
import math
from typing import Any, Optional, Dict, Union

# Word to number mapping for textual demographics & survey answers
WORD_TO_NUM: Dict[str, float] = {
    "zero": 0.0, "none": 0.0, "nil": 0.0,
    "one": 1.0, "two": 2.0, "three": 3.0, "four": 4.0, "five": 5.0,
    "six": 6.0, "seven": 7.0, "eight": 8.0, "nine": 9.0, "ten": 10.0,
    "eleven": 11.0, "twelve": 12.0, "thirteen": 13.0, "fourteen": 14.0,
    "fifteen": 15.0, "sixteen": 16.0, "seventeen": 17.0, "eighteen": 18.0,
    "nineteen": 19.0, "twenty": 20.0, "thirty": 30.0, "forty": 40.0,
    "fifty": 50.0, "sixty": 60.0, "seventy": 70.0, "eighty": 80.0,
    "ninety": 90.0, "hundred": 100.0
}


def parse_word_number(text: str) -> Optional[float]:
    """
    Parses compound word numbers such as 'thirty-five', 'twenty one', or single words.
    """
    clean = text.lower().strip().replace("-", " ")
    parts = clean.split()
    if not parts:
        return None

    total = 0.0
    matched = False
    for p in parts:
        if p in WORD_TO_NUM:
            total += WORD_TO_NUM[p]
            matched = True
        else:
            # Check if token itself is numeric
            try:
                total += float(p)
                matched = True
            except ValueError:
                pass

    return total if matched else None


def safe_float(
    val: Any,
    default: Optional[float] = 0.0,
    min_val: Optional[float] = None,
    max_val: Optional[float] = None
) -> Optional[float]:
    """
    Safely coerces any arbitrary value to float without crashing.
    Handles numeric types, numeric strings, word-numbers ('thirty-five'),
    fuzzed text, None, and NaN.
    Optionally clamps to [min_val, max_val].
    """
    def _fallback():
        return float(default) if default is not None else None

    if val is None:
        result = _fallback()
    elif isinstance(val, (int, float)):
        if math.isnan(val) or math.isinf(val):
            result = _fallback()
        else:
            result = float(val)
    elif isinstance(val, bool):
        result = 1.0 if val else 0.0
    else:
        # Value is string, object, or composite
        s = str(val).strip()
        if not s:
            result = _fallback()
        else:
            # 1. Try direct float conversion
            try:
                result = float(s)
            except ValueError:
                # 2. Try word number parsing (e.g. 'thirty-five', 'none')
                word_num = parse_word_number(s)
                if word_num is not None:
                    result = word_num
                else:
                    # 3. Try extracting first floating-point or integer substring (e.g. '7 hours', '~25.5 ng/mL')
                    match = re.search(r"[-+]?(?:\d*\.\d+|\d+)", s)
                    if match:
                        try:
                            result = float(match.group(0))
                        except ValueError:
                            result = _fallback()
                    else:
                        result = _fallback()

    # Biological clamping if specified and result is not None
    if result is not None:
        if min_val is not None:
            result = max(float(min_val), result)
        if max_val is not None:
            result = min(float(max_val), result)

    return result


def safe_int(
    val: Any,
    default: Optional[int] = 0,
    min_val: Optional[int] = None,
    max_val: Optional[int] = None
) -> Optional[int]:
    """
    Safely coerces arbitrary value to integer.
    """
    flt = safe_float(
        val,
        default=float(default) if default is not None else None,
        min_val=float(min_val) if min_val is not None else None,
        max_val=float(max_val) if max_val is not None else None
    )
    if flt is None:
        return None
    try:
        return int(round(flt))
    except Exception:
        return default


def safe_bool(val: Any, default: bool = False) -> bool:
    """
    Safely coerces truthy/falsy strings ('true', '1', 'yes', 'on') and booleans.
    """
    if val is None:
        return default
    if isinstance(val, bool):
        return val
    if isinstance(val, (int, float)):
        return bool(val != 0)
    s = str(val).strip().lower()
    if s in ["true", "1", "yes", "y", "t", "on"]:
        return True
    if s in ["false", "0", "no", "n", "f", "off", "none", "null"]:
        return False
    return default


def normalize_numeric_feature(
    val: Any,
    default: float,
    min_val: Optional[float] = None,
    max_val: Optional[float] = None
) -> float:
    """
    Normalizes a clinical feature by safely coercing to float and clamping
    to physiological plausibility boundaries.
    """
    return safe_float(val, default=default, min_val=min_val, max_val=max_val)
