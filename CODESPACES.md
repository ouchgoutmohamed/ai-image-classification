# GitHub Codespaces Support

This project is configured to work with GitHub Codespaces for easy development and testing.

## Running in Codespaces

1. Open the repository in GitHub Codespaces:
   - Go to your GitHub repository
   - Click the "Code" button (green button)
   - Select the "Codespaces" tab
   - Click "Create codespace on main"

2. Once the Codespace is ready, open a terminal and run:
   ```bash
   chmod +x codespace.sh
   ./codespace.sh
   ```

3. GitHub Codespaces will automatically forward port 8000. When it does:
   - Look for the "Ports" tab in the bottom panel
   - Find port 8000 in the list
   - Click the globe icon to open the application in your browser

4. You can now use the web interface to upload images for classification, or use the API endpoint at `/predict/`.

## API Usage

- GET `/` - Web UI for image classification
- POST `/predict/` - API endpoint for image classification
  - Accepts image files (JPEG, PNG, BMP, GIF)
  - Returns classification results with confidence scores
- GET `/health` - Health check endpoint
