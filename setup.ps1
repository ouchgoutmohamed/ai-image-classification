# Setup script for building and deploying the image classifier app to Minikube

# Check if Minikube is installed
if (-not (Get-Command "minikube" -ErrorAction SilentlyContinue)) {
    Write-Host "Minikube is not installed. Please install it first." -ForegroundColor Red
    exit 1
}

# Check if Docker is installed
if (-not (Get-Command "docker" -ErrorAction SilentlyContinue)) {
    Write-Host "Docker is not installed. Please install it first." -ForegroundColor Red
    exit 1
}

# Check if kubectl is installed
if (-not (Get-Command "kubectl" -ErrorAction SilentlyContinue)) {
    Write-Host "kubectl is not installed. Please install it first." -ForegroundColor Red
    exit 1
}

# Start Minikube if it's not running
$minikubeStatus = minikube status
if ($minikubeStatus -contains "host: Stopped") {
    Write-Host "Starting Minikube..." -ForegroundColor Yellow
    minikube start
} else {
    Write-Host "Minikube is already running." -ForegroundColor Green
}

# Set docker to use Minikube's Docker daemon
Write-Host "Configuring Docker to use Minikube's Docker daemon..." -ForegroundColor Yellow
& minikube docker-env | Invoke-Expression

# Ensure directories exist (they should already be part of the repository)
if (-not (Test-Path "api\templates")) {
    Write-Host "Templates directory not found in repository. Creating it..." -ForegroundColor Yellow
    New-Item -ItemType Directory -Path "api\templates" | Out-Null
}

if (-not (Test-Path "api\static")) {
    Write-Host "Static files directory not found in repository. Creating it..." -ForegroundColor Yellow
    New-Item -ItemType Directory -Path "api\static" | Out-Null
}

# Build the Docker image
Write-Host "Building Docker image..." -ForegroundColor Yellow
docker build -t image-classifier:latest .

# Apply Kubernetes configuration
Write-Host "Applying Kubernetes configurations..." -ForegroundColor Yellow
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl apply -f k8s/hpa.yaml

# Wait for deployment to be ready
Write-Host "Waiting for deployment to be ready..." -ForegroundColor Yellow
kubectl rollout status deployment/image-classifier

# Get the URL to access the application
$url = minikube service image-classifier-service --url
Write-Host "Application is deployed and available at: $url" -ForegroundColor Green

# Instructions for accessing the application
Write-Host "To access the application, open the URL in your browser." -ForegroundColor Yellow
Write-Host "To monitor the deployment, run: kubectl get pods" -ForegroundColor Yellow
Write-Host "To check autoscaling, run: kubectl get hpa" -ForegroundColor Yellow
Write-Host "To simulate load, you can use a tool like Apache Benchmark or hey." -ForegroundColor Yellow
