"""
Quick verification script to check GPU setup for Qwen2-VL
"""

import torch

print("=" * 60)
print("GPU VERIFICATION SCRIPT")
print("=" * 60)

# Check PyTorch version
print(f"\n1. PyTorch Version: {torch.__version__}")

# Check CUDA availability
cuda_available = torch.cuda.is_available()
print(f"2. CUDA Available: {cuda_available}")

if cuda_available:
    print(f"3. CUDA Version: {torch.version.cuda}")
    print(f"4. GPU Device: {torch.cuda.get_device_name(0)}")
    print(f"5. GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.2f} GB")
    print(f"6. Current Device: {torch.cuda.current_device()}")

    # Test GPU tensor operation
    print("\n7. Testing GPU tensor operation...")
    try:
        x = torch.rand(100, 100).cuda()
        y = torch.rand(100, 100).cuda()
        z = x @ y
        print("   ✅ GPU tensor operations working!")
    except Exception as e:
        print(f"   ❌ GPU tensor operation failed: {e}")
else:
    print("\n❌ CUDA NOT AVAILABLE - Using CPU only")
    print("\nTo fix this, install PyTorch with CUDA:")
    print("pip uninstall torch torchvision -y")
    print("pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121")

print("\n" + "=" * 60)

# Check model loading capability
print("\nTesting Qwen2-VL model handler...")
try:
    from qwen_grader import get_grader
    grader = get_grader()
    print(f"✅ Grader initialized")
    print(f"   Device: {grader.device}")
    print(f"   Model path: {grader.model_path}")
    print(f"   Model loaded: {grader.model is not None}")
except Exception as e:
    print(f"❌ Grader initialization failed: {e}")

print("=" * 60)
