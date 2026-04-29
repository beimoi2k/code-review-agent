"""Code Review Agent - CLI entry point for the multi-agent code analysis system."""

import argparse
import sys
import os
from agent import CodeReviewAgent


def main():
    parser = argparse.ArgumentParser(
        description="Code Review Agent - Multi-agent code analysis and optimization"
    )
    parser.add_argument(
        "path",
        nargs="?",
        default=None,
        help="File path or directory to analyze"
    )
    parser.add_argument(
        "--code", "-c",
        type=str,
        help="Code string to analyze (use instead of path)"
    )
    parser.add_argument(
        "--llm",
        action="store_true",
        help="Enable LLM enhancement for semantic understanding"
    )
    parser.add_argument(
        "--api-key",
        type=str,
        help="API key for LLM provider"
    )
    parser.add_argument(
        "--output", "-o",
        type=str,
        help="Output results to JSON file"
    )
    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="Suppress summary output"
    )

    args = parser.parse_args()

    # Initialize agent
    agent = CodeReviewAgent(use_llm=args.llm, api_key=args.api_key)

    # Determine input source
    code = None
    if args.code:
        code = args.code
    elif args.path:
        if os.path.isfile(args.path):
            with open(args.path, 'r', encoding='utf-8') as f:
                code = f.read()
        elif os.path.isdir(args.path):
            result = agent.run_directory(args.path)
            print_directory_result(result, args.quiet)
            if args.output:
                save_json(args.output, result)
            return

    # Run analysis
    if code:
        result = agent.run(code=code)
        if not args.quiet:
            print_result(result)
        if args.output:
            save_json(args.output, result)
    else:
        # Interactive mode for vibe coding
        print("Code Review Agent (Interactive Mode)")
        print("=" * 40)
        print("Enter code to review (Ctrl+D to finish):")
        print("-" * 40)
        try:
            code = sys.stdin.read()
            if code.strip():
                result = agent.run(code=code)
                if not args.quiet:
                    print_result(result)
                if args.output:
                    save_json(args.output, result)
        except EOFError:
            pass


def print_result(result: dict):
    """Print analysis result."""
    feedback = result.get("feedback", {})
    issues = result.get("analysis", {}).get("issues", [])

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

    validated = result.get("validated", [])
    print(f"\nValidated Suggestions: {len(validated)}")

    print("=" * 50)

    # Print suggestions with examples
    if validated:
        print("\n--- OPTIMIZATION SUGGESTIONS ---\n")
        for i, v in enumerate(validated, 1):
            print(f"{i}. [{v.get('priority', 'unknown').upper()}] {v.get('message', '')}")
            if v.get('example'):
                print("\n   Code Example:")
                for line in v['example'].strip().split('\n'):
                    print(f"   {line}")
            if v.get('rationale'):
                print(f"\n   Rationale: {v.get('rationale')}")
            print()


def print_directory_result(result: dict, quiet: bool):
    """Print directory analysis result."""
    if not quiet:
        print(f"\n{'='*50}")
        print("DIRECTORY ANALYSIS")
        print(f"{'='*50}")
        print(f"Files Analyzed: {result.get('files_analyzed', 0)}")
        print(f"Total Issues: {result.get('total_issues', 0)}")
        print(f"Total Suggestions: {result.get('total_suggestions', 0)}")

        for file_res in result.get("file_results", []):
            print(f"\n  {file_res.get('filepath')}")
            print(f"    Issues: {file_res.get('issues')}")
            metrics = file_res.get("metrics", {})
            if metrics:
                print(f"    Lines: {metrics.get('total_lines', 0)}")
                print(f"    Functions: {metrics.get('functions', 0)}")
                print(f"    Classes: {metrics.get('classes', 0)}")

        print(f"{'='*50}\n")


def save_json(path: str, data: dict):
    """Save result to JSON file."""
    import json
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"\nResults saved to: {path}")


if __name__ == "__main__":
    main()