# components/RFP_document.py
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import pdfplumber
import docx
from PIL import Image
import pytesseract
import subprocess
import json
import traceback
import os
import io

router = APIRouter()

# --------------------------------------------------
# Ollama Configuration
# --------------------------------------------------
OLLAMA_BIN = os.getenv(
    "OLLAMA_PATH",
    r"C:\Users\dheve\AppData\Local\Programs\Ollama\ollama.exe"
)
MODEL_NAME = "gpt-oss:120b-cloud"
TIMEOUT = 600

print("=" * 50)
print("OLLAMA_BIN:", OLLAMA_BIN)
print("Ollama exists:", os.path.exists(OLLAMA_BIN))
print("=" * 50)

# --------------------------------------------------
# Text Extraction Functions
# --------------------------------------------------
async def extract_text(file: UploadFile) -> str:
    """Extract text from uploaded file"""
    try:
        # Read file content
        content = await file.read()
        await file.seek(0)
        
        filename_lower = file.filename.lower()

        # PDF extraction
        if filename_lower.endswith(".pdf"):
            with pdfplumber.open(io.BytesIO(content)) as pdf:
                text_parts = []
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text_parts.append(page_text)
                return "\n".join(text_parts)

        # DOCX extraction
        elif filename_lower.endswith(".docx"):
            doc = docx.Document(io.BytesIO(content))
            return "\n".join(p.text for p in doc.paragraphs if p.text.strip())

        # Image extraction (OCR)
        elif filename_lower.endswith((".png", ".jpg", ".jpeg")):
            image = Image.open(io.BytesIO(content))
            return pytesseract.image_to_string(image)

        # Plain text
        else:
            return content.decode("utf-8", errors="ignore")

    except Exception as e:
        print(f"❌ Extraction error: {str(e)}")
        raise HTTPException(500, f"Text extraction failed: {str(e)}")


# --------------------------------------------------
# Ollama Integration (CORRECTED)
# --------------------------------------------------
def call_ollama(prompt_text: str) -> dict:
    """
    Call Ollama using correct command structure
    """
    try:
        # CORRECTED: Use "run" command, not "generate"
        cmd = [
            OLLAMA_BIN,
            "run",
            MODEL_NAME,
            prompt_text
        ]

        print(f"🚀 Executing Ollama command...")
        print(f"Model: {MODEL_NAME}")

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=TIMEOUT,
            encoding='utf-8',
            errors='ignore'
        )

        # Check for command errors
        if result.returncode != 0:
            error_msg = result.stderr.strip() or "Unknown error"
            print(f"❌ Ollama command failed: {error_msg}")
            raise HTTPException(500, f"Ollama error: {error_msg}")

        # Get raw output
        raw_output = result.stdout.strip()
        
        if not raw_output:
            raise HTTPException(500, "Ollama returned empty response")

        print(f"📤 Ollama response length: {len(raw_output)} chars")
        print(f"First 200 chars: {raw_output[:200]}")

        # Extract and parse JSON
        try:
            json_data = extract_json_from_response(raw_output)
            print("✅ Successfully parsed JSON")
            return json_data
            
        except json.JSONDecodeError as je:
            print(f"❌ JSON parsing failed: {str(je)}")
            print(f"Raw output: {raw_output[:500]}")
            
            # Return error with raw output for debugging
            raise HTTPException(
                500,
                f"Invalid JSON from Ollama. Error: {str(je)}. Output: {raw_output[:200]}"
            )

    except subprocess.TimeoutExpired:
        print(f"❌ Ollama timeout after {TIMEOUT}s")
        raise HTTPException(504, f"Ollama timed out after {TIMEOUT} seconds")
    
    except FileNotFoundError:
        print(f"❌ Ollama binary not found at: {OLLAMA_BIN}")
        raise HTTPException(500, f"Ollama not found at {OLLAMA_BIN}")
    
    except HTTPException:
        raise
    
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        raise HTTPException(500, f"Ollama call failed: {str(e)}")


