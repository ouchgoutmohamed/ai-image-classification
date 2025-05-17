# Use TensorFlow image which already has Python and TensorFlow installed
FROM tensorflow/tensorflow:2.13.0

# Set working directory
WORKDIR /app

# Set essential environment variables
ENV PYTHONUNBUFFERED=1

# Copy requirements and install dependencies
# No need to install system packages as they are already in the base image
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy only the necessary application files
COPY api/ /app/api/

# Expose port and run command
EXPOSE 8000
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]