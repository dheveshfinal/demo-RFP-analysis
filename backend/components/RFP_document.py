# components/RFP_document.py
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
import pdfplumber, docx, io, os, json, subprocess, traceback, re
from PIL import Image
import pytesseract
from database import get_db
from model import BidCompany

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
# Text Extraction
# --------------------------------------------------
async def extract_text(file: UploadFile) -> str:
    try:
        content = await file.read()
        await file.seek(0)
        fname = file.filename.lower()

        if fname.endswith(".pdf"):
            with pdfplumber.open(io.BytesIO(content)) as pdf:
                return "\n".join([p.extract_text() or "" for p in pdf.pages])
        elif fname.endswith(".docx"):
            doc = docx.Document(io.BytesIO(content))
            return "\n".join([p.text for p in doc.paragraphs if p.text.strip()])
        elif fname.endswith((".png", ".jpg", ".jpeg")):
            img = Image.open(io.BytesIO(content))
            return pytesseract.image_to_string(img)
        else:
            return content.decode("utf-8", errors="ignore")
    except Exception as e:
        print(f"❌ Extraction error: {e}")
        raise HTTPException(500, f"Text extraction failed: {str(e)}")

# --------------------------------------------------
# Ollama Integration
# --------------------------------------------------
def call_ollama(prompt_text: str) -> dict:
    try:
        cmd = [OLLAMA_BIN, "run", MODEL_NAME, prompt_text]
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=TIMEOUT,
            encoding='utf-8', errors='ignore'
        )

        if result.returncode != 0:
            print(f"❌ Ollama stderr: {result.stderr}")
            raise HTTPException(500, f"Ollama error: {result.stderr.strip()}")

        raw_output = result.stdout.strip()
        print("=" * 80)
        print("RAW OLLAMA OUTPUT:")
        print(raw_output)
        print("=" * 80)
        
        json_data = extract_json_from_response(raw_output)
        
        print("=" * 80)
        print("PARSED JSON:")
        print(json.dumps(json_data, indent=2))
        print("=" * 80)
        
        return json_data
    except subprocess.TimeoutExpired:
        raise HTTPException(504, f"Ollama timed out after {TIMEOUT}s")
    except FileNotFoundError:
        raise HTTPException(500, f"Ollama not found at {OLLAMA_BIN}")
    except Exception as e:
        print(f"❌ Ollama call exception: {e}")
        raise

def extract_json_from_response(text: str) -> dict:
    """Enhanced JSON extraction with multiple fallback strategies"""
    
    original_text = text
    
    # Strategy 1: Remove markdown code blocks
    if "```json" in text:
        match = re.search(r'```json\s*(\{.*?\})\s*```', text, re.DOTALL)
        if match:
            text = match.group(1)
            print("✓ Extracted from ```json block")
    elif "```" in text:
        match = re.search(r'```\s*(\{.*?\})\s*```', text, re.DOTALL)
        if match:
            text = match.group(1)
            print("✓ Extracted from ``` block")
    
    # Strategy 2: Extract content between first { and last }
    first = text.find("{")
    last = text.rfind("}")
    if first != -1 and last != -1 and last > first:
        text = text[first:last+1]
        print(f"✓ Extracted JSON from position {first} to {last}")
    
    # Strategy 3: Clean up common issues
    text = text.strip()
    
    # Remove trailing commas before closing braces/brackets
    text = re.sub(r',(\s*[}\]])', r'\1', text)
    
    # Try to parse
    try:
        parsed = json.loads(text)
        print("✓ Successfully parsed JSON")
        return parsed
    except json.JSONDecodeError as e:
        print(f"❌ First parse attempt failed: {e}")
        print(f"❌ Attempting to parse: {text[:200]}...")
        
        # Strategy 4: Try to fix common JSON issues
        # Remove comments
        text = re.sub(r'//.*?\n|/\*.*?\*/', '', text, flags=re.DOTALL)
        
        # Try parsing again
        try:
            parsed = json.loads(text)
            print("✓ Successfully parsed after cleanup")
            return parsed
        except json.JSONDecodeError as e2:
            # Strategy 5: Return a default structure if all else fails
            print("=" * 80)
            print("⚠️ ALL PARSING FAILED - RETURNING DEFAULT")
            print(f"Original output length: {len(original_text)}")
            print(f"Original output preview: {original_text[:500]}")
            print("=" * 80)
            
            return {
                "rfp_summary": {
                    "title": "Unable to parse",
                    "client_name": "Unknown",
                    "industry": "Unknown",
                    "contract_type": "Unknown",
                    "estimated_value_usd": None,
                    "duration_months": None,
                    "submission_deadline": None
                },
                "requirements": {
                    "technical": ["Parse error - check RFP manually"],
                    "compliance": []
                },
                "_parse_error": str(e2),
                "_original_output_preview": original_text[:500]
            }

