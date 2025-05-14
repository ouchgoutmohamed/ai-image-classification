import uvicorn
from fastapi import FastAPI, UploadFile, File, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import os
from typing import Dict, Any, List
import io
from pydantic import BaseModel

from api.model import MobileNetClassifier

# Initialize FastAPI app
app = FastAPI(
    title="Image Classification API",
    description="A simple API for image classification using MobileNet",
    version="1.0.0"
)

# Initialize the classifier
classifier = MobileNetClassifier()

# Setup templates for the UI
templates = Jinja2Templates(directory="templates")

# Mount static files directory
os.makedirs("static", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Create templates directory if it doesn't exist
os.makedirs("templates", exist_ok=True)

# Create index.html in the templates directory
with open("templates/index.html", "w") as f:
    f.write("""
<!DOCTYPE html>
<html>
<head>
    <title>Image Classification App</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            line-height: 1.6;
        }
        .container {
            background-color: #f9f9f9;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        h1 {
            color: #333;
            text-align: center;
        }
        .upload-form {
            margin: 20px 0;
            text-align: center;
        }
        .results {
            margin-top: 20px;
        }
        .result-item {
            margin-bottom: 10px;
            padding: 10px;
            background-color: #fff;
            border-radius: 5px;
            display: flex;
            justify-content: space-between;
        }
        .preview-image {
            max-width: 300px;
            max-height: 300px;
            margin: 20px auto;
            display: block;
        }
        .progress {
            height: 5px;
            width: 100%;
            margin-top: 5px;
            background-color: #e0e0e0;
            border-radius: 5px;
            overflow: hidden;
        }
        .progress-bar {
            height: 100%;
            background-color: #4CAF50;
            border-radius: 5px;
        }
        .hidden {
            display: none;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Image Classification App</h1>
        <div class="upload-form">
            <form id="uploadForm" enctype="multipart/form-data">
                <input type="file" id="imageInput" name="file" accept="image/*">
                <button type="submit">Classify Image</button>
            </form>
        </div>
        
        <div id="loading" class="hidden">
            <p>Processing image...</p>
        </div>
        
        <div class="preview">
            <img id="previewImage" class="preview-image hidden" src="">
        </div>
        
        <div id="results" class="results hidden">
            <h3>Classification Results:</h3>
            <div id="resultItems"></div>
        </div>
    </div>

    <script>
        const form = document.getElementById('uploadForm');
        const imageInput = document.getElementById('imageInput');
        const previewImage = document.getElementById('previewImage');
        const loading = document.getElementById('loading');
        const results = document.getElementById('results');
        const resultItems = document.getElementById('resultItems');

        imageInput.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(event) {
                    previewImage.src = event.target.result;
                    previewImage.classList.remove('hidden');
                }
                reader.readAsDataURL(file);
            }
        });

        form.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const formData = new FormData();
            const imageFile = imageInput.files[0];
            
            if (!imageFile) {
                alert('Please select an image to classify');
                return;
            }
            
            formData.append('file', imageFile);
            
            loading.classList.remove('hidden');
            results.classList.add('hidden');
            
            try {
                const response = await fetch('/predict/', {
                    method: 'POST',
                    body: formData
                });
                
                if (response.ok) {
                    const data = await response.json();
                    displayResults(data);
                } else {
                    alert('Error: Failed to classify image');
                }
            } catch (error) {
                alert('Error: ' + error.message);
            } finally {
                loading.classList.add('hidden');
            }
        });

        function displayResults(data) {
            resultItems.innerHTML = '';
            
            data.forEach(item => {
                const resultItem = document.createElement('div');
                resultItem.className = 'result-item';
                
                const confidencePercent = (item.confidence * 100).toFixed(2);
                
                resultItem.innerHTML = `
                    <div class="label">${item.class_name}</div>
                    <div class="confidence">${confidencePercent}%</div>
                `;
                
                const progressContainer = document.createElement('div');
                progressContainer.className = 'progress';
                
                const progressBar = document.createElement('div');
                progressBar.className = 'progress-bar';
                progressBar.style.width = `${confidencePercent}%`;
                
                progressContainer.appendChild(progressBar);
                resultItem.appendChild(progressContainer);
                
                resultItems.appendChild(resultItem);
            });
            
            results.classList.remove('hidden');
        }
    </script>
</body>
</html>
    """)

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
    """
    # Check if the uploaded file is an image
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Only image files are allowed!")
    
    try:
        # Read image bytes
        contents = await file.read()
        
        # Make prediction
        predictions = classifier.predict(contents)
        
        return predictions
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred during prediction: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint to verify API is running"""
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)