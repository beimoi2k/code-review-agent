"""Agent core logic - orchestrates the multi-agent workflow with LLM integration."""

from analyzer import Analyzer
from optimizer import Optimizer
from validator import Validator
from typing import Dict, List, Optional
import json


class CodeReviewAgent:
    """Main agent that coordinates the code review pipeline."""

    def __init__(self, use_llm: bool = False, api_key: str = None):
        self.analyzer = Analyzer()
        self.optimizer = Optimizer()
        self.validator = Validator()
        self.use_llm = use_llm
        self.api_key = api_key
        self.session_stats = {
            "total_runs": 0,
            "issues_found": 0,
            "suggestions_generated": 0,
            "suggestions_validated": 0
        }

    def run(self, code: str = None, filepath: str = None) -> Dict:
        """Run the full code review pipeline and return detailed results."""
        self.session_stats["total_runs"] += 1

        if code is None:
            code = self._get_default_code()

        # Stage 1: Analyze
        analysis_result = self.analyzer.analyze(code, filepath)
        self.session_stats["issues_found"] += len(analysis_result.get("issues", []))

        # Stage 2: Optimize
        suggestions = self.optimizer.optimize(code, analysis_result)
        self.session_stats["suggestions_generated"] += len(suggestions)

        # Stage 3: Validate
        validated = self.validator.validate(code, suggestions)
        self.session_stats["suggestions_validated"] += len(validated)

        # Generate feedback
        feedback = self.validator.get_feedback(analysis_result.get("issues", []), validated)

        # Compile results
        results = {
            "analysis": analysis_result,
            "suggestions": suggestions,
            "validated": validated,
            "feedback": feedback,
            "session_stats": self.session_stats.copy()
        }

        # Print summary
        self._print_summary(analysis_result, feedback)

        return results

    def run_directory(self, path: str) -> Dict:
        """Analyze all Python files in a directory."""
        results = self.analyzer.analyze_directory(path)
        all_suggestions = []
        for result in results:
            suggestions = self.optimizer.optimize("", result)
            validated = self.validator.validate("", suggestions)
            all_suggestions.extend(validated)

        return {
            "files_analyzed": len(results),
            "total_issues": sum(len(r.get("issues", [])) for r in results),
            "total_suggestions": len(all_suggestions),
            "file_results": [
                {
                    "filepath": r.get("filepath"),
                    "issues": len(r.get("issues", [])),
                    "metrics": r.get("metrics", {})
                }
                for r in results
            ]
        }

    def run_with_llm(self, code: str, prompt: str = None) -> Dict:
        """Run the pipeline with LLM enhancement for semantic understanding."""
        if not self.use_llm:
            return self.run(code)

        # Basic analysis
        analysis_result = self.analyze(code)
        suggestions = self.optimizer.optimize(code, analysis_result)

        # Enhance with LLM for semantic understanding
        enhanced_suggestions = self._llm_enhance(code, suggestions, prompt)

        validated = self.validator.validate(code, enhanced_suggestions)
        feedback = self.validator.get_feedback(analysis_result.get("issues", []), validated)

        return {
            "analysis": analysis_result,
            "suggestions": enhanced_suggestions,
            "validated": validated,
            "feedback": feedback
        }

    def _llm_enhance(self, code: str, suggestions: List[Dict], prompt: str = None) -> List[Dict]:
        """Enhance suggestions using LLM for deeper semantic analysis."""
        # Placeholder for LLM integration
        # In production, this would call OpenAI/Anthropic API
        enhanced = []
        for s in suggestions:
            s_copy = s.copy()
            s_copy["llm_enhanced"] = False
            enhanced.append(s_copy)
        return enhanced

    def _get_default_code(self) -> str:
        return '''def MyFunction():
    try:
        x = 1
    except:
        pass
    return x'''

    def _print_summary(self, analysis_result: Dict, feedback: Dict) -> None:
        """Print a summary of the analysis results."""
        issues = analysis_result.get("issues", [])
        print("\n" + "=" * 50)
        print("CODE REVIEW SUMMARY")
        print("=" * 50)
        print(f"Issues Found: {len(issues)}")
        print(f"Coverage: {feedback.get('coverage', 0)*100:.1f}%")
        print(f"Quality Score: {feedback.get('quality_score', 0)*100:.1f}%")

        if issues:
            severity_counts = {}
            for issue in issues:
                severity = issue.get("severity", "unknown")
                severity_counts[severity] = severity_counts.get(severity, 0) + 1

            print("\nBy Severity:")
            for sev, count in severity_counts.items():
                print(f"  {sev}: {count}")

        print("=" * 50 + "\n")

    def get_stats(self) -> Dict:
        """Get session statistics."""
        return self.session_stats.copy()

    def reset_stats(self) -> None:
        """Reset session statistics."""
        self.session_stats = {
            "total_runs": 0,
            "issues_found": 0,
            "suggestions_generated": 0,
            "suggestions_validated": 0
        }