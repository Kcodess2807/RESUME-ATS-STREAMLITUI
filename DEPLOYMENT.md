# Streamlit Cloud Deployment Guide

## Quick Deploy

1. **Push to GitHub**
   ```bash
   git add .
   git commit -m "Fix deployment issues"
   git push
   ```

2. **Deploy on Streamlit Cloud**
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Click "New app"
   - Select your repository
   - **Main file path**: `main.py`
   - Click "Deploy"

## Important Configuration

### Entry Point
The app uses `main.py` as the entry point. Make sure Streamlit Cloud is configured to run `main.py`.

### Secrets (Optional)
If using Supabase database features:
1. In Streamlit Cloud dashboard, go to your app settings
2. Click "Secrets"
3. Add:
   ```toml
   [supabase]
   url = "your-supabase-url"
   key = "your-supabase-anon-key"
   ```

### System Dependencies
The `packages.txt` file includes:
- `libmagic1` - For file type detection
- `libmagic-dev` - Development headers

### Python Dependencies
All Python packages are in `requirements.txt`. The app will:
- Download spaCy model at startup
- Download sentence-transformers models on first use
- This may take 1-2 minutes on first deployment

## Architecture

The app uses a single-page architecture with view routing:
- `main.py` - Entry point with navigation
- `app/views/landing.py` - Home page
- `app/views/scorer.py` - Resume analysis
- `app/views/history.py` - Analysis history
- `app/views/resources.py` - Tips and resources

## Troubleshooting

### App won't start
- Check logs in Streamlit Cloud dashboard
- Verify `main.py` is set as the main file
- Check that all dependencies installed successfully

### Models not loading
- First startup takes longer (downloading models)
- Check memory usage (may need to upgrade plan)
- Models are cached after first download

### Import errors
- Verify all files are committed to git
- Check that `app/views/__init__.py` exists
- Ensure Python version matches `runtime.txt`

### CSS not loading
- Check that `assets/styles.css` exists
- Verify file paths are correct
- CSS loading failures are non-fatal (app still works)

## Performance Tips

1. **Model caching**: Models are cached after first download
2. **Session state**: History is per-session (not persistent)
3. **File uploads**: Limited to 10MB (configured in `.streamlit/config.toml`)

## Local Testing

Before deploying, test locally:
```bash
streamlit run main.py
```

Visit `http://localhost:8501` to verify everything works.
