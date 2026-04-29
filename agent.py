"""Agent core logic - orchestrates the multi-agent workflow."""

from analyzer import Analyzer
from optimizer import Optimizer
from validator import Validator


class CodeReviewAgent:
    """Main agent that coordinates the code review pipeline."""

    def __init__(self):
        self.analyzer = Analyzer()
        self.optimizer = Optimizer()
        self.validator = Validator()

    def run(self, code: str = None):
        """Run the full code review pipeline."""
        if code is None:
            code = self._read_input()

        # Stage 1: Analyze
        issues = self.analyzer.analyze(code)
        print(f"[Analyzer] Found {len(issues)} issues")

        # Stage 2: Optimize
        suggestions = self.optimizer.optimize(code, issues)
        print(f"[Optimizer] Generated {len(suggestions)} suggestions")

        # Stage 3: Validate
        validated = self.validator.validate(code, suggestions)
        print(f"[Validator] {len(validated)} suggestions passed validation")

        return validated

    def _read_input(self):
        """Read code input from user or file."""
        return input("Enter code to review (or path to file): ")