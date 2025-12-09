"""
Model download script for Render deployment.
Downloads fine-tuned QWEN model from HuggingFace Hub.
"""

import os
import sys
from pathlib import Path
from huggingface_hub import snapshot_download
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
MODEL_DIR = Path("models/qwen-title-generator")
HUGGINGFACE_REPO = os.getenv("HUGGINGFACE_MODEL_REPO")  # e.g., "your-username/qwen-lofi-titles"
HUGGINGFACE_TOKEN = os.getenv("HUGGINGFACE_TOKEN")  # For private repos
USE_FINETUNED_MODEL = os.getenv("USE_FINETUNED_MODEL", "false").lower() == "true"


def download_model_from_hf():
    """Download model from HuggingFace Hub."""
    if not USE_FINETUNED_MODEL:
        logger.info("Fine-tuned model disabled (USE_FINETUNED_MODEL=false)")
        logger.info("App will use Claude API fallback")
        return True

    if not HUGGINGFACE_REPO:
        logger.warning("HUGGINGFACE_MODEL_REPO not set in environment")
        logger.warning("Skipping model download. App will use Claude API fallback.")
        return True

    # Check if model already exists
    if MODEL_DIR.exists() and any(MODEL_DIR.iterdir()):
        logger.info(f"Model already exists at {MODEL_DIR}")
        logger.info("Skipping download. Delete the directory to re-download.")
        return True

    # Create model directory
    MODEL_DIR.parent.mkdir(parents=True, exist_ok=True)

    try:
        logger.info(f"Downloading model from HuggingFace: {HUGGINGFACE_REPO}")
        logger.info("This may take 5-10 minutes depending on connection speed...")

        snapshot_download(
            repo_id=HUGGINGFACE_REPO,
            local_dir=str(MODEL_DIR),
            token=HUGGINGFACE_TOKEN,
            repo_type="model",
            local_dir_use_symlinks=False
        )

        logger.info(f"✓ Model downloaded successfully to {MODEL_DIR}")
        return True

    except Exception as e:
        logger.error(f"Failed to download model: {e}")
        logger.warning("App will fall back to Claude API")
        return False


def verify_model_files():
    """Verify that required model files exist."""
    if not USE_FINETUNED_MODEL:
        return True

    if not MODEL_DIR.exists():
        logger.warning(f"Model directory not found: {MODEL_DIR}")
        return False

    required_files = [
        "config.json",
        "tokenizer_config.json",
    ]

    # Check for either PEFT or full model files
    has_peft = (MODEL_DIR / "adapter_config.json").exists()
    has_full_model = any((MODEL_DIR / f"pytorch_model.bin").exists() or
                         (MODEL_DIR / f"model.safetensors").exists() for f in MODEL_DIR.iterdir())

    if not (has_peft or has_full_model):
        logger.error("Model files incomplete (missing adapter or model weights)")
        return False

    for file in required_files:
        if not (MODEL_DIR / file).exists():
            logger.warning(f"Missing file: {file}")
            return False

    logger.info("✓ Model files verified")
    return True


if __name__ == "__main__":
    logger.info("=" * 60)
    logger.info("QWEN Song Title Generator - Model Download")
    logger.info("=" * 60)

    # Download model
    success = download_model_from_hf()

    if success:
        # Verify files
        verified = verify_model_files()

        if verified:
            logger.info("\n" + "=" * 60)
            logger.info("✓ Model ready for deployment!")
            logger.info("=" * 60)
            sys.exit(0)
        else:
            logger.warning("\n" + "=" * 60)
            logger.warning("⚠ Model verification failed")
            logger.warning("App will use Claude API fallback")
            logger.warning("=" * 60)
            sys.exit(0)  # Don't fail deployment, just use fallback
    else:
        logger.warning("\n" + "=" * 60)
        logger.warning("⚠ Model download failed")
        logger.warning("App will use Claude API fallback")
        logger.warning("=" * 60)
        sys.exit(0)  # Don't fail deployment, just use fallback
