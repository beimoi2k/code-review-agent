"""Optimizer module - generates optimization suggestions based on analysis."""

from typing import List, Dict


class Optimizer:
    """Generates optimization suggestions for identified code issues."""

    def optimize(self, code: str, issues: List[Dict]) -> List[Dict]:
        """Generate optimization suggestions based on issues found."""
        suggestions = []

        for issue in issues:
            suggestion = self._generate_suggestion(code, issue)
            if suggestion:
                suggestions.append(suggestion)

        return suggestions

    def _generate_suggestion(self, code: str, issue: Dict) -> Dict:
        """Generate a single optimization suggestion for an issue."""
        issue_type = issue.get("type", "")

        suggestion_map = {
            "high_complexity": {
                "message": f"Consider refactoring '{issue.get('message', 'function')}' to reduce complexity",
                "action": "refactor",
                "priority": "high"
            },
            "naming_violation": {
                "message": "Use snake_case for function names",
                "action": "rename",
                "priority": "low"
            },
            "bare_except": {
                "message": "Use specific exception types instead of bare except",
                "action": "replace",
                "priority": "medium"
            },
            "syntax_error": {
                "message": "Fix syntax error before proceeding",
                "action": "fix",
                "priority": "high"
            }
        }

        return suggestion_map.get(issue_type, {
            "message": f"Review suggested for: {issue.get('message', 'unknown issue')}",
            "action": "review",
            "priority": "medium"
        })