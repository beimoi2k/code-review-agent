"""Code Review Agent - Entry point for the multi-agent code analysis system."""

from agent import CodeReviewAgent


def main():
    agent = CodeReviewAgent()
    agent.run()


if __name__ == "__main__":
    main()