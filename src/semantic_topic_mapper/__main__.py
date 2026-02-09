"""
Entry point for running the pipeline from the command line.

  python -m semantic_topic_mapper path/to/document.txt
  python -m semantic_topic_mapper path/to/document.txt --output output/my_run
  python -m semantic_topic_mapper   # uses INPUT_PATH and OUTPUT_DIR from config
"""

from __future__ import annotations

import argparse
import sys


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run the Semantic Topic Mapper pipeline on a text file.",
    )
    parser.add_argument(
        "input_path",
        nargs="?",
        default=None,
        help="Path to the input .txt file. If omitted, INPUT_PATH from config is used.",
    )
    parser.add_argument(
        "-o",
        "--output",
        default=None,
        dest="output_dir",
        help="Output directory for deliverables. Default: OUTPUT_DIR from config or 'output'.",
    )
    args = parser.parse_args()

    if args.input_path is not None:
        output_dir = args.output_dir
        if output_dir is None:
            from semantic_topic_mapper.config import OUTPUT_DIR
            output_dir = str(OUTPUT_DIR)
        from semantic_topic_mapper.pipeline.main_pipeline import run_pipeline
        run_pipeline(args.input_path, output_dir)
    else:
        from semantic_topic_mapper.pipeline.main_pipeline import run_pipeline_from_config
        run_pipeline_from_config()


if __name__ == "__main__":
    main()
    sys.exit(0)
