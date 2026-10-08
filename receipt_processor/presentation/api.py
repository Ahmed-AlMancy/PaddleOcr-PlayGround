from typing import Dict, Any, Optional
from ..use_cases.process_receipt import ProcessReceiptUseCase
from ..infrastructure.ollama_llm_client import OllamaLlmClient


def process_receipt(
    input_path: str,
    output_path: Optional[str] = "receipt_output.json",
    use_llm: bool = True,
    ocr_lang: str = "ar",
    ollama_path: Optional[str] = None,
    ollama_model: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Presentation API function delegating to ProcessReceiptUseCase (Clean Architecture).
    """
    llm_client = OllamaLlmClient(ollama_path=ollama_path) if ollama_path else None
    use_case = ProcessReceiptUseCase(llm_client=llm_client)

    return use_case.execute(
        input_path=input_path,
        output_path=output_path,
        use_llm=use_llm,
        ocr_lang=ocr_lang,
        ollama_model=ollama_model,
    )
