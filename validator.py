"""Validator module - validates and scores optimization suggestions with feedback."""

from typing import List, Dict, Tuple
import re


class Validator:
    """Validates optimization suggestions and provides feedback optimization."""

    def __init__(self):
        self.validation_history = []
        self.confidence_scores = {}

    def validate(self, code: str, suggestions: List[Dict]) -> List[Dict]:
        """Validate suggestions and return those that pass validation."""
        validated = []
        for suggestion in suggestions:
            result = self._validate_single(code, suggestion)
            if result["is_valid"]:
                # Merge original suggestion fields into result
                merged = {**suggestion, **result}
                validated.append(merged)
        self.validation_history.append(validated)
        return validated

    def _validate_single(self, code: str, suggestion: Dict) -> Dict:
        """Validate a single suggestion against code context."""
        suggestion_type = suggestion.get("type", "")
        priority = suggestion.get("priority", "medium")
        message = suggestion.get("message", "")

        result = {
            "is_valid": True,
            "confidence": 0.8,
            "warnings": [],
            "score": 0.0
        }

        # Critical priority auto-reject check
        if priority == "critical":
            if suggestion_type not in ("code_injection_risk", "syntax_error"):
                result["is_valid"] = False
                result["warnings"].append("Critical suggestions must be related to security or syntax")
                return result

        # Check for empty or invalid messages
        if not message or len(message) < 5:
            result["is_valid"] = False
            result["warnings"].append("Suggestion message is too short or empty")
            return result

        # Validate based on issue type
        validation_rules = {
            "high_complexity": self._validate_complexity,
            "bare_except": self._validate_except,
            "naming_violation": self._validate_naming,
            "code_injection_risk": self._validate_security,
            "too_many_parameters": self._validate_parameters,
        }

        if suggestion_type in validation_rules:
            type_result = validation_rules[suggestion_type](code, suggestion)
            result.update(type_result)

        # Calculate overall score
        result["score"] = self._calculate_score(result)

        return result

    def _validate_complexity(self, code: str, suggestion: Dict) -> Dict:
        """Validate complexity-related suggestions."""
        result = {"is_valid": True, "confidence": 0.9}
        complexity_match = re.search(r'complexity (\d+)', suggestion.get("message", ""))
        if complexity_match:
            complexity = int(complexity_match.group(1))
            if complexity < 5:
                result["is_valid"] = False
                result["warnings"] = ["Complexity is too low to warrant a suggestion"]
            elif complexity > 20:
                result["confidence"] = 0.7
                result["warnings"] = ["Very high complexity may not be fixable with simple refactoring"]
        return result

    def _validate_except(self, code: str, suggestion: Dict) -> Dict:
        """Validate exception handling suggestions."""
        result = {"is_valid": True, "confidence": 0.85}
        if "specific" in suggestion.get("message", "").lower():
            result["confidence"] = 0.95
        return result

    def _validate_naming(self, code: str, suggestion: Dict) -> Dict:
        """Validate naming convention suggestions."""
        result = {"is_valid": True, "confidence": 0.7}
        # Check if suggestion is about function/class naming
        message = suggestion.get("message", "").lower()
        if "snake_case" in message or "pascalcase" in message:
            result["confidence"] = 0.9
        return result

    def _validate_security(self, code: str, suggestion: Dict) -> Dict:
        """Validate security-related suggestions."""
        result = {"is_valid": True, "confidence": 0.95}
        # Security suggestions should always be validated
        if "eval" in suggestion.get("message", "").lower():
            result["score"] = 1.0
        return result

    def _validate_parameters(self, code: str, suggestion: Dict) -> Dict:
        """Validate parameter count suggestions."""
        result = {"is_valid": True, "confidence": 0.8}
        param_match = re.search(r'(\d+) parameters', suggestion.get("message", ""))
        if param_match:
            param_count = int(param_match.group(1))
            if param_count < 5:
                result["is_valid"] = False
                result["warnings"] = ["Parameter count is within acceptable range"]
        return result

    def _calculate_score(self, result: Dict) -> float:
        """Calculate overall validation score."""
        base_score = 0.5 if result["is_valid"] else 0.0
        confidence = result.get("confidence", 0.5)
        warning_penalty = len(result.get("warnings", [])) * 0.1
        return max(0.0, min(1.0, base_score + (confidence * 0.5) - warning_penalty))

    def get_feedback(self, original_issues: List[Dict], validated_suggestions: List[Dict]) -> Dict:
        """Generate feedback for the optimization process."""
        if not original_issues or not validated_suggestions:
            return {
                "improvement_rate": 0.0,
                "coverage": 0.0,
                "quality_score": 0.0
            }

        issues_covered = len(validated_suggestions)
        total_issues = len(original_issues)
        coverage = issues_covered / total_issues if total_issues > 0 else 0

        avg_quality = sum(s.get("score", 0) for s in validated_suggestions) / len(validated_suggestions)
        improvement_rate = coverage * avg_quality

        return {
            "improvement_rate": improvement_rate,
            "coverage": coverage,
            "quality_score": avg_quality,
            "total_issues": total_issues,
            "issues_resolved": issues_covered,
            "critical_count": sum(1 for s in validated_suggestions if s.get("priority") == "critical")
        }

    def iterative_refine(self, code: str, suggestions: List[Dict], iterations: int = 3) -> Tuple[List[Dict], Dict]:
        """Iteratively refine suggestions through multiple validation passes."""
        current_suggestions = suggestions
        refinement_log = []

        for i in range(iterations):
            validated = self.validate(code, current_suggestions)
            feedback = self.get_feedback(
                [s.get("original_issue", {}) for s in current_suggestions if s.get("original_issue")],
                validated
            )

            refinement_log.append({
                "iteration": i + 1,
                "suggestion_count": len(validated),
                "quality_score": feedback.get("quality_score", 0),
                "coverage": feedback.get("coverage", 0)
            })

            # Stop if quality is good enough
            if feedback.get("quality_score", 0) >= 0.9:
                break

            # Adjust confidence based on feedback
            current_suggestions = self._adjust_confidence(current_suggestions, feedback)

        final_validated = self.validate(code, current_suggestions)

        return final_validated, {
            "iterations": refinement_log,
            "final_quality": sum(s.get("score", 0) for s in final_validated) / len(final_validated) if final_validated else 0
        }

    def _adjust_confidence(self, suggestions: List[Dict], feedback: Dict) -> List[Dict]:
        """Adjust suggestion confidence based on feedback."""
        quality_score = feedback.get("quality_score", 0)
        adjusted = []

        for s in suggestions:
            s_copy = s.copy()
            if quality_score < 0.5:
                # Increase priority for low quality suggestions
                current_priority = s_copy.get("priority", "medium")
                priority_order = {"low": "medium", "medium": "high", "high": "critical"}
                s_copy["priority"] = priority_order.get(current_priority, "medium")
            adjusted.append(s_copy)

        return adjusted