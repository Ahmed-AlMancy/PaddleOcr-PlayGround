import os
import sys
import glob
import time
import json
import logging
import psutil
from typing import Dict, Any, List

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("benchmark")

from receipt_processor.use_cases.process_receipt import ProcessReceiptUseCase
from receipt_processor.domain.preprocessor import ReceiptPreprocessor
from receipt_processor.use_cases.spatial_parser import SpatialLayoutParser

# Try importing PPStructureV3
PPSTRUCTUREV3_AVAILABLE = False
try:
    from paddleocr import PPStructureV3
    PPSTRUCTUREV3_AVAILABLE = True
except Exception as e:
    logger.warning("PPStructureV3 import error: %s", e)


def get_memory_mb() -> float:
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / (1024 * 1024)


def benchmark_current_pipeline(image_path: str) -> Dict[str, Any]:
    use_case = ProcessReceiptUseCase()
    
    start_time = time.time()
    mem_before = get_memory_mb()
    
    base_name = os.path.splitext(os.path.basename(image_path))[0]
    per_image_output = f"{base_name}_output.json"
    
    # Execute full pipeline with LLM categorization
    final_dict = use_case.execute(
        input_path=image_path,
        output_path=per_image_output,
        use_llm=True
    )
    
    # Also save copy to ocr_result.json and receipt_output.json
    for out_file in ["ocr_result.json", "receipt_output.json"]:
        with open(out_file, "w", encoding="utf-8") as f:
            json.dump(final_dict, f, ensure_ascii=False, indent=2)

    elapsed = time.time() - start_time
    mem_after = get_memory_mb()
    
    items = final_dict.get("items", [])
    return {
        "engine": "Current PaddleOCR (v3.7.0)",
        "image": os.path.basename(image_path),
        "processing_time_sec": round(elapsed, 3),
        "ram_usage_mb": round(mem_after - mem_before, 2),
        "merchant": final_dict.get("merchant"),
        "items_count": len(items),
        "items_sample": [{"name": it.get("name"), "price": it.get("price")} for it in items[:5]],
        "subtotal": final_dict.get("subtotal"),
        "total": final_dict.get("total"),
    }


def benchmark_ppstructurev3(image_path: str, struct_engine) -> Dict[str, Any]:
    start_time = time.time()
    mem_before = get_memory_mb()
    
    try:
        res = struct_engine.predict(image_path)
        elapsed = time.time() - start_time
        mem_after = get_memory_mb()
        
        boxes_count = 0
        tables_count = 0
        if isinstance(res, list):
            for page in res:
                if hasattr(page, 'get'):
                    boxes_count += len(page.get("dt_polys", []))
                    tables_count += len(page.get("html", []))
        
        return {
            "engine": "PP-StructureV3",
            "image": os.path.basename(image_path),
            "ocr_boxes_count": boxes_count,
            "tables_found": tables_count,
            "processing_time_sec": round(elapsed, 3),
            "ram_usage_mb": round(mem_after - mem_before, 2),
            "status": "Success",
        }
    except Exception as e:
        elapsed = time.time() - start_time
        return {
            "engine": "PP-StructureV3",
            "image": os.path.basename(image_path),
            "processing_time_sec": round(elapsed, 3),
            "status": f"Error: {str(e)}",
        }


def run_full_benchmark():
    images = sorted(glob.glob("receipt*.jpg") + glob.glob("receipt*.png"))
    print(f"\nFound {len(images)} receipt test images: {[os.path.basename(img) for img in images]}\n")
    
    current_results = []
    print("=" * 70)
    print("1. BENCHMARKING CURRENT PADDLEOCR PIPELINE")
    print("=" * 70)
    
    for img in images:
        print(f"Running Current Pipeline on: {img}...")
        res = benchmark_current_pipeline(img)
        current_results.append(res)
        print(f"   -> Items Extracted: {res['items_count']}, Total: {res['total']}, Time: {res['processing_time_sec']}s")
    
    ppstruct_results = []
    print("\n" + "=" * 70)
    print("2. BENCHMARKING PP-STRUCTUREV3")
    print("=" * 70)
    
    if PPSTRUCTUREV3_AVAILABLE:
        try:
            print("Initializing PPStructureV3 engine...")
            struct_engine = PPStructureV3()
            for img in images:
                print(f"Running PP-StructureV3 on: {img}...")
                res = benchmark_ppstructurev3(img, struct_engine)
                ppstruct_results.append(res)
                print(f"   -> Result Status: {res.get('status', 'OK')}, Time: {res.get('processing_time_sec', 0)}s")
        except Exception as e:
            print(f"Failed to initialize PPStructureV3: {e}")
    else:
        print("PPStructureV3 is not installed or unavailable.")

    # Save benchmark summary report
    benchmark_report = {
        "summary": {
            "images_count": len(images),
            "current_pipeline_avg_time_sec": round(sum(r["processing_time_sec"] for r in current_results) / max(len(current_results), 1), 3),
            "ppstructurev3_available": PPSTRUCTUREV3_AVAILABLE and len(ppstruct_results) > 0,
        },
        "current_pipeline_results": current_results,
        "ppstructurev3_results": ppstruct_results,
    }
    
    with open("benchmark_report.json", "w", encoding="utf-8") as f:
        json.dump(benchmark_report, f, ensure_ascii=False, indent=2)
        
    print("\n" + "=" * 70)
    print("BENCHMARK COMPLETED. Report saved to benchmark_report.json")
    print("=" * 70)


if __name__ == "__main__":
    run_full_benchmark()
