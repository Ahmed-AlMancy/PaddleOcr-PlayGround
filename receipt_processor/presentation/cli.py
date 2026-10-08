import argparse
import json
import logging
import sys
from .api import process_receipt


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(
        description="Generic Arabic & English Receipt Expense Processor"
    )
    parser.add_argument(
        "input_path",
        help="Path to receipt image file (.jpg, .png) or OCR JSON file"
    )
    parser.add_argument(
        "-o", "--output",
        default="receipt_output.json",
        help="Path to output JSON file (default: receipt_output.json)"
    )
    parser.add_argument(
        "--lang",
        default="ar",
        help="OCR language model ('ar' for Arabic/English mixed, 'en' for English)"
    )
    parser.add_argument(
        "--no-llm",
        action="store_true",
        help="Disable LLM categorization step"
    )
    parser.add_argument(
        "--ollama-path",
        help="Path to Ollama executable"
    )
    parser.add_argument(
        "--ollama-model",
        help="Ollama model name (default: qwen2.5:3b)"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable debug logging"
    )

    args = parser.parse_args()

    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    )

    try:
        result = process_receipt(
            input_path=args.input_path,
            output_path=args.output,
            use_llm=not args.no_llm,
            ocr_lang=args.lang,
            ollama_path=args.ollama_path,
            ollama_model=args.ollama_model,
        )

        print("\n" + "=" * 60)
        print("STRUCTURED RECEIPT RESULT")
        print("=" * 60)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        print("=" * 60)
        print(f"Output saved to: {args.output}\n")

    except Exception as e:
        logging.error(f"Failed to process receipt: {e}")
        if args.verbose:
            logging.exception(e)
        sys.exit(1)


if __name__ == "__main__":
    main()
