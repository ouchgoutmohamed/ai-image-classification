import uvicorn
from fastapi import FastAPI, UploadFile, File, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import os
from typing import Dict, Any, List
import io
from pydantic import BaseModel
import pathlib
import sys

# Ensure the correct import path
from api.model import MobileNetClassifier

# Initialize FastAPI app
app = FastAPI(
    title="Image Classification API",
    description="A simple API for image classification using MobileNet",
    version="1.0.0"
)

# Initialize the classifier
classifier = MobileNetClassifier()

# Get the directory where this file is located
CURRENT_DIR = pathlib.Path(__file__).parent.absolute()

# Setup templates for the UI
templates_dir = os.path.join(CURRENT_DIR, "templates")
templates = Jinja2Templates(directory=templates_dir)

# Mount static files directory
static_dir = os.path.join(CURRENT_DIR, "static")
app.mount("/static", StaticFiles(directory=static_dir), name="static")

class PredictionResponse(BaseModel):
    class_id: str
    class_name: str
    confidence: float

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """Serve the web UI for image upload and classification"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/predict/", response_model=List[PredictionResponse])
async def predict(file: UploadFile = File(...)):
    """
    Endpoint to predict the class of an uploaded image
    
    Args:
        file: The uploaded image file
    
    Returns:
        A list of top predictions with class names and confidence scores
        
    Raises:
        HTTPException: When the file is not an image or is invalid
    """
    # Check if the uploaded file is an image based on content type
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Only image files are allowed!")
    
    try:
        # Read image bytes
        contents = await file.read()
        
        # Make prediction (includes image validation)
        predictions = classifier.predict(contents)
        
        return predictions
        
    except ValueError as e:
        # Handle validation errors (e.g., unsupported format, corrupted image)
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # Handle other errors (e.g., model errors, server errors)
        raise HTTPException(status_code=500, detail=f"An error occurred during prediction: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint to verify API is running"""
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)