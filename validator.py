"""Validator module - validates optimization suggestions."""

from typing import List, Dict


class Validator:
    """Validates optimization suggestions to ensure they are reasonable."""

    def validate(self, code: str, suggestions: List[Dict]) -> List[Dict]:
        """Validate suggestions and return those that pass validation."""
        validated = []

        for suggestion in suggestions:
            if self._is_valid(suggestion):
                validated.append(suggestion)

        return validated

    def _is_valid(self, suggestion: Dict) -> bool:
        """Check if a suggestion passes validation rules."""
        if not suggestion.get("message"):
            return False

        priority = suggestion.get("priority", "medium")
        if priority == "critical":
            return False

        return True