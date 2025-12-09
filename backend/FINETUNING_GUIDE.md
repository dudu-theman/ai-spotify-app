# QWEN Song Title Generator - Fine-tuning Guide

## Overview
This guide walks you through fine-tuning the Qwen2.5-0.5B model for song title generation and deploying it to your Render backend.

## Current Status
✅ All code files created
🔄 Training data generation in progress (~5-10 minutes)
⏳ Ready for fine-tuning once data generation completes

---

## Step 1: Wait for Training Data Generation ⏳

The training data generation script is currently running in the background. You can check progress:

```bash
# Watch the output
tail -f backend/training_data/song_titles.jsonl
```

**Expected output**: `backend/training_data/song_titles.jsonl` with ~200-250 examples

**Time**: ~5-10 minutes
**Cost**: ~$1-3 in Claude API usage

---

## Step 2: Fine-tune the Model Locally 🚀

Once training data generation completes:

### Install ML Dependencies

```bash
cd backend
pip install -r requirements.txt
```

**Note**: This will install PyTorch (~2GB), Transformers, and other ML libs. Make sure you have:
- 8GB+ free disk space
- 8GB+ RAM
- 30-60 minutes for training (CPU)

### Run Fine-tuning

```bash
python fine_tune_model.py
```

**What this does**:
1. Loads Qwen2.5-0.5B base model (~1.2GB download)
2. Applies LoRA fine-tuning (only trains 0.5% of parameters)
3. Saves fine-tuned model to `backend/models/qwen-title-generator/`
4. Tests the model with sample prompts

**Expected time**:
- **CPU**: ~30-60 minutes
- **GPU (if available)**: ~10-15 minutes

**Expected output**:
```
Training complete! Saving model...
Model saved to: backend/models/qwen-title-generator
```

### Test the Model

```bash
cd backend/helper_functions
python model_utils.py
```

This will test the model with 4 sample prompts. Verify that:
- Titles are <5 words
- Titles are creative and plausible
- No profanity or generic names

---

## Step 3: Upload Model to HuggingFace Hub 📦

To deploy the model to Render, you need to host it on HuggingFace:

### 3a. Create HuggingFace Account
1. Go to https://huggingface.co/join
2. Create a free account
3. Go to Settings → Access Tokens → Create new token (Write permissions)

### 3b. Install HuggingFace CLI

```bash
pip install huggingface_hub
huggingface-cli login
```

Paste your access token when prompted.

### 3c. Upload Model

```bash
cd backend/models/qwen-title-generator
huggingface-cli upload your-username/qwen-lofi-titles . .
```

Replace `your-username` with your HuggingFace username.

**Make it private** (optional):
- Go to https://huggingface.co/your-username/qwen-lofi-titles/settings
- Set repository to "Private"

---

## Step 4: Configure Render Environment Variables 🔧

