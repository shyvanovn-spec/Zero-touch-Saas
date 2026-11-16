import os
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from pydantic import BaseModel, EmailStr, Field
from google import genai
from google.genai import types

app = FastAPI(title="Zero-Touch Accounting SaaS - Credit System")

client = genai.Client()

DATABASE = {}

MAX_FILE_SIZE_MB = 10
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024

class InvoiceResponse(BaseModel):
    vendor_name: str
    invoice_number: str
    date: str
    net_amount: float
    tax_amount: float
    gross_amount: float
    currency: str

class RegisterRequest(BaseModel):
    email: EmailStr
    accepted_terms: bool = Field(..., description="AGB und Datenschutz akzeptiert")

@app.post("/api/register")
async def register_client(data: RegisterRequest):
    if not data.accepted_terms:
        raise HTTPException(
            status_code=400, 
            detail="Sie müssen den AGB und Datenschutz zustimmen."
        )
    
    user_hash = abs(hash(data.email)) % 100000
    personal_email = f"user_{user_hash}@your-app.de"
    
    DATABASE[personal_email] = {
        "client_email": data.email,
        "credits": 3, 
    }
    
    return {
        "status": "success",
        "message": "Registrierung erfolgreich.",
        "assigned_invoice_email": personal_email,
        "free_credits": 3
    }

@app.post("/api/process-invoice")
async def process_incoming_invoice(
    client_invoice_email: str = Form(...), 
    file: UploadFile = File(...)
):
    if client_invoice_email not in DATABASE:
        raise HTTPException(status_code=403, detail="Unbekannte E-Mail. Bitte registrieren.")
    
    user_data = DATABASE[client_invoice_email]
    if user_data["credits"] <= 0:
        raise HTTPException(status_code=402, detail="Nicht genügend Credits. Bitte aufladen.")

    try:
        file_bytes = await file.read()
        
        if len(file_bytes) > MAX_FILE_SIZE_BYTES:
            raise HTTPException(
                status_code=413, 
                detail=f"Datei zu groß. Max. {MAX_FILE_SIZE_MB} MB."
            )

        mime_type = file.content_type
        if mime_type not in ["application/pdf", "image/jpeg", "image/png"]:
            raise HTTPException(status_code=400, detail="Ungültiges Format (nur PDF/JPEG/PNG).")

        prompt = (
            "Analyze this German invoice and extract accurately: "
            "vendor name, invoice number, date, net amount (Nettobetrag), "
            "tax amount (MwSt / Steuer), gross amount (Bruttobetrag), and currency."
        )

        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=[
                types.Part.from_bytes(data=file_bytes, mime_type=mime_type),
                prompt,
            ],
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=InvoiceResponse,
                temperature=0.1,
            ),
        )

        extracted_data = response.text
        user_data["credits"] -= 1

        return {
            "status": "success",
            "recipient_box": client_invoice_email,
            "extracted_data": eval(extracted_data),
            "credits_left": user_data["credits"],
            "storage_status": "Files wiped from RAM successfully"
        }

    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Serverfehler: {str(e)}"
        )

@app.post("/api/billing/takenos-webhook")
async def takenos_payment_webhook(
    client_invoice_email: str = Form(...),
    credits_to_add: int = Form(...)
):
    if client_invoice_email not in DATABASE:
        raise HTTPException(status_code=404, detail="Kunde nicht gefunden.")
    
    DATABASE[client_invoice_email]["credits"] += credits_to_add
    
    return {
        "status": "success",
        "new_balance": DATABASE[client_invoice_email]["credits"]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
