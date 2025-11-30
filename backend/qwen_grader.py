"""
Qwen2-VL-2B-Instruct Model for Kids Creative Challenge Grading
This module handles loading and inference using the local Qwen2-VL model
"""

import torch
from transformers import Qwen2VLForConditionalGeneration, AutoProcessor
from qwen_vl_utils import process_vision_info
from PIL import Image
import io
import json
import re
import os


class QwenGrader:
    """
    Qwen2-VL-2B-Instruct model handler for grading kids' creative work
    """

    def __init__(self, model_path=None):
        """
        Initialize the Qwen2-VL model

        Args:
            model_path: Path to the local Qwen2-VL-2B-Instruct model directory
        """
        if model_path is None:
            # Default: qwenv2 folder in parent directory (story-generator/qwenv2/)
            script_dir = os.path.dirname(os.path.abspath(__file__))
            parent_dir = os.path.dirname(script_dir)  # Go up to story-generator/
            model_path = os.path.join(parent_dir, "qwenv2")

        # Convert to absolute path
        self.model_path = os.path.abspath(model_path)
        self.model = None
        self.processor = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"QwenGrader: Using device: {self.device}")
        print(f"QwenGrader: Model path: {self.model_path}")

    def load_model(self):
        """Load the model and processor into memory"""
        if self.model is not None:
            print("QwenGrader: Model already loaded")
            return

        # Check if model directory exists
        if not os.path.exists(self.model_path):
            raise FileNotFoundError(f"Model directory not found: {self.model_path}")

        print(f"QwenGrader: Loading model from {self.model_path}...")

        try:
            # Load processor (handles tokenization and image processing)
            self.processor = AutoProcessor.from_pretrained(
                self.model_path,
                trust_remote_code=True
            )

            # Load model with appropriate settings
            if self.device == "cuda":
                # For GPU: Load in bfloat16 for RTX 3050 (4GB VRAM)
                self.model = Qwen2VLForConditionalGeneration.from_pretrained(
                    self.model_path,
                    torch_dtype=torch.bfloat16,
                    device_map="auto",
                    trust_remote_code=True
                )
            else:
                # For CPU: Load in float32
                self.model = Qwen2VLForConditionalGeneration.from_pretrained(
                    self.model_path,
                    torch_dtype=torch.float32,
                    device_map="cpu",
                    trust_remote_code=True
                )

            print(f"QwenGrader: Model loaded successfully on {self.device}")

        except Exception as e:
            print(f"QwenGrader: Error loading model: {str(e)}")
            raise

    def analyze_image(self, image_bytes, assignment_title, assignment_description, assignment_criteria):
        """
        Analyze a child's creative work image

        Args:
            image_bytes: Image data as bytes
            assignment_title: Title of the assignment
            assignment_description: Description of what the assignment asks for
            assignment_criteria: Grading criteria

        Returns:
            dict: Contains vision_description, score, feedback, and improvement
        """
        if self.model is None:
            self.load_model()

        try:
            # Load image
            image = Image.open(io.BytesIO(image_bytes))
            if image.mode != 'RGB':
                image = image.convert('RGB')

            # Create the prompt for analysis and grading
            prompt = f"""You are a friendly and encouraging teacher grading creative work from a young child (ages 5-8).

Assignment: {assignment_title}
Description: {assignment_description}
Criteria: {assignment_criteria}

Please analyze this child's creative work and provide:

1. A detailed description of what you see in the image (colors, shapes, objects, creativity)
2. A score out of 10 (be generous and encouraging for young children, focus on effort and creativity)
3. Positive, encouraging feedback (2-3 sentences celebrating their effort)
4. One gentle improvement suggestion (constructive and kind)

IMPORTANT: Be VERY encouraging and positive! These are young children (5-8 years old). Focus on what they did well. Give scores between 7-10 to encourage them.

Respond in this EXACT JSON format:
{{
  "description": "Detailed description of what you see in the image",
  "score": 8.5,
  "feedback": "Wonderful work! You used so many beautiful colors and were very creative!",
  "improvement": "Next time, try adding even more details to make it extra special!"
}}"""

            # Prepare messages for the model
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
                        }
                    ]
                }
            ]

            # Apply chat template
            text = self.processor.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=True
            )

            # Process vision info
            image_inputs, video_inputs = process_vision_info(messages)

            # Prepare inputs
            inputs = self.processor(
                text=[text],
                images=image_inputs,
                videos=video_inputs,
                padding=True,
                return_tensors="pt"
            )

            # Move inputs to device
            inputs = inputs.to(self.device)

            # Generate response
            print("QwenGrader: Generating grading response...")
            with torch.no_grad():
                generated_ids = self.model.generate(
                    **inputs,
                    max_new_tokens=512,
                    temperature=0.7,
                    do_sample=True,
                    top_p=0.9
                )

            # Trim input tokens from generated output
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

            print(f"QwenGrader: Raw output: {output_text}")

            # Parse JSON response
            result = self._parse_grading_response(output_text)

            return result

        except Exception as e:
            print(f"QwenGrader: Error during analysis: {str(e)}")
            import traceback
            traceback.print_exc()
            # Return fallback response
            return {
                "description": "I can see your creative work! You put effort into this assignment.",
                "score": 7.5,
                "feedback": "Great job! You showed wonderful creativity and effort!",
                "improvement": "Keep being creative and trying your best!"
            }

    def _parse_grading_response(self, response_text):
        """
        Parse the JSON response from the model

        Args:
            response_text: Raw text output from model

        Returns:
            dict: Parsed grading data
        """
        try:
            # Remove markdown code blocks if present
            response_text = re.sub(r'```json\s*', '', response_text)
            response_text = re.sub(r'```\s*', '', response_text)
            response_text = response_text.strip()

            # Try to find JSON in the response
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                response_text = json_match.group(0)

            # Parse JSON
            result = json.loads(response_text)

            # Validate and ensure score is in range
            score = float(result.get('score', 7.5))
            score = max(0.0, min(10.0, score))  # Clamp between 0 and 10

            return {
                "description": result.get('description', 'Creative work detected'),
                "score": score,
                "feedback": result.get('feedback', 'Great effort!'),
                "improvement": result.get('improvement', 'Keep practicing!')
            }

        except (json.JSONDecodeError, ValueError) as e:
            print(f"QwenGrader: Error parsing JSON: {e}")
            print(f"QwenGrader: Response was: {response_text}")

            # Fallback: Return default positive feedback
            return {
                "description": response_text[:200] if len(response_text) > 0 else "I can see your creative work!",
                "score": 7.5,
                "feedback": "Great job! You showed wonderful creativity and effort!",
                "improvement": "Keep being creative and trying your best!"
            }

    def unload_model(self):
        """Unload model from memory to free up resources"""
        if self.model is not None:
            del self.model
            del self.processor
            self.model = None
            self.processor = None
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            print("QwenGrader: Model unloaded from memory")


# Global instance (lazy loading)
_grader_instance = None

def get_grader():
    """Get or create the global QwenGrader instance"""
    global _grader_instance
    if _grader_instance is None:
        _grader_instance = QwenGrader()
    return _grader_instance
