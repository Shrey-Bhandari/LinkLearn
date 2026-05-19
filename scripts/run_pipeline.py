import argparse
import json
import os
import sys

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT_DIR)

from src.core.pipeline import Link2LearnPipeline


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Link2Learn: convert educational URLs into structured exam-ready learning artifacts"
    )
    parser.add_argument(
        "urls",
        nargs="+",
        help="One or more educational URLs to process",
    )
    parser.add_argument(
        "--use-groq",
        action="store_true",
        help="Enable Groq API for note, flashcard, and MCQ generation if configured",
    )
    parser.add_argument(
        "--output",
        help="Optional JSON output file path",
        default=None,
    )
    args = parser.parse_args()

    pipeline = Link2LearnPipeline(use_groq=args.use_groq)
    result = pipeline.process_urls(args.urls)
    serialized = result.model_dump()

    if args.output:
        with open(args.output, "w", encoding="utf-8") as handle:
            json.dump(serialized, handle, indent=2)
        print(f"Saved Link2Learn output to {args.output}")
    else:
        print(json.dumps(serialized, indent=2))


if __name__ == "__main__":
    main()
