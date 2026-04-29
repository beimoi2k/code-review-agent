"""Analyzer module - identifies code issues through static analysis and dependency graph."""

import ast
import os
from typing import List, Dict, Set, Tuple
from collections import defaultdict


class Analyzer:
    """Analyzes code for potential issues, performance problems, and anti-patterns."""

    def __init__(self):
        self.call_graph = defaultdict(set)  # function -> called functions
        self.dependency_graph = defaultdict(set)  # function -> imported/used modules
        self.issues_history = []  # track all issues for feedback

    def analyze(self, code: str, filepath: str = None) -> Dict:
        """Analyze code and return comprehensive analysis results."""
        result = {
            "issues": [],
            "call_graph": {},
            "metrics": {},
            "dependencies": []
        }

        try:
            tree = ast.parse(code)

            # Extract call graph and dependencies
            self._build_call_graph(tree)
            self._build_dependency_graph(tree)

            # Run all checks
            result["issues"].extend(self._check_complexity(tree))
            result["issues"].extend(self._check_naming(tree))
            result["issues"].extend(self._check_best_practices(tree))
            result["issues"].extend(self._check_performance(tree))
            result["issues"].extend(self._check_security(tree))
            result["issues"].extend(self._check_maintainability(tree))

            result["call_graph"] = dict(self.call_graph)
            result["dependencies"] = list(self.dependency_graph.keys())
            result["metrics"] = self._calculate_metrics(tree)

            self.issues_history.append(result["issues"])

        except SyntaxError as e:
            result["issues"].append({
                "type": "syntax_error",
                "message": f"Syntax error: {e}",
                "line": e.lineno or 0,
                "severity": "critical"
            })

        return result

    def analyze_directory(self, path: str) -> List[Dict]:
        """Analyze all Python files in a directory."""
        results = []
        for root, _, files in os.walk(path):
            for file in files:
                if file.endswith('.py'):
                    filepath = os.path.join(root, file)
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            code = f.read()
                        result = self.analyze(code, filepath)
                        result["filepath"] = filepath
                        results.append(result)
                    except Exception as e:
                        results.append({
                            "filepath": filepath,
                            "issues": [{"type": "read_error", "message": str(e)}]
                        })
        return results

    def _build_call_graph(self, tree: ast.AST) -> None:
        """Build function call relationship graph."""
        current_function = None
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                current_function = node.name
                self.call_graph[current_function] = set()
            elif isinstance(node, ast.Call) and current_function:
                if isinstance(node.func, ast.Name):
                    self.call_graph[current_function].add(node.func.id)
                elif isinstance(node.func, ast.Attribute):
                    self.call_graph[current_function].add(node.func.attr)

    def _build_dependency_graph(self, tree: ast.AST) -> None:
        """Build module dependency graph."""
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    self.dependency_graph[alias.name].add(alias.asname or alias.name)
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                for alias in node.names:
                    self.dependency_graph[module].add(alias.name)

    def _check_complexity(self, tree: ast.AST) -> List[Dict]:
        """Check code complexity issues."""
        issues = []
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                complexity = self._calculate_complexity(node)
                lines = self._get_function_length(node)

                if complexity > 10:
                    issues.append({
                        "type": "high_complexity",
                        "message": f"Function '{node.name}' has cyclomatic complexity {complexity}",
                        "line": node.lineno,
                        "severity": "warning",
                        "suggestion": "Consider breaking this function into smaller, focused functions"
                    })
                if lines > 100:
                    issues.append({
                        "type": "too_long",
                        "message": f"Function '{node.name}' is {lines} lines (recommended: <100)",
                        "line": node.lineno,
                        "severity": "info"
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

    def _get_function_length(self, node: ast.FunctionDef) -> int:
        """Get the number of lines in a function."""
        if hasattr(node, 'end_lineno') and node.end_lineno:
            return node.end_lineno - node.lineno
        return 0

    def _check_naming(self, tree: ast.AST) -> List[Dict]:
        """Check naming convention issues."""
        issues = []
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if node.name[0].isupper() and not node.name.startswith('_'):
                    issues.append({
                        "type": "naming_violation",
                        "message": f"Function '{node.name}' should use snake_case",
                        "line": node.lineno,
                        "severity": "info"
                    })
            elif isinstance(node, ast.ClassDef):
                if not node.name[0].isupper():
                    issues.append({
                        "type": "naming_violation",
                        "message": f"Class '{node.name}' should use PascalCase",
                        "line": node.lineno,
                        "severity": "info"
                    })
            elif isinstance(node, ast.Name):
                if node.id.isupper() and not node.id.startswith('_'):
                    issues.append({
                        "type": "naming_violation",
                        "message": f"Variable '{node.id}' should use snake_case",
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
                        "severity": "warning",
                        "suggestion": "Use specific exception types like 'except ValueError:' or 'except Exception:'"
                    })
            elif isinstance(node, ast.FunctionDef):
                if node.returns is None and not isinstance(node, ast.AsyncFunctionDef):
                    issues.append({
                        "type": "missing_return_type",
                        "message": f"Function '{node.name}' has no return type annotation",
                        "line": node.lineno,
                        "severity": "info"
                    })
        return issues

    def _check_performance(self, tree: ast.AST) -> List[Dict]:
        """Check for performance anti-patterns."""
        issues = []
        for node in ast.walk(tree):
            if isinstance(node, ast.ListComp):
                if len(node.generators) > 2:
                    issues.append({
                        "type": "nested_comprehension",
                        "message": "Nested list comprehension may hurt readability",
                        "line": node.lineno,
                        "severity": "info"
                    })
            elif isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name) and node.func.id == "range":
                    if node.args and isinstance(node.args[0], ast.Call):
                        issues.append({
                            "type": "inefficient_range",
                            "message": "Using range(len()) is inefficient, use enumerate() instead",
                            "line": node.lineno,
                            "severity": "info"
                        })
        return issues

    def _check_security(self, tree: ast.AST) -> List[Dict]:
        """Check for security issues."""
        issues = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                func_name = ""
                if isinstance(node.func, ast.Name):
                    func_name = node.func.id
                elif isinstance(node.func, ast.Attribute):
                    func_name = node.func.attr

                if func_name in ("eval", "exec", "compile"):
                    issues.append({
                        "type": "code_injection_risk",
                        "message": f"Use of '{func_name}' poses a code injection risk",
                        "line": node.lineno,
                        "severity": "critical",
                        "suggestion": "Avoid dynamic code execution unless absolutely necessary"
                    })
        return issues

    def _check_maintainability(self, tree: ast.AST) -> List[Dict]:
        """Check for maintainability issues."""
        issues = []
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if len(node.args.args) > 6:
                    issues.append({
                        "type": "too_many_parameters",
                        "message": f"Function '{node.name}' has {len(node.args.args)} parameters (recommended: <6)",
                        "line": node.lineno,
                        "severity": "warning"
                    })
        return issues

    def _calculate_metrics(self, tree: ast.AST) -> Dict:
        """Calculate code metrics."""
        total_lines = 0
        function_count = 0
        class_count = 0
        import_count = 0

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                function_count += 1
            elif isinstance(node, ast.ClassDef):
                class_count += 1
            elif isinstance(node, (ast.Import, ast.ImportFrom)):
                import_count += 1

        if hasattr(tree, 'end_lineno') and tree.end_lineno:
            total_lines = tree.end_lineno

        return {
            "total_lines": total_lines,
            "functions": function_count,
            "classes": class_count,
            "imports": import_count
        }

    def get_fix_success_rate(self) -> float:
        """Calculate the success rate of fixes based on history."""
        if len(self.issues_history) < 2:
            return 0.0
        first_issues = sum(len(i) for i in self.issues_history[0])
        current_issues = sum(len(i) for i in self.issues_history[-1])
        if first_issues == 0:
            return 1.0
        return max(0.0, (first_issues - current_issues) / first_issues)