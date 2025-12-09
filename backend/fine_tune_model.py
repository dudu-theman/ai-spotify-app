"""
Fine-tune Qwen2.5-0.5B for song title generation using LoRA.
Optimized for 512MB deployment with 4-bit quantization.
"""

import json
import os
import torch
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    TrainingArguments,
    Trainer,
    DataCollatorForLanguageModeling,
    BitsAndBytesConfig
)
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from datasets import Dataset

# Configuration
MODEL_NAME = "Qwen/Qwen2.5-0.5B"  # Smallest QWEN model
OUTPUT_DIR = "models/qwen-title-generator"
TRAINING_DATA = "training_data/song_titles.jsonl"

# LoRA configuration (efficient fine-tuning)
LORA_CONFIG = LoraConfig(
    r=8,  # Rank (lower for smaller model)
    lora_alpha=16,
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],  # Attention layers
    lora_dropout=0.05,
    bias="none",
    task_type="CAUSAL_LM"
)

# 4-bit quantization configuration (for deployment)
QUANT_CONFIG = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.float16,
    bnb_4bit_use_double_quant=True
)


def load_training_data(file_path):
    """Load training data from JSONL file."""
    data = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            example = json.loads(line)
            data.append(example)
    print(f"Loaded {len(data)} training examples")
    return data


def format_training_example(example):
    """Format a single example for training."""
    # Simple format: Prompt → Title
    # Using a clear delimiter for the model to learn
    prompt = example['prompt']
    title = example['title']

    # Format: "Create a song title for: [PROMPT]\nTitle: [TITLE]"
    formatted = f"Create a song title for: {prompt}\nTitle: {title}"
    return formatted


def prepare_dataset(tokenizer, training_data, max_length=128):
    """Prepare dataset for training."""
    # Format all examples
    formatted_texts = [format_training_example(ex) for ex in training_data]

    # Tokenize
    tokenized = tokenizer(
        formatted_texts,
        truncation=True,
        max_length=max_length,
        padding=False,
        return_tensors=None
    )

    # Create HuggingFace dataset
    dataset = Dataset.from_dict({
        "input_ids": tokenized["input_ids"],
        "attention_mask": tokenized["attention_mask"]
    })

    # Split into train/eval (90/10)
    split = dataset.train_test_split(test_size=0.1, seed=42)

    print(f"Training samples: {len(split['train'])}")
    print(f"Evaluation samples: {len(split['test'])}")

    return split['train'], split['test']


def fine_tune_model():
    """Main fine-tuning function."""
    print("=" * 60)
    print("QWEN 0.5B Song Title Generator - Fine-tuning")
    print("=" * 60)

    # Check if training data exists
    if not os.path.exists(TRAINING_DATA):
        print(f"Error: Training data not found at {TRAINING_DATA}")
        print("Please run generate_training_data.py first.")
        return

    # Load training data
    print("\n[1/6] Loading training data...")
    training_data = load_training_data(TRAINING_DATA)

    # Load tokenizer
    print("\n[2/6] Loading tokenizer...")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, trust_remote_code=True)
    tokenizer.pad_token = tokenizer.eos_token  # Set padding token

    # Load base model (for training, don't use 4-bit yet)
    print("\n[3/6] Loading base model...")
    print("Note: This may take a few minutes and use ~4-6GB RAM during training")
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_NAME,
        torch_dtype=torch.float16,  # Use FP16 for faster training
        device_map="auto",
        trust_remote_code=True
    )

    # Prepare model for LoRA
    print("\n[4/6] Applying LoRA configuration...")
    model = prepare_model_for_kbit_training(model)
    model = get_peft_model(model, LORA_CONFIG)

    # Print trainable parameters
    trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    total_params = sum(p.numel() for p in model.parameters())
    print(f"Trainable parameters: {trainable_params:,} ({100 * trainable_params / total_params:.2f}%)")

    # Prepare datasets
    print("\n[5/6] Preparing datasets...")
    train_dataset, eval_dataset = prepare_dataset(tokenizer, training_data)

    # Training arguments
    training_args = TrainingArguments(
        output_dir=OUTPUT_DIR,
        num_train_epochs=3,
        per_device_train_batch_size=4,
        per_device_eval_batch_size=4,
        gradient_accumulation_steps=4,  # Effective batch size = 16
        learning_rate=2e-4,
        weight_decay=0.01,
        warmup_ratio=0.05,
        logging_steps=10,
        eval_strategy="steps",
        eval_steps=50,
        save_strategy="steps",
        save_steps=100,
        save_total_limit=2,
        fp16=True,  # Use mixed precision
        report_to="none",  # Don't use wandb/tensorboard
        load_best_model_at_end=True,
        metric_for_best_model="eval_loss",
    )

    # Data collator
    data_collator = DataCollatorForLanguageModeling(
        tokenizer=tokenizer,
        mlm=False  # Causal LM, not masked LM
    )

    # Initialize trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=eval_dataset,
        data_collator=data_collator,
    )

    # Train!
    print("\n[6/6] Starting training...")
    print("This will take ~30-60 minutes on CPU, ~10-15 minutes on GPU")
    print("-" * 60)

    trainer.train()

    # Save final model
    print("\n" + "=" * 60)
    print("Training complete! Saving model...")
    model.save_pretrained(OUTPUT_DIR)
    tokenizer.save_pretrained(OUTPUT_DIR)

    print(f"\nModel saved to: {OUTPUT_DIR}")
    print("=" * 60)

    # Test the model
    print("\n" + "=" * 60)
    print("Testing fine-tuned model...")
    test_prompts = [
        "Generate a lo-fi beat that has a happy mood and is very fast",
        "Create a slow peaceful lo-fi track with rain sounds",
        "Make a melancholic lo-fi beat perfect for a rainy day"
    ]

    for prompt in test_prompts:
        test_input = f"Create a song title for: {prompt}\nTitle:"
        inputs = tokenizer(test_input, return_tensors="pt").to(model.device)

        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=20,
                temperature=0.9,
                do_sample=True,
                pad_token_id=tokenizer.eos_token_id
            )

        generated = tokenizer.decode(outputs[0], skip_special_tokens=True)
        title = generated.split("Title:")[-1].strip().split("\n")[0]

        print(f"\nPrompt: {prompt}")
        print(f"Generated Title: \"{title}\"")

    print("\n" + "=" * 60)
    print("Fine-tuning complete!")
    print("\nNext steps:")
    print("1. Test the model further with various prompts")
    print("2. Upload to HuggingFace Hub (optional): model.push_to_hub('your-username/qwen-lofi-titles')")
    print("3. Update backend code to use this model")
    print("=" * 60)


if __name__ == "__main__":
    fine_tune_model()
