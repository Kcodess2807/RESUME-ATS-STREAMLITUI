# Streamlit Cloud Deployment Checklist

## ✅ Step-by-Step Deployment

### 1. Update Google Cloud Console

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Navigate to **APIs & Services** > **Credentials**
3. Click on your OAuth 2.0 Client ID
4. Under **Authorized redirect URIs**, add:
   ```
   https://your-app-name.streamlit.app
   https://your-app-name.streamlit.app/
   https://your-app-name.streamlit.app/component/streamlit_google_auth.login_button
   ```
5. Under **Authorized JavaScript origins**, add:
   ```
   https://your-app-name.streamlit.app
   ```
6. Click **Save**

**Note:** Replace `your-app-name` with your actual Streamlit Cloud app name!

### 2. Configure Streamlit Cloud Secrets

1. Go to [Streamlit Cloud](https://share.streamlit.io/)
2. Find your app
3. Click **Settings** (⚙️)
4. Click **Secrets**
5. Paste this configuration:

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
redirect_uri = "https://YOUR-APP-NAME.streamlit.app"
```

**IMPORTANT:** Change `YOUR-APP-NAME` to your actual app URL!

6. Click **Save**

### 3. Deploy/Reboot App

1. If first deployment:
   - Click **Deploy** button
   - Wait for build to complete

2. If already deployed:
   - Click **Reboot app** to apply new secrets
   - Wait for app to restart

### 4. Test Authentication

1. Visit your app URL: `https://your-app-name.streamlit.app`
2. Should see login screen
3. Click "Sign in with Google"
4. Approve permissions
5. Should redirect back and be authenticated

## Common Issues

### Issue: "FileNotFoundError: google_credentials.json"

**Status:** ✅ Fixed in latest code
**Solution:** The app now uses secrets in production

### Issue: "redirect_uri_mismatch"

**Cause:** Google OAuth redirect URI doesn't match
**Fix:**
1. Check Google Console has your exact Streamlit URL
2. Check secrets has correct redirect_uri
3. URLs must match exactly

### Issue: App won't start

**Check:**
1. View logs in Streamlit Cloud dashboard
2. Look for import errors
3. Verify all packages in requirements.txt
4. Check packages.txt has system dependencies

### Issue: Authentication fails silently

**Fix:**
1. Verify secrets are saved correctly
2. Check Google OAuth credentials are correct
3. Ensure redirect URIs match in both places

## Verification Checklist

Before going live:

- [ ] Code pushed to GitHub
- [ ] Google Console redirect URIs updated
- [ ] Streamlit secrets configured
- [ ] redirect_uri in secrets matches app URL
- [ ] App deployed/rebooted
- [ ] Login tested and working
- [ ] User info displays correctly
- [ ] Logout works
- [ ] History saves correctly

## Your App Details

**App URL:** `https://your-app-name.streamlit.app`
**Google Client ID:** `YOUR_CLIENT_ID.apps.googleusercontent.com`
**Supabase URL:** `https://cbulptkxvnefcytfyrln.supabase.co`

## Need Help?

1. Check Streamlit Cloud logs
2. Verify secrets are configured
3. Test Google OAuth redirect URIs
4. Check browser console for errors

## Quick Commands

```bash
# Push latest code
git add .
git commit -m "fix: deployment configuration"
git push origin main

# Streamlit Cloud will auto-deploy
```

---

**Last Updated:** February 26, 2026
**Status:** Ready for deployment