def extract_json_from_response(text: str) -> dict:
    """
    Extract JSON from Ollama response that might contain extra text
    """
    # Remove markdown code blocks
    if "```json" in text:
        start = text.find("```json") + 7
        end = text.find("```", start)
        if end != -1:
            text = text[start:end].strip()
    elif "```" in text:
        start = text.find("```") + 3
        end = text.find("```", start)
        if end != -1:
            text = text[start:end].strip()
    
    # Find the first { and last }
    first_brace = text.find("{")
    last_brace = text.rfind("}")
    
    if first_brace != -1 and last_brace != -1:
        text = text[first_brace:last_brace + 1]
    
    # Parse JSON
    return json.loads(text)


# --------------------------------------------------
# Create Optimized Prompt
# --------------------------------------------------
def create_analysis_prompt(rfp_text: str) -> str:
    """
    Create a well-structured prompt for RFP analysis
    """
    # Limit text to avoid token limits
    max_chars = 6000
    if len(rfp_text) > max_chars:
        rfp_text = rfp_text[:max_chars] + "\n... [text truncated for analysis]"
    
    return f"""You are an expert RFP analysis system. Analyze this RFP document and extract structured information.

CRITICAL INSTRUCTIONS:
1. Return ONLY valid JSON - no markdown, no explanations, no extra text
2. Use the exact structure provided below
3. If information is missing, use null or empty arrays
4. Do not add any text before or after the JSON

RFP DOCUMENT TEXT:
{rfp_text}

Required JSON structure (return this exact format):
{{
  "rfp_summary": {{
    "title": "extracted project or RFP title",
    "client_name": "organization issuing the RFP",
    "industry": "industry sector",
    "contract_type": "contract type (e.g., Fixed Price, T&M)",
    "estimated_value_usd": null,
    "duration_months": null,
    "submission_deadline": "YYYY-MM-DD format or null"
  }},
  "requirements": {{
    "technical": ["technical requirement 1", "technical requirement 2"],
    "compliance": ["compliance requirement 1", "compliance requirement 2"]
  }}
}}

Return ONLY the JSON object:"""


# --------------------------------------------------
# Main Upload Endpoint
# --------------------------------------------------
@router.post("/api/rfp/upload")
async def fileupload(file: UploadFile = File(...)):
    """
    Upload and analyze RFP document
    Supports: PDF, DOCX, TXT, Images (PNG, JPG, JPEG)
    """
    try:
        print(f"\n{'='*60}")
        print(f"📄 Processing file: {file.filename}")
        print(f"{'='*60}")

        # Step 1: Extract text
        rfp_text = await extract_text(file)
        
        if not rfp_text or len(rfp_text.strip()) < 50:
            raise HTTPException(400, "Extracted text is too short or empty")
        
        print(f"✅ Extracted {len(rfp_text)} characters")

        # Step 2: Create prompt
        prompt = create_analysis_prompt(rfp_text)

        # Step 3: Analyze with Ollama
        print("🤖 Analyzing with Ollama...")
        result_json = call_ollama(prompt)

        print("✅ Analysis complete!")
        print(f"{'='*60}\n")

        # Return result to frontend
        return JSONResponse(content=result_json)

    except HTTPException as he:
        print(f"❌ HTTP Exception: {he.status_code} - {he.detail}")
        return JSONResponse(
            status_code=he.status_code,
            content={"error": he.detail}
        )

    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        print(traceback.format_exc())
        return JSONResponse(
            status_code=500,
            content={"error": f"Internal server error: {str(e)}"}
        )


# --------------------------------------------------
# Test Endpoint
# --------------------------------------------------
@router.get("/api/rfp/test")
def test_ollama():
    """Test Ollama connection"""
    try:
        print("\n🧪 Testing Ollama connection...")
        
        test_prompt = """Return ONLY this JSON with no extra text:
{"status": "success", "message": "Ollama is working correctly"}"""
        
        result = call_ollama(test_prompt)
        
        return {
            "ollama_status": "connected",
            "ollama_path": OLLAMA_BIN,
            "model": MODEL_NAME,
            "test_response": result
        }
        
    except Exception as e:
        return {
            "ollama_status": "error",
            "ollama_path": OLLAMA_BIN,
            "error": str(e)
        }


@router.get("/api/rfp/health")
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "RFP Analysis API",
        "ollama_configured": os.path.exists(OLLAMA_BIN)
    }