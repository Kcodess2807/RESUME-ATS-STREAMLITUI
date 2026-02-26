# Pages Directory - DEPRECATED

⚠️ **This directory is no longer used!**

## Current Architecture

The app now uses a **single-page architecture** with view routing in `main.py`.

The views are located in `app/views/`:
- `app/views/landing.py` - Home page
- `app/views/scorer.py` - ATS Scorer
- `app/views/history.py` - History
- `app/views/resources.py` - Resources

## Why This Directory Still Exists

These files were part of the old multi-page Streamlit architecture but are no longer used. They're kept for reference only.

## For Deployment

Make sure Streamlit Cloud is configured to run:
- **Main file**: `main.py` (NOT any file in this directory)

## Can I Delete This?

Yes, you can safely delete this entire `app/pages/` directory. The app doesn't use it anymore.
