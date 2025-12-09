"""
Training data generator for song title fine-tuning.
Uses Claude Sonnet 3.5 to generate diverse prompt→title pairs.
"""

import json
import os
import random
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

# Initialize Claude client
client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# Template components for diverse lofi prompts
MOODS = [
    "happy", "sad", "melancholic", "peaceful", "energetic", "dreamy", "nostalgic",
    "chill", "uplifting", "calm", "reflective", "cozy", "ethereal", "groovy",
    "mellow", "jazzy", "ambient", "vibrant", "serene", "contemplative"
]

TEMPOS = [
    "slow", "fast", "moderate", "very slow", "upbeat", "downtempo", "mid-tempo",
    "lazy", "brisk", "relaxed pace", "steady", "flowing"
]

INSTRUMENTS = [
    "piano", "guitar", "saxophone", "vinyl crackle", "rain sounds", "strings",
    "synth", "bass", "drums", "flute", "trumpet", "bells", "chimes",
    "ocean waves", "bird chirps", "wind sounds", "record scratches"
]

ATMOSPHERES = [
    "rainy day", "sunset", "late night", "early morning", "coffee shop",
    "study session", "city lights", "forest", "beach", "starry night",
    "autumn leaves", "winter evening", "spring garden", "summer breeze"
]

QUALITIES = [
    "smooth", "warm", "crisp", "fuzzy", "clean", "distorted", "lo-fi",
    "reverb-heavy", "minimalist", "layered", "spacious", "intimate"
]

# Profanity filter (basic)
PROFANITY_KEYWORDS = [
    "shit", "fuck", "damn", "hell", "ass", "bitch", "crap", "bastard"
]


def generate_prompt():
    """Generate a random lofi beat prompt."""
    templates = [
        f"Generate a lo-fi beat that has a {random.choice(MOODS)} mood and is {random.choice(TEMPOS)}",
        f"Create a {random.choice(TEMPOS)} {random.choice(QUALITIES)} lo-fi track with {random.choice(INSTRUMENTS)}",
        f"Make a {random.choice(MOODS)} lo-fi beat perfect for a {random.choice(ATMOSPHERES)}",
        f"Generate a {random.choice(QUALITIES)} lo-fi instrumental with {random.choice(INSTRUMENTS)} and {random.choice(INSTRUMENTS)}",
        f"Create a {random.choice(TEMPOS)}, {random.choice(MOODS)} lo-fi beat with {random.choice(ATMOSPHERES)} vibes",
        f"Make a {random.choice(MOODS)} lo-fi track featuring {random.choice(INSTRUMENTS)} for {random.choice(ATMOSPHERES)}",
        f"Generate a {random.choice(QUALITIES)} {random.choice(TEMPOS)} beat with {random.choice(MOODS)} energy",
        f"Create an instrumental lo-fi track with {random.choice(INSTRUMENTS)}, {random.choice(MOODS)} and {random.choice(TEMPOS)}",
        f"Make a {random.choice(ATMOSPHERES)} inspired lo-fi beat that's {random.choice(MOODS)} and {random.choice(TEMPOS)}",
        f"Generate a {random.choice(MOODS)} lo-fi instrumental perfect for {random.choice(ATMOSPHERES)} listening",
    ]
    return random.choice(templates)


def generate_title_with_claude(prompt):
    """Use Claude Sonnet 3.5 to generate a high-quality song title."""
    system_prompt = """You are an expert at creating catchy, evocative song titles for lo-fi instrumental music.

CRITERIA for a good song title:
- MAXIMUM 5 words (prefer 2-3 words)
- Captures the "feeling" using strong, vivid adjectives
- Sounds like a real, plausible song title
- NO profanity or offensive language
- Can be poetic, metaphorical, or descriptive
- Should evoke emotion and atmosphere

EXAMPLES of GOOD titles:
- "Midnight Rain"
- "Golden Hour Dreams"
- "Velvet Sunrise"
- "Lazy Sunday Groove"
- "Neon Nostalgia"
- "Autumn's Whisper"
- "Urban Serenity"
- "Faded Polaroids"
- "Cosmic Coffeehouse"
- "Twilight Reflections"

EXAMPLES of BAD titles (don't do these):
- "A Song About Happiness" (too literal, boring)
- "Lo-fi Beat Number 5" (generic)
- "This Is A Very Happy Song With Piano" (way too long)
- "Untitled Track" (lazy)

Your task: Generate ONE song title based on the prompt. Output ONLY the title, nothing else."""

    user_message = f"Create a song title for this prompt: \"{prompt}\""

    response = client.messages.create(
        model="claude-sonnet-4-5-20250929",
        max_tokens=30,
        temperature=1.0,
        system=system_prompt,
        messages=[{"role": "user", "content": user_message}]
    )

    return response.content[0].text.strip().strip('"').strip("'")


def is_valid_title(title):
    """Validate title against quality criteria."""
    # Check word count
    word_count = len(title.split())
    if word_count > 5:
        return False, f"Too many words ({word_count})"

    # Check for profanity
    title_lower = title.lower()
    for word in PROFANITY_KEYWORDS:
        if word in title_lower:
            return False, f"Contains profanity: {word}"

    # Check if it's not just a generic template
    generic_phrases = ["lo-fi beat", "lofi beat", "instrumental track", "untitled"]
    for phrase in generic_phrases:
        if phrase in title_lower:
            return False, f"Too generic: {phrase}"

    return True, "Valid"


def generate_dataset(num_examples=250, output_file="backend/training_data/song_titles.jsonl"):
    """Generate training dataset."""
    dataset = []
    successful = 0
    failed = 0

    print(f"Generating {num_examples} training examples...")
    print("This will use Claude Sonnet 3.5 and take ~5-10 minutes.\n")

    for i in range(num_examples):
        try:
            # Generate prompt
            prompt = generate_prompt()

            # Generate title with Claude
            title = generate_title_with_claude(prompt)

            # Validate
            is_valid, reason = is_valid_title(title)

            if is_valid:
                dataset.append({"prompt": prompt, "title": title})
                successful += 1
                print(f"✓ [{successful}/{num_examples}] {prompt[:60]}... → \"{title}\"")
            else:
                failed += 1
                print(f"✗ [{i+1}/{num_examples}] REJECTED ({reason}): \"{title}\"")
                # Generate another to compensate
                num_examples += 1

        except Exception as e:
            print(f"✗ Error generating example {i+1}: {e}")
            failed += 1

        # Progress update every 25 examples
        if (i + 1) % 25 == 0:
            print(f"\n--- Progress: {successful} valid, {failed} rejected ---\n")

    # Save to JSONL
    with open(output_file, "w", encoding="utf-8") as f:
        for example in dataset:
            f.write(json.dumps(example, ensure_ascii=False) + "\n")

    print(f"\n{'='*60}")
    print(f"Dataset generation complete!")
    print(f"Total valid examples: {successful}")
    print(f"Total rejected: {failed}")
    print(f"Saved to: {output_file}")
    print(f"{'='*60}")

    # Print sample examples
    print("\nSample examples:")
    for example in random.sample(dataset, min(10, len(dataset))):
        print(f"  Prompt: {example['prompt']}")
        print(f"  Title: \"{example['title']}\"")
        print()

    return dataset


if __name__ == "__main__":
    # Generate 250 examples (will have ~200-230 after filtering)
    generate_dataset(num_examples=250)
