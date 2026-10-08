import os
import json
import sys
from receipt_processor import process_receipt

# Reconfigure stdout for UTF-8 display in Windows terminal
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Default receipt image file
DEFAULT_RECEIPT_FILE = "data/images/receipt_07.jpg"


def main():
    input_arg = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_RECEIPT_FILE
    
    # Resolve input path (support passing receipt_07.jpg or data/images/receipt_07.jpg)
    if os.path.exists(input_arg):
        receipt_file = input_arg
    elif os.path.exists(os.path.join("data", "images", input_arg)):
        receipt_file = os.path.join("data", "images", input_arg)
    else:
        print(f"Error: Receipt file '{input_arg}' not found.")
        sys.exit(1)

    output_dir = "data/outputs"
    os.makedirs(output_dir, exist_ok=True)

    print(f"\nProcessing receipt: {receipt_file}...")

    base_name = os.path.splitext(os.path.basename(receipt_file))[0]
    per_image_output = os.path.join(output_dir, f"{base_name}_output.json")
    default_output = os.path.join(output_dir, "receipt_output.json")

    # Run complete receipt pipeline
    result = process_receipt(
        input_path=receipt_file,
        output_path=default_output,
        use_llm=True
    )

    # Save copies to ocr_result.json and per-image output file in data/outputs
    for output_file in [os.path.join(output_dir, "ocr_result.json"), per_image_output]:
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

    # Display final result
    print("\n" + "=" * 60)
    print("FINAL STRUCTURED RECEIPT RESULT")
    print("=" * 60)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    print("=" * 60)
    print(f"\nOutput saved to: {default_output}, {os.path.join(output_dir, 'ocr_result.json')}, and {per_image_output}\n")


if __name__ == "__main__":
    main()
