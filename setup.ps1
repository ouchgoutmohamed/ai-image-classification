

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
