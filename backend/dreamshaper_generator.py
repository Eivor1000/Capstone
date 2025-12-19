"""
DreamShaper Image Generator for Storybook Illustrations
Uses local Stable Diffusion 1.5 DreamShaper model for high-quality storybook images
"""

import torch
from diffusers import StableDiffusionPipeline, DPMSolverMultistepScheduler
from PIL import Image
import os
import io
import base64


class DreamShaperGenerator:
    """
    DreamShaper Stable Diffusion model handler for storybook illustrations
    Optimized for RTX 3050 4GB VRAM
    """

    def __init__(self, model_path=None):
        """
        Initialize the DreamShaper model

        Args:
            model_path: Path to the local DreamShaper model file
        """
        if model_path is None:
            # Default: image-gen/model in parent directory
            script_dir = os.path.dirname(os.path.abspath(__file__))
            parent_dir = os.path.dirname(script_dir)  # Go up to story-generator/
            model_path = os.path.join(parent_dir, "image-gen", "model")

        self.model_path = os.path.abspath(model_path)
        self.pipe = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"DreamShaperGenerator: Using device: {self.device}")
        print(f"DreamShaperGenerator: Model path: {self.model_path}")

    def load_model(self):
        """Load the DreamShaper model with optimizations for 4GB VRAM"""
        if self.pipe is not None:
            print("DreamShaperGenerator: Model already loaded")
            return

        if not os.path.exists(self.model_path):
            raise FileNotFoundError(f"Model file not found: {self.model_path}")

        print(f"DreamShaperGenerator: Loading DreamShaper model from {self.model_path}...")

        try:
            print("DreamShaperGenerator: Configuring model loading...")
            
            # Load the model with optimizations
            # Monkey patch to fix weights_only issue in newer PyTorch
            original_load = torch.load
            def patched_load(*args, **kwargs):
                kwargs['weights_only'] = False
                return original_load(*args, **kwargs)
            torch.load = patched_load
            
            print("DreamShaperGenerator: Loading model checkpoint (this may take a few minutes)...")
            
            # Try to detect if model is safetensors
            import safetensors
            try:
                # Check first few bytes to determine format
                with open(self.model_path, 'rb') as f:
                    header = f.read(8)
                    is_safetensors = header[:2] == b'\xce\x00' or header[:2] == b'\x00\xce'
            except:
                is_safetensors = False
            
            print(f"DreamShaperGenerator: Detected format - {'safetensors' if is_safetensors else 'pickle/ckpt'}")
            
            self.pipe = StableDiffusionPipeline.from_single_file(
                self.model_path,
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                load_safety_checker=False,
                local_files_only=True,
                use_safetensors=is_safetensors
            )
            
            # Restore original load
            torch.load = original_load
            
            print("DreamShaperGenerator: Model checkpoint loaded, configuring pipeline...")

            # Set scheduler for better quality with fewer steps
            self.pipe.scheduler = DPMSolverMultistepScheduler.from_config(
                self.pipe.scheduler.config,
                use_karras_sigmas=True
            )

            # Move to device
            if self.device == "cuda":
                print("DreamShaperGenerator: Moving model to GPU...")
                self.pipe = self.pipe.to(self.device)
                
                # Enable memory optimizations for 4GB VRAM
                print("DreamShaperGenerator: Enabling memory optimizations...")
                self.pipe.enable_attention_slicing("max")
                self.pipe.enable_vae_tiling()
                
                # Optional: Enable model CPU offload if needed
                # self.pipe.enable_model_cpu_offload()
                
                print("DreamShaperGenerator: Memory optimizations enabled")
            else:
                self.pipe = self.pipe.to("cpu")

            print(f"DreamShaperGenerator: Model loaded successfully on {self.device}")

        except Exception as e:
            print(f"DreamShaperGenerator: Error loading model: {str(e)}")
            import traceback
            traceback.print_exc()
            raise RuntimeError(f"Failed to load DreamShaper model: {str(e)}")

    def generate_image(
        self,
        prompt,
        negative_prompt=None,
        num_inference_steps=20,
        guidance_scale=7.0,
        seed=None,
        width=512,
        height=512
    ):
        """
        Generate a storybook illustration

        Args:
            prompt: Text description of the image to generate
            negative_prompt: What to avoid in the image
            num_inference_steps: Number of denoising steps (20-25 recommended for speed)
            guidance_scale: How closely to follow the prompt (7-7.5 recommended)
            seed: Random seed for reproducibility
            width: Image width (512 recommended for 4GB VRAM)
            height: Image height (512 recommended for 4GB VRAM)

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

        print(f"DreamShaperGenerator: Generating image...")
        print(f"  - Resolution: {width}x{height}")
        print(f"  - Steps: {num_inference_steps}")
        print(f"  - Guidance: {guidance_scale}")

        try:
            # Set seed for reproducibility
            generator = None
            if seed is not None:
                generator = torch.Generator(device=self.device).manual_seed(seed)

            # Generate image
            with torch.no_grad():
                result = self.pipe(
                    prompt=enhanced_prompt,
                    negative_prompt=negative_prompt,
                    num_inference_steps=num_inference_steps,
                    guidance_scale=guidance_scale,
                    width=width,
                    height=height,
                    generator=generator
                )

            image = result.images[0]
            
            # Clear CUDA cache after generation
            if self.device == "cuda":
                torch.cuda.empty_cache()

            print(f"DreamShaperGenerator: Image generated successfully")
            return image

        except Exception as e:
            print(f"DreamShaperGenerator: Error during generation: {str(e)}")
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
            print("DreamShaperGenerator: Model unloaded from memory")


# Global instance (lazy loading)
_generator_instance = None


def get_generator():
    """Get or create the global DreamShaperGenerator instance"""
    global _generator_instance
    if _generator_instance is None:
        _generator_instance = DreamShaperGenerator()
    return _generator_instance
