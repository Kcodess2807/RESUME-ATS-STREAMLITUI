# Streamlit Cloud Deployment Guide

## Common Issues and Fixes

### Issue 1: Google OAuth Credentials

**Problem:** `google_credentials.json` is not in the repository (it's gitignored for security).

**Solution:** Use Streamlit Secrets instead.

#### In Streamlit Cloud Dashboard:

1. Go to your app settings
2. Click on "Secrets" section
3. Add this configuration:

```toml
# Supabase Database Configuration
[supabase]
url = "https://cbulptkxvnefcytfyrln.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImNidWxwdGt4dm5lZmN5dGZ5cmxuIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjQ1ODA1NzMsImV4cCI6MjA4MDE1NjU3M30.QqzKckzPOCD4lpPbvxCKlI4wbOiSWUoD1EFvAc60Gzg"
anon_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImNidWxwdGt4dm5lZmN5dGZ5cmxuIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjQ1ODA1NzMsImV4cCI6MjA4MDE1NjU3M30.QqzKckzPOCD4lpPbvxCKlI4wbOiSWUoD1EFvAc60Gzg"

# Google OAuth Configuration
[google_oauth]
client_id = "YOUR_GOOGLE_CLIENT_ID.apps.googleusercontent.com"
client_secret = "YOUR_GOOGLE_CLIENT_SECRET"
redirect_uri = "https://your-app-name.streamlit.app"
```

**Important:** Replace `your-app-name` with your actual Streamlit Cloud app URL!

### Issue 2: Google OAuth Redirect URI

**Problem:** OAuth redirect URI doesn't match production URL.

**Solution:** Update Google Cloud Console:

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Navigate to APIs & Services > Credentials
3. Edit your OAuth 2.0 Client ID
4. Add authorized redirect URIs:
   - `https://your-app-name.streamlit.app`
   - `https://your-app-name.streamlit.app/`
   - `https://your-app-name.streamlit.app/component/streamlit_google_auth.login_button`
5. Add authorized JavaScript origins:
   - `https://your-app-name.streamlit.app`

### Issue 3: Missing google_credentials.json

**Problem:** App tries to load `google_credentials.json` but it doesn't exist in deployment.

**Solution:** Update `main.py` to use Streamlit secrets as fallback.

### Issue 4: Package Installation Failures

**Problem:** Some packages fail to install on Streamlit Cloud.

**Solution:** Check `requirements.txt` and `packages.txt` are correct.

## Deployment Checklist

### Before Deploying:

- [ ] Push all code to GitHub
- [ ] Verify `.gitignore` excludes secrets
- [ ] Check `requirements.txt` is up to date
- [ ] Verify `packages.txt` has system dependencies

### In Streamlit Cloud:

- [ ] Connect to GitHub repository
- [ ] Set main file path: `main.py`
- [ ] Add secrets (see above)
- [ ] Update redirect URI in secrets
- [ ] Deploy app

### After Deploying:

- [ ] Get your app URL (e.g., `https://your-app.streamlit.app`)
- [ ] Update Google Cloud Console redirect URIs
- [ ] Update secrets with correct redirect_uri
- [ ] Reboot app in Streamlit Cloud
- [ ] Test authentication

## Common Errors

### Error: "FileNotFoundError: google_credentials.json"

**Fix:** The app needs to use secrets instead of the file. Update main.py.

### Error: "redirect_uri_mismatch"

**Fix:** 
1. Check Google Console has your Streamlit Cloud URL
2. Check secrets has correct redirect_uri
3. URLs must match exactly (no trailing slashes)

### Error: "ModuleNotFoundError"

**Fix:** Check requirements.txt has all dependencies:
```
streamlit>=1.35.0
streamlit-google-auth>=1.1.8
supabase>=2.3.0
```

### Error: "libmagic not found"

**Fix:** Verify packages.txt contains:
```
libmagic1
libmagic-dev
```

## Testing Deployment

1. Visit your app URL
2. Should see login screen
3. Click "Sign in with Google"
4. Should redirect to Google
5. Approve permissions
6. Should redirect back to app
7. Should be authenticated

## Logs

To check deployment logs:
1. Go to Streamlit Cloud dashboard
2. Click on your app
3. Click "Manage app"
4. View logs for errors

## Need Help?

Common log errors and solutions:

**"No module named 'streamlit_google_auth'"**
- Add to requirements.txt: `streamlit-google-auth>=1.1.8`

**"FileNotFoundError: google_credentials.json"**
- Update main.py to use secrets (see fix below)

**"Authentication failed"**
- Check secrets are configured
- Verify Google OAuth redirect URIs

## Quick Fix for google_credentials.json Issue

The app should check for secrets first, then fall back to file. This is already handled by streamlit-google-auth if you configure secrets properly.