In your Render dashboard (https://dashboard.render.com):

1. Go to your backend service
2. Navigate to **Environment** tab
3. Add these variables:

```
USE_FINETUNED_MODEL=true
HUGGINGFACE_MODEL_REPO=your-username/qwen-lofi-titles
HUGGINGFACE_TOKEN=your_huggingface_token_here
```

**Optional**: Keep Claude as fallback by leaving `ANTHROPIC_API_KEY` set.

---

## Step 5: Deploy to Render 🚀

### 5a. Update Render Build Command (Optional)

If you want the model to download automatically on deploy:

**Build Command**:
```bash
python backend/download_model.py && pip install -r backend/requirements.txt
```

### 5b. Verify RAM Requirements

Your Render Starter instance has **512MB RAM**. The 4-bit quantized model uses ~200-300MB.

**If you encounter out-of-memory errors**:
- Option 1: Upgrade to a higher Render plan (2GB RAM = $21/mo)
- Option 2: Set `USE_FINETUNED_MODEL=false` to use Claude API fallback

### 5c. Deploy

```bash
# Commit changes
git add .
git commit -m "Add fine-tuned QWEN model for song titles"
git push origin main
```

Render will automatically detect the push and redeploy.

**Expected deploy time**: ~10-15 minutes (includes downloading model from HF)

---

## Step 6: Test in Production 🧪

Once deployed, test the `/generate` endpoint:

```bash
curl -X POST "https://lofi-app-dc75.onrender.com/generate?q=Create%20a%20happy%20fast%20lofi%20beat" \
  -H "Cookie: session=YOUR_SESSION_COOKIE"
```

Check Render logs to see:
```
Loading model from: backend/models/qwen-title-generator
Model loaded successfully!
Generating title for: Create a happy fast lofi beat...
Generated title: "Joyful Velocity"
```

---

## Troubleshooting 🔍

### Training Data Generation Fails
- **Symptom**: Script crashes or no JSONL file created
- **Solution**: Check Claude API key in `.env`, ensure you have API credits

### Fine-tuning Out of Memory
- **Symptom**: "RuntimeError: CUDA out of memory" or system freezes
- **Solution**:
  - Close other applications
  - Reduce batch size in `fine_tune_model.py` (line ~148): `per_device_train_batch_size=2`

### Model Download Fails on Render
- **Symptom**: Render logs show "Failed to download model"
- **Solution**:
  - Verify `HUGGINGFACE_MODEL_REPO` and `HUGGINGFACE_TOKEN` are set correctly
  - Check HuggingFace repository is public or token has access
  - Model will fallback to Claude API automatically

### Low-Quality Titles
- **Symptom**: Titles are generic, too long, or don't match prompt
- **Solution**:
  - Generate more training data (500+ examples)
  - Review training data quality (`backend/training_data/song_titles.jsonl`)
  - Adjust temperature in `model_utils.py` (line ~140): `temperature=0.7` (lower = more conservative)

### Render 512MB RAM Insufficient
- **Symptom**: "Killed" or "Out of memory" in Render logs
- **Solution**:
  - Set `USE_FINETUNED_MODEL=false` to disable model and use Claude fallback
  - Upgrade Render plan to 2GB RAM
  - OR: Re-fine-tune with even smaller model (Qwen2.5-0.5B with 8-bit quant)

---

## Cost Breakdown 💰

| Item | Cost | Frequency |
|------|------|-----------|
| Training data generation | $1-3 | One-time |
| Fine-tuning (local) | $0 | One-time |
| HuggingFace hosting | $0 | Free tier |
| Render deployment | $0 (512MB tier) | Monthly |
| Claude API (fallback) | ~$0.001/request | Per title (if model fails) |

**Total setup cost**: ~$1-3 one-time

---

## Performance Expectations 📊

| Metric | Claude API | QWEN Fine-tuned (4-bit) |
|--------|-----------|------------------------|
| Latency | ~0.5-1s | ~2-5s (CPU) |
| Cost per title | $0.001 | $0 |
| RAM usage | 0MB | ~250-300MB |
| Quality | Excellent | Good (depends on training data) |
| Cold start | None | ~30-60s (first request) |

---

## Next Steps 🎯

1. ✅ Wait for training data generation to complete
2. ⏳ Run `python fine_tune_model.py`
3. ⏳ Upload model to HuggingFace
4. ⏳ Configure Render environment variables
5. ⏳ Deploy and test

---

## Files Created

```
backend/
├── helper_functions/
│   ├── generate_training_data.py   # Dataset generator
│   ├── model_utils.py               # Model loading & inference
│   └── song_maker.py                # Updated to use QWEN
├── training_data/
│   └── song_titles.jsonl            # Training dataset (generated)
├── models/
│   └── qwen-title-generator/        # Fine-tuned model (after training)
├── fine_tune_model.py               # Fine-tuning script
├── download_model.py                # Render deployment script
├── requirements.txt                 # Updated with ML deps
└── FINETUNING_GUIDE.md             # This file
```

---

## Support

If you encounter issues:
1. Check Render logs: https://dashboard.render.com → Your Service → Logs
2. Test locally first before deploying
3. Use Claude fallback by setting `USE_FINETUNED_MODEL=false`

Good luck! 🚀