# --------------------------------------------------
# Fetch Company Data
# --------------------------------------------------
def fetch_company_data(db: Session, company_id: int = 1):
    company = db.query(BidCompany).filter(BidCompany.bid_company == company_id).first()
    if not company:
        raise HTTPException(404, "BidCompany not found")
    
    # Map database fields correctly based on your schema
    data = {
        "org_id": company.org_id,
        "capability_level": company.capability_level,  # VARCHAR - e.g., "High"
        "project_experience": company.project_experience,  # INTEGER - e.g., 8 (years)
        "certifications": company.certifications_held,  # VARCHAR - e.g., "ISO 9001"
        "team_availability": company.team_availability,  # INTEGER - e.g., 70
        "domain_experience": company.domain_experience,  # VARCHAR - e.g., "Healthcare IT"
        "project_duration": company.project_duration,  # INTEGER - e.g., 18 (months)
        "deal_size_range": company.deal_size_range,  # VARCHAR - e.g., "2M-25M"
        "types_worked_with": company.types_worked_with  # VARCHAR - e.g., "Government"
    }
    
    print("=" * 80)
    print("COMPANY DATA:")
    print(json.dumps(data, indent=2, default=str))
    print("=" * 80)
    
    return data

# --------------------------------------------------
# Complete Bid Evaluation Scores
# --------------------------------------------------
def compute_bid_evaluation(company_data: dict, rfp_data: dict) -> dict:
    scores = {}
    
    print("=" * 80)
    print("COMPUTING BID EVALUATION")
    print(f"Company Data: {company_data}")
    print(f"RFP Industry: {rfp_data.get('rfp_summary', {}).get('industry')}")
    print(f"RFP Duration: {rfp_data.get('rfp_summary', {}).get('duration_months')}")
    print("=" * 80)

    # --- 1. Certifications Match ---
    required_certs = ["ISO 9001", "ISO 27001", "HIPAA", "SOC 2"]
    cert_input = str(company_data.get("certifications", ""))
    certs = [c.strip() for c in cert_input.split(",") if c.strip()]
    
    cert_score = 0
    matched_certs = 0
    for c in certs:
        if any(req in c for req in required_certs):
            cert_score += 30
            matched_certs += 1
    
    # Bonus for multiple certifications
    if matched_certs >= 3:
        cert_score = 95
    elif matched_certs == 2:
        cert_score = 75
    elif matched_certs == 1:
        cert_score = 60
    else:
        cert_score = 30
    
    scores["certifications_match"] = cert_score

    # --- 2. Domain Experience (VARCHAR field like "Healthcare IT") ---
    domain_exp_str = str(company_data.get("domain_experience", "")).lower()
    rfp_industry = str(rfp_data.get("rfp_summary", {}).get("industry", "")).lower()
    
    # Check if domain matches RFP industry
    if rfp_industry and rfp_industry in domain_exp_str:
        scores["domain_experience"] = 95
    elif any(word in domain_exp_str for word in ["healthcare", "finance", "government", "technology"]):
        scores["domain_experience"] = 75
    else:
        scores["domain_experience"] = 50

    # --- 3. Team Availability (INTEGER 0-100) ---
    try:
        team_avail = int(company_data.get("team_availability", 0))
    except (ValueError, TypeError):
        team_avail = 0
    scores["team_availability"] = min(max(team_avail, 0), 100)

    # --- 4. Technical Match (based on capability_level VARCHAR) ---
    capability = str(company_data.get("capability_level", "")).lower()
    if "high" in capability or "advanced" in capability or "expert" in capability:
        scores["technical_match"] = 90
    elif "medium" in capability or "intermediate" in capability:
        scores["technical_match"] = 70
    elif "low" in capability or "basic" in capability:
        scores["technical_match"] = 50
    else:
        scores["technical_match"] = 60

    # --- 5. Past Project Similarity (based on project_experience INTEGER - years) ---
    try:
        project_years = int(company_data.get("project_experience", 0))
    except (ValueError, TypeError):
        project_years = 0
    
    if project_years >= 10:
        scores["past_project_similarity"] = 90
    elif project_years >= 5:
        scores["past_project_similarity"] = 75
    elif project_years >= 3:
        scores["past_project_similarity"] = 60
    else:
        scores["past_project_similarity"] = 40

    # --- 6. Timeline Feasibility ---
    try:
        company_duration = int(company_data.get("project_duration", 0))
        rfp_dur = rfp_data.get("rfp_summary", {}).get("duration_months")
        rfp_duration = int(rfp_dur) if rfp_dur else 0
        
        if rfp_duration > 0:
            if company_duration >= rfp_duration:
                scores["timeline_feasibility"] = 90
            elif company_duration >= rfp_duration * 0.75:
                scores["timeline_feasibility"] = 70
            else:
                scores["timeline_feasibility"] = 50
        else:
            # No RFP duration specified, use company capability
            if company_duration >= 12:
                scores["timeline_feasibility"] = 80
            else:
                scores["timeline_feasibility"] = 60
    except (ValueError, TypeError):
        scores["timeline_feasibility"] = 60

    # --- 7. Deal Size Fit (VARCHAR like "2M-25M") ---
    deal_size = str(company_data.get("deal_size_range", "")).lower()
    
    try:
        rfp_val = rfp_data.get("rfp_summary", {}).get("estimated_value_usd")
        rfp_value = int(rfp_val) if rfp_val else 0
    except (ValueError, TypeError):
        rfp_value = 0
    
    # Parse deal size range
    if "m" in deal_size or "million" in deal_size:
        if "25" in deal_size or "20" in deal_size or "30" in deal_size:
            scores["deal_size_fit"] = 85
        elif "10" in deal_size or "15" in deal_size:
            scores["deal_size_fit"] = 75
        else:
            scores["deal_size_fit"] = 70
    elif "k" in deal_size or "thousand" in deal_size:
        scores["deal_size_fit"] = 60
    else:
        scores["deal_size_fit"] = 70

    # --- 8. Client Type Familiarity (VARCHAR like "Government") ---
    types_worked = str(company_data.get("types_worked_with", "")).lower()
    rfp_industry = str(rfp_data.get("rfp_summary", {}).get("industry", "")).lower()
    rfp_client = str(rfp_data.get("rfp_summary", {}).get("client_name", "")).lower()
    
    # Check if client type matches
    match_score = 50  # default
    
    if rfp_industry and rfp_industry in types_worked:
        match_score = 95
    elif any(client_type in types_worked for client_type in ["government", "healthcare", "finance", "enterprise"]):
        if any(client_type in rfp_client or client_type in rfp_industry 
               for client_type in ["government", "healthcare", "finance", "enterprise"]):
            match_score = 85
        else:
            match_score = 70
    elif types_worked:
        match_score = 60
    
    scores["client_type_familiarity"] = match_score

    print("FINAL SCORES:")
    print(json.dumps(scores, indent=2))
    print("=" * 80)
    
    return scores

