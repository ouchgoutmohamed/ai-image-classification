# Load testing script for the image classifier application running in Minikube on WSL

# This script requires hey load testing tool. 
# Install it first: go get -u github.com/rakyll/hey

# Get the URL of the service from Minikube in WSL
Write-Host "Getting service URL from Minikube in WSL..." -ForegroundColor Yellow
$url = wsl -- minikube service image-classifier-service --url

# Check if a test image is available, if not create a sample one
if (-not (Test-Path "test_image.jpg")) {
    Write-Host "Creating a sample test image..." -ForegroundColor Yellow
    Invoke-WebRequest -Uri "https://picsum.photos/200" -OutFile "test_image.jpg"
}

Write-Host "Starting load test..." -ForegroundColor Yellow
Write-Host "This will send multiple requests to test the autoscaling feature." -ForegroundColor Yellow

# Run load test using hey
# Adjust these parameters based on your system capabilities:
# -n: number of requests
# -c: number of concurrent requests
# -m: HTTP method
hey -n 1000 -c 100 -m POST -T "multipart/form-data" -F "file=@./test_image.jpg" "$url/predict/"

Write-Host "Load test completed." -ForegroundColor Green
Write-Host "Checking HPA status to see if it scaled:" -ForegroundColor Yellow
wsl -- kubectl get hpa image-classifier-hpa

Write-Host "`nTo monitor pods during/after the test:" -ForegroundColor Yellow
Write-Host "wsl -- kubectl get pods" -ForegroundColor Cyan
Write-Host "wsl -- kubectl describe hpa image-classifier-hpa" -ForegroundColor Cyan
