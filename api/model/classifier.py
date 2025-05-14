import tensorflow as tf
import numpy as np
from PIL import Image
import io
from typing import List, Tuple, Dict, Any

class MobileNetClassifier:
    def __init__(self):
        # Load pre-trained MobileNet model
        self.model = tf.keras.applications.MobileNetV2(weights='imagenet')
        
        # Load ImageNet class names
        self.class_indices = tf.keras.applications.mobilenet_v2.decode_predictions
        
        # Set image preprocessing parameters
        self.img_size = (224, 224)  # MobileNet expected input size
        self.preprocess_input = tf.keras.applications.mobilenet_v2.preprocess_input
    
    def preprocess_image(self, image_bytes: bytes) -> np.ndarray:
        """
        Preprocess the image bytes to prepare for MobileNet prediction
        """
        # Open image from bytes
        img = Image.open(io.BytesIO(image_bytes))
        
        # Resize image to required input size
        img = img.resize(self.img_size)
        
        # Convert to numpy array and add batch dimension
        img_array = tf.keras.preprocessing.image.img_to_array(img)
        img_array = np.expand_dims(img_array, axis=0)
        
        # Apply MobileNet-specific preprocessing
        preprocessed_img = self.preprocess_input(img_array)
        
        return preprocessed_img
    
    def predict(self, image_bytes: bytes, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Make prediction on the input image and return top k classes
        
        Args:
            image_bytes: Raw image bytes
            top_k: Number of top predictions to return
            
        Returns:
            List of dictionaries with class_name, class_description and score
        """
        # Preprocess image
        preprocessed_img = self.preprocess_image(image_bytes)
        
        # Make prediction
        predictions = self.model.predict(preprocessed_img)
        
        # Decode predictions to get human-readable labels
        decoded_predictions = self.class_indices(predictions, top=top_k)[0]
        
        # Format results
        results = [
            {
                "class_id": class_id,
                "class_name": class_name,
                "confidence": float(score)
            }
            for _, class_name, score in decoded_predictions
        ]
        
        return results