import os
import json
import sys
from receipt_processor import process_receipt

# Reconfigure stdout for UTF-8 display in Windows terminal
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# =====================================================================
# DEFAULT RECEIPT FILE (Can be overridden via command-line argument)
# e.g., python run.py receipt11.jpg
# =====================================================================
DEFAULT_RECEIPT_FILE = "receipt12.jpg"


def main():
    receipt_file = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_RECEIPT_FILE
    if not os.path.exists(receipt_file):
        print(f"Error: Receipt file '{receipt_file}' not found.")
        sys.exit(1)

    print(f"\nProcessing receipt: {receipt_file}...")

    # Run complete receipt pipeline
    result = process_receipt(
        input_path=receipt_file,
        output_path="receipt_output.json",
        use_llm=True
    )

    # Save to ocr_result.json and per-image output file
    base_name = os.path.splitext(os.path.basename(receipt_file))[0]
    per_image_output = f"{base_name}_output.json"

    for output_file in ["ocr_result.json", per_image_output]:
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

    # Display final result
    print("\n" + "=" * 60)
    print("FINAL STRUCTURED RECEIPT RESULT")
    print("=" * 60)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    print("=" * 60)
    print(f"\nOutput saved to: receipt_output.json, ocr_result.json, and {per_image_output}\n")


if __name__ == "__main__":
    main()
