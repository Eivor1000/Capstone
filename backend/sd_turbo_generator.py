"""
SD-Turbo Image Generator for Storybook Illustrations
Uses local Stable Diffusion Turbo model for fast high-quality storybook images
Optimized for 4GB VRAM
"""

import torch
from diffusers import AutoPipelineForText2Image
from PIL import Image
import os
import io
import base64


class SDTurboGenerator:
    """
    SD-Turbo model handler for storybook illustrations
    Optimized for speed and 4GB VRAM
    """

    def __init__(self, model_path=None):
        """
        Initialize the SD-Turbo model

        Args:
            model_path: Path to the local SD-Turbo model directory
        """
        if model_path is None:
            # Default: image-gen/sd-turbo in parent directory
            script_dir = os.path.dirname(os.path.abspath(__file__))
            parent_dir = os.path.dirname(script_dir)
            model_path = os.path.join(parent_dir, "image-gen", "sd-turbo")

        self.model_path = os.path.abspath(model_path)
        self.pipe = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"SDTurboGenerator: Using device: {self.device}")
        print(f"SDTurboGenerator: Model path: {self.model_path}")

    def load_model(self):
        """Load the SD-Turbo model with optimizations for 4GB VRAM"""
        if self.pipe is not None:
            print("SDTurboGenerator: Model already loaded")
            return

        if not os.path.exists(self.model_path):
            raise FileNotFoundError(f"Model directory not found: {self.model_path}")

        print(f"SDTurboGenerator: Loading SD-Turbo model from {self.model_path}...")

        try:
            # Load SD-Turbo pipeline
            self.pipe = AutoPipelineForText2Image.from_pretrained(
                self.model_path,
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                variant="fp16" if self.device == "cuda" else None
            )

            # Move to device
            if self.device == "cuda":
                print("SDTurboGenerator: Moving model to GPU...")
                self.pipe = self.pipe.to(self.device)
                
                # Enable memory optimizations for 4GB VRAM
                print("SDTurboGenerator: Enabling memory optimizations...")
                self.pipe.enable_attention_slicing("max")
                self.pipe.enable_vae_tiling()
                
                print("SDTurboGenerator: Memory optimizations enabled")
            else:
                self.pipe = self.pipe.to("cpu")

            print(f"SDTurboGenerator: Model loaded successfully on {self.device}")

        except Exception as e:
            print(f"SDTurboGenerator: Error loading model: {str(e)}")
            import traceback
            traceback.print_exc()
            raise RuntimeError(f"Failed to load SD-Turbo model: {str(e)}")

    def generate_image(
        self,
        prompt,
        negative_prompt=None,
        num_inference_steps=1,
        guidance_scale=0.0,
        width=512,
        height=512
    ):
        """
        Generate a storybook illustration

        Args:
            prompt: Text description of the image to generate
            negative_prompt: What to avoid in the image
            num_inference_steps: Number of denoising steps (1-4 for turbo)
            guidance_scale: How closely to follow prompt (0.0 for turbo)
            width: Image width (512 recommended)
            height: Image height (512 recommended)

        Returns:
            PIL Image object
        """
        if self.pipe is None:
            self.load_model()

        # Default negative prompt for storybook illustrations
        if negative_prompt is None:
            negative_prompt = (
                "ugly, blurry, low quality, distorted, deformed, "
                "watermark, text, signature, realistic photo, "
                "violent, scary, dark, nightmare"
            )

        # Add storybook style prefix to prompt
        enhanced_prompt = (
            f"storybook illustration, whimsical, soft lighting, "
            f"painterly style, fantasy children book art, colorful, "
            f"magical, {prompt}"
        )

        print(f"SDTurboGenerator: Generating image...")
        print(f"  - Resolution: {width}x{height}")
        print(f"  - Steps: {num_inference_steps}")

        try:
            # Generate image with SD-Turbo (no guidance scale needed)
            with torch.no_grad():
                result = self.pipe(
                    prompt=enhanced_prompt,
                    negative_prompt=negative_prompt,
                    num_inference_steps=num_inference_steps,
                    guidance_scale=guidance_scale,
                    width=width,
                    height=height
                )

            image = result.images[0]
            
            # Clear CUDA cache after generation
            if self.device == "cuda":
                torch.cuda.empty_cache()

            print(f"SDTurboGenerator: Image generated successfully")
            return image

        except Exception as e:
            print(f"SDTurboGenerator: Error during generation: {str(e)}")
            # Clear CUDA cache on error
            if self.device == "cuda":
                torch.cuda.empty_cache()
            raise

    def generate_image_base64(self, prompt, **kwargs):
        """
        Generate image and return as base64 string

        Args:
            prompt: Text description
            **kwargs: Additional arguments for generate_image

        Returns:
            str: Base64 encoded image
        """
        image = self.generate_image(prompt, **kwargs)
        
        # Convert to base64
        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.read()).decode('utf-8')
        
        return image_base64

    def unload_model(self):
        """Unload model from memory to free up resources"""
        if self.pipe is not None:
            del self.pipe
            self.pipe = None
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            print("SDTurboGenerator: Model unloaded from memory")


# Global instance (lazy loading)
_generator_instance = None


def get_generator():
    """Get or create the global SDTurboGenerator instance"""
    global _generator_instance
    if _generator_instance is None:
        _generator_instance = SDTurboGenerator()
    return _generator_instance
