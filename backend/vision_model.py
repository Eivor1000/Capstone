"""
Local Qwen2-VL Vision Model for Kids Challenge Image Analysis
Loads the model once and keeps it in memory for fast inference
"""

import torch
from transformers import Qwen2VLForConditionalGeneration, AutoProcessor
from qwen_vl_utils import process_vision_info
from PIL import Image
from io import BytesIO
import os

class LocalVisionModel:
    def __init__(self, model_path):
        """
        Initialize the local Qwen2-VL model

        Args:
            model_path: Path to the local Qwen2-VL model directory
        """
        self.model_path = model_path
        self.model = None
        self.processor = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"

        print(f"Initializing Qwen2-VL model from: {model_path}")
        print(f"Using device: {self.device}")

    def load_model(self):
        """Load the model into memory (call this once at startup)"""
        if self.model is not None:
            print("Model already loaded")
            return

        try:
            print("Loading Qwen2-VL model... (this may take 1-2 minutes)")

            # Load processor
            self.processor = AutoProcessor.from_pretrained(
                self.model_path,
                trust_remote_code=True
            )

            # Load model
            self.model = Qwen2VLForConditionalGeneration.from_pretrained(
                self.model_path,
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                device_map="auto" if self.device == "cuda" else None,
                trust_remote_code=True
            )

            if self.device == "cpu":
                self.model = self.model.to(self.device)

            print("✓ Model loaded successfully!")

        except Exception as e:
            print(f"Error loading model: {str(e)}")
            raise

    def analyze_image(self, image_bytes, prompt):
        """
        Analyze an image using the local Qwen2-VL model

        Args:
            image_bytes: Raw image bytes
            prompt: Text prompt describing what to analyze

        Returns:
            str: Model's analysis/description of the image
        """
        if self.model is None:
            raise ValueError("Model not loaded. Call load_model() first.")

        try:
            # Convert bytes to PIL Image
            image = Image.open(BytesIO(image_bytes))

            # Convert to RGB if needed
            if image.mode != 'RGB':
                image = image.convert('RGB')

            # Prepare messages in Qwen2-VL format
            messages = [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "image": image,
                        },
                        {
                            "type": "text",
                            "text": prompt
                        },
                    ],
                }
            ]

            # Process the inputs
            text = self.processor.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=True
            )

            image_inputs, video_inputs = process_vision_info(messages)

            inputs = self.processor(
                text=[text],
                images=image_inputs,
                videos=video_inputs,
                padding=True,
                return_tensors="pt",
            )

            # Move to device
            inputs = inputs.to(self.device)

            # Generate response
            with torch.no_grad():
                generated_ids = self.model.generate(
                    **inputs,
                    max_new_tokens=256,
                    do_sample=True,
                    temperature=0.7,
                )

            # Trim the generated ids
            generated_ids_trimmed = [
                out_ids[len(in_ids):]
                for in_ids, out_ids in zip(inputs.input_ids, generated_ids)
            ]

            # Decode the response
            output_text = self.processor.batch_decode(
                generated_ids_trimmed,
                skip_special_tokens=True,
                clean_up_tokenization_spaces=False
            )[0]

            return output_text

        except Exception as e:
            print(f"Error analyzing image: {str(e)}")
            raise


# Global model instance (loaded once at startup)
_vision_model_instance = None

def get_vision_model(model_path=None):
    """
    Get the global vision model instance (singleton pattern)
    Loads the model on first call

    Args:
        model_path: Path to local model (only needed on first call)

    Returns:
        LocalVisionModel instance
    """
    global _vision_model_instance

    if _vision_model_instance is None:
        if model_path is None:
            raise ValueError("model_path required for first initialization")

        _vision_model_instance = LocalVisionModel(model_path)
        _vision_model_instance.load_model()

    return _vision_model_instance
