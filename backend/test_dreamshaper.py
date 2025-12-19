"""
Test script to verify DreamShaper model loads correctly
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dreamshaper_generator import get_generator

def test_model_loading():
    """Test if DreamShaper model loads successfully"""
    print("="*60)
    print("Testing DreamShaper Model Loading")
    print("="*60)
    
    try:
        # Get generator instance
        print("\n1. Getting generator instance...")
        generator = get_generator()
        print("✓ Generator instance created")
        
        # Load model
        print("\n2. Loading DreamShaper model...")
        generator.load_model()
        print("✓ Model loaded successfully")
        
        print("\n3. Model information:")
        print(f"   - Device: {generator.device}")
        print(f"   - Model path: {generator.model_path}")
        print(f"   - Pipeline loaded: {generator.pipe is not None}")
        
        print("\n" + "="*60)
        print("SUCCESS: DreamShaper model is ready to use!")
        print("="*60)
        
        return True
        
    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        print("\n" + "="*60)
        print("FAILED: Could not load DreamShaper model")
        print("="*60)
        return False

if __name__ == "__main__":
    success = test_model_loading()
    sys.exit(0 if success else 1)
