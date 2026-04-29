"""Analyzer module - identifies code issues through static analysis."""

import ast
from typing import List, Dict


class Analyzer:
    """Analyzes code for potential issues, performance problems, and anti-patterns."""

    def analyze(self, code: str) -> List[Dict]:
        """Analyze code and return list of identified issues."""
        issues = []

        try:
            tree = ast.parse(code)
            issues.extend(self._check_complexity(tree))
            issues.extend(self._check_naming(tree))
            issues.extend(self._check_best_practices(tree))
        except SyntaxError as e:
            issues.append({
                "type": "syntax_error",
                "message": f"Syntax error: {e}",
                "line": e.lineno or 0
            })

        return issues

    def _check_complexity(self, tree: ast.AST) -> List[Dict]:
        """Check code complexity issues."""
        issues = []
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                complexity = self._calculate_complexity(node)
                if complexity > 10:
                    issues.append({
                        "type": "high_complexity",
                        "message": f"Function '{node.name}' has complexity {complexity}",
                        "line": node.lineno,
                        "severity": "warning"
                    })
        return issues

    def _calculate_complexity(self, node: ast.AST) -> int:
        """Calculate cyclomatic complexity of a function."""
        complexity = 1
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
        return complexity

    def _check_naming(self, tree: ast.AST) -> List[Dict]:
        """Check naming convention issues."""
        issues = []
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if node.name[0].isupper() and not node.name.startswith('_'):
                    issues.append({
                        "type": "naming_violation",
                        "message": f"Function '{node.name}' should be snake_case",
                        "line": node.lineno,
                        "severity": "info"
                    })
        return issues

    def _check_best_practices(self, tree: ast.AST) -> List[Dict]:
        """Check for common best practice violations."""
        issues = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Try):
                if len(node.handlers) == 0:
                    issues.append({
                        "type": "bare_except",
                        "message": "Bare except clause should be avoided",
                        "line": node.lineno,
                        "severity": "warning"
                    })
        return issues