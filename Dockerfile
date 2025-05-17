# Use TensorFlow image which already has Python and TensorFlow installed
FROM tensorflow/tensorflow:2.13.0

# Set working directory
WORKDIR /app

# Set essential environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app
ENV KERAS_HOME=/root/.keras

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy only the necessary application files
COPY api/ /app/api/

# Pre-download model weights and initialize decoder
RUN mkdir -p /root/.keras/models/ && \
    python -c "import tensorflow as tf; tf.keras.applications.MobileNetV2(weights='imagenet'); print('MobileNetV2 model weights downloaded.')" && \
    python -c "import tensorflow as tf, numpy as np; tf.keras.applications.mobilenet_v2.decode_predictions(np.zeros((1,1000))); print('MobileNetV2 decoder initialized.')"

# Expose port and run command
EXPOSE 8000
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]