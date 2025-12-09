"""
Quick test script to validate the setup before fine-tuning.
"""

import os
import json
from pathlib import Path

def test_training_data():
    """Verify training data file exists and is valid."""
    data_file = Path("training_data/song_titles.jsonl")

    if not data_file.exists():
        print(f"❌ Training data not found: {data_file}")
        return False

    # Load and validate
    examples = []
    with open(data_file, 'r', encoding='utf-8') as f:
        for line in f:
            examples.append(json.loads(line))

    print(f"✓ Training data found: {len(examples)} examples")

    # Show sample
    print(f"\nSample examples:")
    for i, ex in enumerate(examples[:3], 1):
        print(f"  {i}. Prompt: {ex['prompt'][:60]}...")
        print(f"     Title: \"{ex['title']}\"")

    # Validate quality
    issues = 0
    for ex in examples:
        words = len(ex['title'].split())
        if words > 5:
            issues += 1

    if issues > 0:
        print(f"\n⚠ {issues} titles have >5 words (will be filtered)")
    else:
        print(f"\n✓ All titles meet quality criteria")

    return True


def test_ml_imports():
    """Verify all ML dependencies are installed."""
    try:
        import torch
        from transformers import AutoTokenizer
        from peft import PeftModel
        from datasets import Dataset
        print("✓ All ML dependencies installed")
        print(f"  - PyTorch: {torch.__version__}")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        return False


def test_env_vars():
    """Check environment variables."""
    required = ["ANTHROPIC_API_KEY", "SUNO_API_KEY"]
    optional = ["HUGGINGFACE_TOKEN", "USE_FINETUNED_MODEL"]

    print("\nEnvironment variables:")
    for var in required:
        value = os.getenv(var)
        status = "✓" if value else "❌"
        print(f"  {status} {var}: {'Set' if value else 'NOT SET'}")

    for var in optional:
        value = os.getenv(var)
        status = "ℹ" if value else "·"
        print(f"  {status} {var}: {value if value else 'not set (optional)'}")

    return True


if __name__ == "__main__":
    print("=" * 60)
    print("QWEN Song Title Generator - Setup Test")
    print("=" * 60)

    print("\n[1/3] Testing ML Dependencies...")
    test_ml_imports()

    print("\n[2/3] Testing Training Data...")
    test_training_data()

    print("\n[3/3] Testing Environment Variables...")
    test_env_vars()

    print("\n" + "=" * 60)
    print("Setup test complete!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. If training data exists: Run 'python fine_tune_model.py'")
    print("2. If training data missing: Run 'python helper_functions/generate_training_data.py'")
    print("=" * 60)
