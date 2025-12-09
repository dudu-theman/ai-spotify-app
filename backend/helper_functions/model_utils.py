"""
Model loading and inference utilities for QWEN song title generator.
Optimized for 512MB RAM deployment with 4-bit quantization.
"""

import os
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
from peft import PeftModel
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global model cache (load once, reuse)
_model = None
_tokenizer = None
_model_loaded = False


def get_model_path():
    """Get model path from environment or use default."""
    # Get absolute path to backend directory
    backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    default_path = os.path.join(backend_dir, "models", "qwen-title-generator")
    return os.getenv("MODEL_PATH", default_path)


def load_model_with_quantization():
    """
    Load fine-tuned QWEN model with 4-bit quantization.
    Memory footprint: ~200-300MB total.
    """
    global _model, _tokenizer, _model_loaded

    # Return cached model if already loaded
    if _model_loaded:
        logger.info("Using cached model")
        return _model, _tokenizer

    model_path = get_model_path()
    logger.info(f"Loading model from: {model_path}")

    try:
        # Check if CUDA is available for quantization
        use_quantization = torch.cuda.is_available()

        if use_quantization:
            # 4-bit quantization config (reduces ~1.2GB model to ~300MB)
            quant_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_quant_type="nf4",
                bnb_4bit_compute_dtype=torch.float16,
                bnb_4bit_use_double_quant=True
            )
            logger.info("Loading base model with 4-bit quantization...")
        else:
            quant_config = None
            logger.info("CUDA not available, loading model without quantization (CPU mode)...")
            logger.info("This will use ~2-3GB RAM but works on Mac/CPU")

        # Load tokenizer
        logger.info("Loading tokenizer...")
        tokenizer = AutoTokenizer.from_pretrained(
            model_path,
            trust_remote_code=True
        )
        tokenizer.pad_token = tokenizer.eos_token

        # Load base model
        logger.info("Loading base Qwen2.5-0.5B model...")
        logger.info("This may take 30-60 seconds on first load...")

        base_model = AutoModelForCausalLM.from_pretrained(
            "Qwen/Qwen2.5-0.5B",
            quantization_config=quant_config if use_quantization else None,
            device_map="auto" if use_quantization else None,
            trust_remote_code=True,
            low_cpu_mem_usage=True
        )

        # Load LoRA adapters from local path
        logger.info(f"Loading LoRA adapters from {model_path}...")
        model = PeftModel.from_pretrained(base_model, model_path)

        model.eval()  # Set to evaluation mode

        # Cache for future use
        _model = model
        _tokenizer = tokenizer
        _model_loaded = True

        logger.info("Model loaded successfully!")
        logger.info(f"Model device: {model.device}")
        logger.info(f"Memory footprint: ~250-350MB")

        return model, tokenizer

    except Exception as e:
        logger.error(f"Error loading model: {e}")
        raise


def generate_title(prompt, temperature=0.9, max_new_tokens=20):
    """
    Generate a song title from a prompt.

    Args:
        prompt: The song description (e.g., "Generate a lo-fi beat that has a happy mood")
        temperature: Sampling temperature (higher = more creative, lower = more conservative)
        max_new_tokens: Maximum tokens to generate

    Returns:
        Generated song title (string)
    """
    try:
        # Load model (will use cache if already loaded)
        model, tokenizer = load_model_with_quantization()

        # Format input
        formatted_input = f"Create a song title for: {prompt}\nTitle:"

        # Tokenize
        inputs = tokenizer(
            formatted_input,
            return_tensors="pt",
            truncation=True,
            max_length=256
        ).to(model.device)

        # Generate
        logger.info(f"Generating title for: {prompt[:60]}...")

        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                temperature=temperature,
                do_sample=True,
                top_p=0.95,
                top_k=50,
                pad_token_id=tokenizer.eos_token_id,
                eos_token_id=tokenizer.eos_token_id
            )

        # Decode and extract title
        generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)

        # Extract just the title part (after "Title:")
        if "Title:" in generated_text:
            title = generated_text.split("Title:")[-1].strip()
        else:
            title = generated_text.strip()

        # Clean up: take only first line, remove quotes, limit length
        title = title.split("\n")[0].strip()
        title = title.strip('"').strip("'")

        # Truncate to max 5 words if needed
        words = title.split()
        if len(words) > 5:
            title = " ".join(words[:5])

        logger.info(f"Generated title: \"{title}\"")
        return title

    except Exception as e:
        logger.error(f"Error generating title: {e}")
        # Return a generic fallback
        return "Lofi Vibes"


def generate_title_with_fallback(prompt, fallback_func=None):
    """
    Generate title with fallback to Claude if model fails.

    Args:
        prompt: Song description
        fallback_func: Function to call if model generation fails (e.g., Claude API)

    Returns:
        Generated title
    """
    use_finetuned = os.getenv("USE_FINETUNED_MODEL", "false").lower() == "true"

    if use_finetuned:
        try:
            return generate_title(prompt)
        except Exception as e:
            logger.warning(f"Fine-tuned model failed: {e}")
            if fallback_func:
                logger.info("Falling back to Claude API...")
                return fallback_func(prompt)
            else:
                logger.warning("No fallback available, using generic title")
                return "Lofi Beats"
    else:
        # Model disabled, use fallback
        if fallback_func:
            return fallback_func(prompt)
        else:
            return "Lofi Beats"


def unload_model():
    """Unload model from memory (useful for testing/debugging)."""
    global _model, _tokenizer, _model_loaded

    if _model_loaded:
        del _model
        del _tokenizer
        _model = None
        _tokenizer = None
        _model_loaded = False
        torch.cuda.empty_cache() if torch.cuda.is_available() else None
        logger.info("Model unloaded from memory")


if __name__ == "__main__":
    # Test the model
    print("=" * 60)
    print("Testing QWEN Song Title Generator")
    print("=" * 60)

    test_prompts = [
        "Generate a lo-fi beat that has a happy mood and is very fast",
        "Create a slow peaceful lo-fi track with rain sounds",
        "Make a melancholic lo-fi beat perfect for a rainy day",
        "Generate a cozy lo-fi instrumental with piano for late night studying"
    ]

    for i, prompt in enumerate(test_prompts, 1):
        print(f"\n[{i}/{len(test_prompts)}] Prompt: {prompt}")
        title = generate_title(prompt)
        print(f"    Generated Title: \"{title}\"")

    print("\n" + "=" * 60)
    print("Test complete!")
    print("=" * 60)