# --------------------------------------------------
# Upload RFP & Analyze
# --------------------------------------------------
@router.post("/api/rfp/upload")
async def fileupload(file: UploadFile = File(...), db: Session = Depends(get_db)):
    try:
        rfp_text = await extract_text(file)
        if not rfp_text.strip(): 
            raise HTTPException(400, "Text too short")
        
        print(f"✓ Extracted {len(rfp_text)} characters from RFP")

        company_data = fetch_company_data(db)

        # Simplified, more direct prompt
        prompt = f"""Extract RFP information and return ONLY valid JSON (no text before or after).

{{
  "rfp_summary": {{
    "title": "project title from document",
    "client_name": "issuing organization",
    "industry": "industry/sector",
    "contract_type": "Fixed Price or T&M or Cost Plus",
    "estimated_value_usd": 0,
    "duration_months": 0,
    "submission_deadline": "2025-01-01"
  }},
  "requirements": {{
    "technical": ["req1", "req2"],
    "compliance": ["comp1", "comp2"]
  }}
}}

RFP:
{rfp_text[:2500]}"""

        result_json = call_ollama(prompt)
        bid_evaluation = compute_bid_evaluation(company_data, result_json)

        return JSONResponse(content={
            "rfp_extracted_json": result_json,
            "bid_evaluation": bid_evaluation
        })

    except Exception as e:
        print("=" * 80)
        print("EXCEPTION IN UPLOAD:")
        print(traceback.format_exc())
        print("=" * 80)
        raise HTTPException(500, str(e))

# --------------------------------------------------
# Test Endpoint
# --------------------------------------------------
@router.get("/api/rfp/test")
def test_ollama():
    """Test Ollama connection"""
    try:
        test_prompt = 'Return only this JSON: {"status": "success", "message": "working"}'
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
            "error": str(e),
            "traceback": traceback.format_exc()
        }

@router.get("/api/rfp/health")
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "RFP Analysis API",
        "ollama_configured": os.path.exists(OLLAMA_BIN)
    }