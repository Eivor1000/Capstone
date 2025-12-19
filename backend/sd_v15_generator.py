"""
Stable Diffusion v1.5 Image Generator for Storybook Illustrations
Uses local SD v1.5 model for high-quality storybook images
Optimized for 4GB VRAM
"""

import torch
from diffusers import StableDiffusionPipeline, DPMSolverMultistepScheduler
from PIL import Image
import os
import io
import base64


class SDv15Generator:
    """
    SD v1.5 model handler for high-quality storybook illustrations
    Optimized for 4GB VRAM
    """

    def __init__(self, model_path=None):
        """
        Initialize the SD v1.5 model

        Args:
            model_path: Path to the local SD v1.5 safetensors file
        """
        if model_path is None:
            # Default: image-gen/sd-v1-5 in parent directory
            script_dir = os.path.dirname(os.path.abspath(__file__))
            parent_dir = os.path.dirname(script_dir)
            model_path = os.path.join(parent_dir, "image-gen", "v1-5-pruned-emaonly.safetensors")

        self.model_path = os.path.abspath(model_path)
        self.pipe = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"SDv15Generator: Using device: {self.device}")
        print(f"SDv15Generator: Model path: {self.model_path}")

    def load_model(self):
        """Load the SD v1.5 model with optimizations for 4GB VRAM"""
        if self.pipe is not None:
            print("SDv15Generator: Model already loaded")
            return

        if not os.path.exists(self.model_path):
            raise FileNotFoundError(f"Model file not found: {self.model_path}")

        print(f"SDv15Generator: Loading SD v1.5 model from {self.model_path}...")

        try:
            # Load SD v1.5 pipeline from single safetensors file
            # Skip safety checker to avoid torch.load vulnerability and save VRAM
            self.pipe = StableDiffusionPipeline.from_single_file(
                self.model_path,
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                safety_checker=None,
                feature_extractor=None,
                requires_safety_checker=False
            )

            # Use efficient scheduler (DPM++ 2M)
            self.pipe.scheduler = DPMSolverMultistepScheduler.from_config(
                self.pipe.scheduler.config
            )

            # Move to device
            if self.device == "cuda":
                print("SDv15Generator: Moving model to GPU...")
                self.pipe = self.pipe.to(self.device)
                
                # Enable memory optimizations for 4GB VRAM
                print("SDv15Generator: Enabling memory optimizations...")
                self.pipe.enable_attention_slicing("max")
                self.pipe.enable_vae_slicing()
                
                # Optional: Enable CPU offloading if VRAM is tight
                # self.pipe.enable_model_cpu_offload()
                
                print("SDv15Generator: Memory optimizations enabled")
            else:
                self.pipe = self.pipe.to("cpu")

            print(f"SDv15Generator: Model loaded successfully on {self.device}")

        except Exception as e:
            print(f"SDv15Generator: Error loading model: {str(e)}")
            import traceback
            traceback.print_exc()
            raise RuntimeError(f"Failed to load SD v1.5 model: {str(e)}")

    def generate_image(
        self,
        prompt,
        negative_prompt=None,
        num_inference_steps=25,
        guidance_scale=7.5,
        width=512,
        height=512
    ):
        """
        Generate a storybook illustration

        Args:
            prompt: Text description of the image to generate
            negative_prompt: What to avoid in the image
            num_inference_steps: Number of denoising steps (25-50 recommended)
            guidance_scale: How closely to follow prompt (7-10 recommended)
            width: Image width (512 recommended for 4GB VRAM)
            height: Image height (512 recommended for 4GB VRAM)

        Returns:
            PIL Image object
        """
        if self.pipe is None:
            self.load_model()

        print(f"SDv15Generator: Generating {width}x{height} image...")
        print(f"Prompt: {prompt[:100]}...")

        try:
            # Generate image
            result = self.pipe(
                prompt=prompt,
                negative_prompt=negative_prompt,
                num_inference_steps=num_inference_steps,
                guidance_scale=guidance_scale,
                width=width,
                height=height,
                generator=torch.Generator(device=self.device).manual_seed(int(torch.rand(1).item() * 1000000))
            )

            image = result.images[0]
            print("SDv15Generator: Image generated successfully")
            return image

        except Exception as e:
            print(f"SDv15Generator: Error during generation: {str(e)}")
            import traceback
            traceback.print_exc()
            raise

    def generate_image_base64(
        self,
        prompt,
        negative_prompt=None,
        num_inference_steps=25,
        guidance_scale=7.5,
        width=512,
        height=512
    ):
        """
        Generate image and return as base64 string

        Args:
            Same as generate_image()

        Returns:
            Base64-encoded PNG image string
        """
        image = self.generate_image(
            prompt=prompt,
            negative_prompt=negative_prompt,
            num_inference_steps=num_inference_steps,
            guidance_scale=guidance_scale,
            width=width,
            height=height
        )

        # Convert to base64
        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
        image_bytes = buffer.getvalue()
        image_base64 = base64.b64encode(image_bytes).decode('utf-8')

        return image_base64

    def unload_model(self):
        """Unload model from memory"""
        if self.pipe is not None:
            del self.pipe
            self.pipe = None
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            print("SDv15Generator: Model unloaded")


# Global generator instance
_generator = None


def get_generator(model_path=None):
    """
    Get or create the global SD v1.5 generator instance

    Args:
        model_path: Optional path to model file

    Returns:
        SDv15Generator instance
    """
    global _generator
    if _generator is None:
        _generator = SDv15Generator(model_path=model_path)
        _generator.load_model()
    return _generator
