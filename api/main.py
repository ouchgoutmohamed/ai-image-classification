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
import logging
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("image-classifier-api")

# Log startup information
logger.info("Starting Image Classification API")
start_time = time.time()

# Ensure the correct import path
# Try both import styles to handle different execution contexts
try:
    logger.info("Attempting to import from api.model...")
    from api.model import MobileNetClassifier
    logger.info("Successfully imported from api.model")
except ImportError as e:
    logger.warning(f"Import from api.model failed: {e}")
    try:
        # This import works when run from the app directory
        logger.info("Attempting to import from model...")
        from model import MobileNetClassifier
        logger.info("Successfully imported from model")
    except ImportError as e:
        logger.error(f"All import attempts failed: {e}")
        raise

# Initialize FastAPI app
app = FastAPI(
    title="Image Classification API",
    description="A simple API for image classification using MobileNet",
    version="1.0.0"
)

# Initialize the classifier
logger.info("Initializing MobileNet classifier...")
classifier_start_time = time.time()
try:
    classifier = MobileNetClassifier()
    classifier_init_time = time.time() - classifier_start_time
    logger.info(f"MobileNet classifier initialized successfully in {classifier_init_time:.2f} seconds")
except Exception as e:
    logger.error(f"Failed to initialize MobileNet classifier: {e}")
    raise

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
    """
    Health check endpoint to verify API is running and model is loaded
    
    The endpoint checks:
    1. If the API is running
    2. If the classifier is initialized
    3. If the model is loaded and can make basic predictions
    
    Returns:
        Dict with status and model readiness information
    """
    try:
        # Check if classifier and model are initialized
        if classifier and classifier.model:
            # Create a tiny black image (1x1 pixel) for a quick model sanity check
            import numpy as np
            test_img = np.zeros((1, 224, 224, 3), dtype=np.float32)
            
            # Run a quick prediction to ensure the model works
            # This only verifies model functionality, not accuracy
            _ = classifier.model.predict(test_img, verbose=0)
            
            return {
                "status": "ok",
                "model_loaded": True,
                "message": "API is healthy and model is ready for predictions"
            }
        else:
            return {
                "status": "warning",
                "model_loaded": False,
                "message": "API is running but model is not fully initialized"
            }
    except Exception as e:
        return {
            "status": "error",
            "model_loaded": False,
            "message": f"API is running but model check failed: {str(e)}"
        }

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)