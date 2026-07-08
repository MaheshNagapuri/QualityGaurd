"""
Centralized JSON extraction utility for TaskOutput parsing.

Handles all JSON extraction from CrewAI TaskOutput objects across the codebase.
Single source of truth for output parsing logic.
"""

import json
import re
from typing import Any, Optional, Dict


# Extract structured JSON from TaskOutput, dict, or text using layered fallbacks and key validation.
def extract_json_from_output(output: Any, required_keys: Optional[list] = None) -> Dict[str, Any]:
    """
    Extract JSON from various output formats.

    Handles TaskOutput objects, strings, dicts with multiple fallback strategies.
    Works for all agents and tasks, including formatted text from tools.

    Args:
        output: TaskOutput object, string, or dict
        required_keys: List of keys that must exist in output (validation)

    Returns:
        Extracted JSON as dict, or empty dict if extraction fails

    Raises:
        Nothing - always returns a dict (empty on failure)
    """
    if not output:
        return {}

    # Strategy 1: Check if TaskOutput has json_dict
    if hasattr(output, 'json_dict') and output.json_dict:
        if isinstance(output.json_dict, dict):
            if _validate_keys(output.json_dict, required_keys):
                return output.json_dict

    # Strategy 2: Parse raw string output (JSON or formatted text)
    if hasattr(output, 'raw') and isinstance(output.raw, str):
        parsed = _extract_json_from_string(output.raw)
        if parsed and _validate_keys(parsed, required_keys):
            return parsed

        # Try parsing formatted text from tools (Cost Impact Analysis, etc.)
        parsed = _extract_from_formatted_text(output.raw)
        if parsed and _validate_keys(parsed, required_keys):
            return parsed

    # Strategy 3: Check if it's already a dict
    if isinstance(output, dict):
        if _validate_keys(output, required_keys):
            return output

    # Strategy 4: Try parsing string representation
    if isinstance(output, str):
        parsed = _extract_json_from_string(output)
        if parsed and _validate_keys(parsed, required_keys):
            return parsed

        # Try parsing formatted text
        parsed = _extract_from_formatted_text(output)
        if parsed and _validate_keys(parsed, required_keys):
            return parsed

    # All strategies failed
    return {}


# Parse the most complete valid JSON object found inside a free-form text string.
def _extract_json_from_string(text: str) -> Optional[Dict[str, Any]]:
    """
    Extract JSON object from text string.

    Handles:
    - Markdown code blocks (```json...```)
    - Multiple JSON objects (returns largest/most complete)
    - Malformed JSON with extra text

    Args:
        text: String potentially containing JSON

    Returns:
        Parsed JSON dict or None if no valid JSON found
    """
    if not isinstance(text, str):
        return None

    text = text.strip()

    # Remove markdown code blocks
    text = re.sub(r'```(?:json)?\s*', '', text)
    text = re.sub(r'\s*```', '', text)
    text = text.strip()

    # Find all potential JSON matches (largest first = most complete)
    json_matches = list(re.finditer(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', text, re.DOTALL))

    if not json_matches:
        return None

    # Try each match, sorted by length (longest = most likely complete)
    matches_sorted = sorted(json_matches, key=lambda m: len(m.group(0)), reverse=True)

    for json_match in matches_sorted:
        try:
            parsed = json.loads(json_match.group(0))
            if isinstance(parsed, dict) and len(parsed) > 0:
                return parsed
        except json.JSONDecodeError:
            continue

    return None


# Convert known human-readable tool output (like Cost Impact text) into normalized JSON fields.
def _extract_from_formatted_text(text: str) -> Optional[Dict[str, Any]]:
    """
    Extract data from formatted text output (e.g., tool outputs).

    Handles formats like:
    - Cost Impact Analysis:
      - Estimated Defective Units: 619
      - Total Financial Impact: $213,633.38
      - Risk Level: CRITICAL

    Args:
        text: Formatted text string

    Returns:
        Parsed dict or None if no match
    """
    if not isinstance(text, str) or not text.strip():
        return None

    result = {}

    # Extract Cost Impact Analysis data
    if "Cost Impact Analysis" in text or "Estimated Defective Units" in text:
        # Match patterns like "- Key: value" or "- Key: $value" or "- Key: value%"
        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            if not line.startswith('-'):
                continue

            # Remove leading dash and split on colon
            line = line[1:].strip()
            if ':' not in line:
                continue

            key, value = line.split(':', 1)
            key = key.strip().lower()
            value = value.strip()

            # Map readable names to JSON keys
            key_map = {
                "estimated defective units": "estimated_defective_units",
                "estimated returned units": "estimated_returned_units",
                "total affected units": "total_affected_units",
                "direct loss": "direct_loss",
                "handling costs": "handling_costs",
                "total financial impact": "total_financial_impact",
                "risk level": "risk_level",
            }

            json_key = key_map.get(key)
            if json_key:
                # Clean up value (remove $ and commas)
                value = value.replace('$', '').replace(',', '').strip()
                try:
                    # Try to convert to float/int
                    if '.' in value:
                        result[json_key] = float(value)
                    else:
                        result[json_key] = int(value) if value.isdigit() else value
                except (ValueError, AttributeError):
                    result[json_key] = value

    return result if result else None


# Check that parsed data contains all required keys before accepting it as valid output.
def _validate_keys(data: Dict[str, Any], required_keys: Optional[list] = None) -> bool:
    """
    Validate that required keys exist in dict.

    Args:
        data: Dictionary to validate
        required_keys: List of required keys (None = skip validation)

    Returns:
        True if all required keys present or required_keys is None
    """
    if required_keys is None:
        return True

    if not isinstance(data, dict):
        return False

    return all(key in data for key in required_keys)


# Fetch one key from extracted output safely, returning a fallback when the key is missing.
def get_value(output: Any, key: str, default: Any = None) -> Any:
    """
    Extract a specific value from output by key.

    Convenience function for extracting single values.

    Args:
        output: TaskOutput or dict
        key: Key to extract
        default: Default value if key not found

    Returns:
        Value for key, or default if not found
    """
    data = extract_json_from_output(output)
    return data.get(key, default)
