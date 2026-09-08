import os
import fitz # PyMuPDF
try:
    from PIL import Image
    import pytesseract
    from pdf2image import convert_from_path
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False

from langchain_google_genai import ChatGoogleGenerativeAI
from schemas.document import (
    ClassificationResult, InvoiceData, RemittanceData, 
    BankStatementData, PolicyData
)

def extract_text_from_pdf(file_path: str) -> str:
    """Extracts text using PyMuPDF (Layer 1). Falls back to OCR (Layer 2) if empty."""
    text = ""
    try:
        doc = fitz.open(file_path)
        for page in doc:
            text += page.get_text()
            
        text = text.strip()
        
        # If text is too short, it might be a scanned image
        if len(text) < 50 and OCR_AVAILABLE:
            print("Native extraction failed or too short. Falling back to OCR...")
            images = convert_from_path(file_path)
            ocr_text = ""
            for img in images:
                ocr_text += pytesseract.image_to_string(img)
            text = ocr_text.strip()
            
    except Exception as e:
        print(f"Error during extraction: {e}")
        
    return text

def classify_document(text: str) -> str:
    api_key = os.getenv("GEMINI_API_KEY")
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=api_key)
    structured_llm = llm.with_structured_output(ClassificationResult)
    
    prompt = f"""
    Analyze the following extracted text from a financial document.
    Determine its document type.
    
    TEXT:
    {text[:2000]} # Limit text for classification to save tokens
    """
    
    try:
        result = structured_llm.invoke(prompt)
        return result.document_type
    except Exception as e:
        print(f"Classification failed: {e}")
        return "UNKNOWN"

def extract_structured_data(text: str, doc_type: str) -> dict:
    api_key = os.getenv("GEMINI_API_KEY")
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=api_key)
    
    schema_map = {
        "INVOICE": InvoiceData,
        "REMITTANCE": RemittanceData,
        "BANK_STATEMENT": BankStatementData,
        "POLICY": PolicyData
    }
    
    target_schema = schema_map.get(doc_type)
    if not target_schema:
        raise ValueError(f"No schema defined for document type: {doc_type}")
        
    structured_llm = llm.with_structured_output(target_schema)
    
    prompt = f"""
    You are an expert financial data extraction AI.
    Extract the required structured fields from the following document text.
    If a field is not found, leave it as null or empty according to the schema.
    Provide a realistic confidence score (0.0 to 1.0) for the overall extraction quality.
    
    DOCUMENT TEXT:
    {text}
    """
    
    try:
        result = structured_llm.invoke(prompt)
        return result.model_dump()
    except Exception as e:
        print(f"Structured extraction failed: {e}")
        raise
