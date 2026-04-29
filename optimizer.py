"""Optimizer module - generates optimization suggestions with code examples."""

from typing import List, Dict


class Optimizer:
    """Generates optimization suggestions for identified code issues."""

    def __init__(self):
        self.suggestion_cache = {}

    def optimize(self, code: str, analysis_result: Dict) -> List[Dict]:
        """Generate optimization suggestions based on analysis results."""
        suggestions = []
        issues = analysis_result.get("issues", [])

        for issue in issues:
            suggestion = self._generate_suggestion(issue)
            if suggestion:
                suggestions.append(suggestion)

        return suggestions

    def _generate_suggestion(self, issue: Dict) -> Dict:
        """Generate a single optimization suggestion for an issue."""
        issue_type = issue.get("type", "")

        suggestion_map = {
            "high_complexity": {
                "message": f"Function complexity is {issue.get('message', 'high')}",
                "action": "refactor",
                "priority": "high",
                "example": self._get_complexity_example(),
                "rationale": "High cyclomatic complexity makes code hard to test and maintain"
            },
            "too_long": {
                "message": issue.get("message", "Function is too long"),
                "action": "refactor",
                "priority": "medium",
                "rationale": "Long functions are harder to understand and debug"
            },
            "naming_violation": {
                "message": issue.get("message", "Naming convention violation"),
                "action": "rename",
                "priority": "low",
                "example": self._get_naming_example(),
                "rationale": "Consistent naming improves code readability"
            },
            "bare_except": {
                "message": "Bare except clause is too broad",
                "action": "replace",
                "priority": "medium",
                "example": self._get_except_example(),
                "rationale": "Catching specific exceptions allows proper error handling"
            },
            "missing_return_type": {
                "message": "Missing return type annotation",
                "action": "add_annotation",
                "priority": "low",
                "example": self._get_type_annotation_example(),
                "rationale": "Type hints improve code documentation and IDE support"
            },
            "nested_comprehension": {
                "message": "Nested list comprehension may hurt readability",
                "action": "refactor",
                "priority": "low",
                "example": self._get_comprehension_example(),
                "rationale": "Nested comprehensions are hard to read; consider using a loop"
            },
            "inefficient_range": {
                "message": "Inefficient use of range(len())",
                "action": "refactor",
                "priority": "low",
                "example": self._get_enumerate_example(),
                "rationale": "enumerate() is more Pythonic and efficient"
            },
            "code_injection_risk": {
                "message": "Potential code injection risk",
                "action": "avoid",
                "priority": "critical",
                "example": self._get_security_example(),
                "rationale": "Dynamic code execution can lead to security vulnerabilities"
            },
            "too_many_parameters": {
                "message": issue.get("message", "Too many parameters"),
                "action": "refactor",
                "priority": "medium",
                "example": self._get_parameters_example(),
                "rationale": "Functions with many parameters are hard to call correctly"
            },
            "syntax_error": {
                "message": "Syntax error must be fixed",
                "action": "fix",
                "priority": "critical"
            }
        }

        suggestion = suggestion_map.get(issue_type, {
            "message": f"Review suggested: {issue.get('message', 'unknown issue')}",
            "action": "review",
            "priority": "medium",
            "rationale": "Manual review recommended"
        })

        suggestion["type"] = issue_type
        suggestion["original_issue"] = issue.get("message", "")

        return suggestion

    def _get_complexity_example(self) -> str:
        return '''# Before: High complexity
def process_order(order):
    if order:
        if order.is_valid():
            if order.has_items():
                for item in order.items:
                    if item.in_stock:
                        if item.price > 0:
                            # process item
                            pass

# After: Low complexity
def is_processable(order):
    return order and order.is_valid() and order.has_items()

def process_order_items(order):
    for item in order.items:
        if is_item_valid(item):
            process_item(item)'''

    def _get_naming_example(self) -> str:
        return '''# Before: camelCase function
def myFunctionName():
    pass

# After: snake_case function
def my_function_name():
    pass

# Classes should use PascalCase
class MyClassName:
    pass'''

    def _get_except_example(self) -> str:
        return '''# Before: Bare except
try:
    result = int(user_input)
except:
    pass

# After: Specific exceptions
try:
    result = int(user_input)
except ValueError:
    result = 0
except TypeError:
    result = 0'''

    def _get_type_annotation_example(self) -> str:
        return '''# Before: No type hints
def calculate_total(items):
    return sum(item.price for item in items)

# After: With type hints
def calculate_total(items: list[Item]) -> float:
    return sum(item.price for item in items)'''

    def _get_comprehension_example(self) -> str:
        return '''# Before: Nested comprehension
result = [[x*y for x in range(10)] for y in range(10)]

# After: Explicit loop
result = []
for y in range(10):
    row = []
    for x in range(10):
        row.append(x * y)
    result.append(row)'''

    def _get_enumerate_example(self) -> str:
        return '''# Before: range(len())
for i in range(len(items)):
    print(i, items[i])

# After: enumerate()
for i, item in enumerate(items):
    print(i, item)'''

    def _get_security_example(self) -> str:
        return '''# Before: Using eval
code = "2 + 3"
result = eval(code)

# After: Avoid eval, use ast.literal_eval for safe evaluation
import ast
code = "2 + 3"
result = ast.literal_eval(code)'''

    def _get_parameters_example(self) -> str:
        return '''# Before: Too many parameters
def create_user(name, age, email, phone, address, city, country, zipcode):
    pass

# After: Use a data class or dictionary
from dataclasses import dataclass

@dataclass
class UserAddress:
    phone: str
    address: str
    city: str
    country: str
    zipcode: str

@dataclass
class User:
    name: str
    age: int
    email: str
    address: UserAddress

def create_user(user: User):
    pass'''

    def batch_optimize(self, analysis_results: List[Dict]) -> Dict:
        """Optimize multiple files and aggregate suggestions."""
        all_suggestions = []
        file_summaries = {}

        for result in analysis_results:
            filepath = result.get("filepath", "unknown")
            suggestions = self.optimize("", result)
            all_suggestions.extend(suggestions)
            file_summaries[filepath] = {
                "issue_count": len(result.get("issues", [])),
                "suggestion_count": len(suggestions)
            }

        return {
            "suggestions": all_suggestions,
            "summaries": file_summaries,
            "total_issues": sum(s["issue_count"] for s in file_summaries.values()),
            "priority_breakdown": self._count_by_priority(all_suggestions)
        }

    def _count_by_priority(self, suggestions: List[Dict]) -> Dict:
        """Count suggestions by priority level."""
        counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}
        for s in suggestions:
            priority = s.get("priority", "medium")
            if priority in counts:
                counts[priority] += 1
        return counts