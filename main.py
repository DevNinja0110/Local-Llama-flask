import os
import glob
from fastapi import FastAPI, File, UploadFile, Depends
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ConfigDict
from fastapi.responses import StreamingResponse
from libs.utils import extract_text_from_doc, extract_text_from_docx, extract_text_from_pdf
from auth.auth import router as auth_router
from database import engine
from auth.models import Base
from fastapi.security import OAuth2PasswordBearer
from langchain_ollama import OllamaLLM
from fastapi import HTTPException
from sqlalchemy.orm import Session
from database import get_db
from auth.models import API

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/auth", tags=["auth"])

Base.metadata.create_all(bind=engine)

class Query(BaseModel):
    text: str
    model_config = ConfigDict(from_attributes=True)  # Updated for Pydantic V2

llm = OllamaLLM(model="llama3.1")

@app.post("/llama", description="Generate text based on the provided query..")
async def generate_text(query: Query, apikey: str, db: Session = Depends(get_db)):
    # Check if the provided API key exists in the database
    api_key = db.query(API).filter(API.key == apikey).first()
    if not api_key:
        raise HTTPException(status_code=401, detail="APIKey is not correct.")

    response = llm.invoke(query.text)
    return response

@app.post("/extracttext/", description="Upload a file and extract text from it. Supports PDF and DOC files..")
async def upload_file(file: UploadFile = File(...), token: str = Depends(oauth2_scheme)):
    file_location = f"uploaded_files/{file.filename}"
    with open(file_location, "wb+") as file_object:
        file_object.write(file.file.read())

    if file.content_type == "application/pdf":
        text = extract_text_from_pdf(file_location)
    elif file.content_type == "application/msword":
        text = extract_text_from_doc(file_location)
    else:
        return {"error": "Unsupported file type"}

    return {"extracted_text": text}

@app.delete("/removefiles", description="Remove all uploaded files.")
async def remove_files(token: str = Depends(oauth2_scheme)):
    files = glob.glob('uploaded_files/*')
    for f in files:
        os.remove(f)
    return JSONResponse(content={"message": "All files have been removed."})