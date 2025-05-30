# AI Image Classification API

This application provides a REST API for image classification using the MobileNetV2 model. It's containerized with Docker and deployed on Kubernetes for scalability.

## Features

- Real-time image classification using TensorFlow's MobileNetV2 model
- REST API endpoints for programmatic access
- Web interface for easy upload and classification
- Containerized deployment with Docker
- Kubernetes orchestration with auto-scaling capabilities
- Health check endpoint for monitoring
- Input validation for image format and dimensions

## Requirements

- Python 3.8+
- Docker
- Kubernetes/Minikube
- kubectl
- PowerShell (for Windows)
- hey (optional, for load testing)

## Setup

To set up the application:

```powershell
.\setup.ps1
```

This script will:
1. Start Minikube if it's not running
2. Configure Docker to use Minikube's daemon
3. Build the Docker image
4. Deploy the application to Kubernetes using the configuration files
5. Display the URL to access the application




## API Endpoints

- **GET /** - Web UI for image classification
  - Renders the HTML interface for uploading and classifying images
  - Provides a user-friendly way to interact with the classification service

- **POST /predict/** - API endpoint for image classification 
  - Accepts image files (JPEG, PNG, BMP, GIF)
  - Returns classification results as JSON with:
    - `class_id`: The ImageNet class ID
    - `class_name`: Human-readable class name
    - `confidence`: Confidence score (0-1)
  - Validates image format and dimensions:
    - Minimum dimensions: 10x10 pixels
    - Maximum dimensions: 4000x4000 pixels
    - Supported formats: JPEG, PNG, BMP, GIF
  - Returns top 5 predictions by default

- **GET /health** - Health check endpoint
  - Used by Kubernetes for readiness and liveness probes
  - Returns `{"status": "ok"}` when the service is healthy

## Accessing the Application

After deploying the application using the setup script, you can access the web UI in the following ways:

1. **Through the NodePort service**:
   - The setup script will display the URL (e.g., http://192.168.49.2:30080)
   - Open this URL in your browser to access the web interface
   - This is the recommended method for local development

2. **Using Minikube**:
   ```powershell
   # Get the URL to access the application
   minikube service image-classifier-service --url
   ```

3. **Port forwarding (alternative method)**:
   ```powershell
   # Forward the service port to your local machine
   kubectl port-forward svc/image-classifier-service 8000:8000
   ```
   Then access the application at http://localhost:8000

## Development

To develop and extend this application:

1. **Setup Local Development Environment**:
   ```powershell
   # Clone the repository (if you haven't already)
   git clone <repository-url>
   cd Richdale_Internship_May17

   # Create a virtual environment
   python -m venv venv
   .\venv\Scripts\Activate.ps1

   # Install dependencies
   pip install -r requirements.txt
   ```

2. **Run the Application Locally**:
   ```powershell
   # Run without Docker/Kubernetes
   cd api
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

## Load Testing

The repository includes a load testing script to verify the auto-scaling capabilities:

```powershell
# Run the load test
.\load_test.ps1
```

This script will:
1. Get the service URL
2. Create a test image if one doesn't exist
3. Send 1000 requests with 100 concurrent connections
4. Display the HPA status to show scaling in action

Requirements:
- The `hey` load testing tool (https://github.com/rakyll/hey)

## Technical Details

- **Framework**: FastAPI
- **ML Model**: TensorFlow MobileNetV2 pre-trained on ImageNet
- **Container**: Python 3.9 slim-based Docker image
- **Kubernetes Resources**:
  - CPU Request: 500m (0.5 CPU)
  - Memory Request: 512Mi
  - CPU Limit: 1000m (1 CPU)
  - Memory Limit: 1Gi
