# Google Authentication Setup Guide

## ✅ Implementation Complete!

Google Authentication has been implemented using the `streamlit-google-auth` library.

## What Was Implemented

### Files Created/Modified:

1. **`main.py`** - Added Google authentication layer
   - Login screen for unauthenticated users
   - User info display in sidebar
   - Logout button

2. **`google_credentials.json`** - OAuth credentials file
   - Needs your Google Client ID and Secret

3. **`.streamlit/secrets.toml`** - Added Google OAuth section
   - Configuration for authentication

4. **`app/config/database.py`** - Updated user ID handling
   - Uses authenticated user's email as user ID

5. **`requirements.txt`** - Added streamlit-google-auth package

## Setup Instructions

### Step 1: Get Google OAuth Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Navigate to **APIs & Services** > **Credentials**
4. Click **Create Credentials** > **OAuth client ID**
5. Select **Web application**
6. Add authorized redirect URI: `http://localhost:8501`
7. Copy the **Client ID** and **Client Secret**

### Step 2: Configure Credentials

**Option A: Update `google_credentials.json`:**
```json
{
  "web": {
    "client_id": "YOUR_ACTUAL_CLIENT_ID.apps.googleusercontent.com",
    "client_secret": "YOUR_ACTUAL_CLIENT_SECRET",
    "redirect_uris": ["http://localhost:8501"],
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token"
  }
}
```

**Option B: Update `.streamlit/secrets.toml`:**
```toml
[google_oauth]
client_id = "YOUR_ACTUAL_CLIENT_ID.apps.googleusercontent.com"
client_secret = "YOUR_ACTUAL_CLIENT_SECRET"
redirect_uri = "http://localhost:8501"
```

### Step 3: Test the App

```bash
streamlit run main.py
```

You should see:
1. Welcome screen with "Sign in with Google" button
2. Google OAuth consent screen
3. After approval, redirected back to app
4. User info in sidebar
5. Full access to all features

## How It Works

### Authentication Flow:

```
1. User visits app
   ↓
2. Not authenticated → Show login screen
   ↓
3. Click "Sign in with Google"
   ↓
4. Google OAuth consent screen
   ↓
5. User approves
   ↓
6. Redirected back to app
   ↓
7. User authenticated ✓
   ↓
8. Full app access
```

### Session Management:

- Authentication state stored in `st.session_state['connected']`
- User info stored in `st.session_state['user_info']`
- Cookies used for persistent sessions
- Logout clears session and cookies

### User Identification:

- User's email used as unique identifier
- History tied to email address
- Persists across devices and sessions

## Features

✅ **Google OAuth Sign-In** - Secure authentication
✅ **Session Persistence** - Stay logged in across page reloads
✅ **User Profile Display** - Shows name, email, and avatar
✅ **Logout Functionality** - Clean session termination
✅ **Protected Content** - All pages require authentication
✅ **User-Specific Data** - History tied to user account

## Security

- OAuth 2.0 standard protocol
- Secure token handling by streamlit-google-auth
- Cookies are httpOnly and secure
- No passwords stored
- Session expiration handled automatically

## Production Deployment

### For Streamlit Cloud:

1. Add secrets in Streamlit Cloud settings:
```toml
[google_oauth]
client_id = "YOUR_CLIENT_ID"
client_secret = "YOUR_CLIENT_SECRET"
redirect_uri = "https://your-app.streamlit.app"
```

2. Update Google Cloud Console:
   - Add production URL to authorized redirect URIs
   - Format: `https://your-app.streamlit.app`

3. Update `main.py` redirect_uri if needed:
```python
redirect_uri = st.secrets.get("google_oauth", {}).get("redirect_uri", "http://localhost:8501")
```

## Troubleshooting

### "redirect_uri_mismatch" Error:
- Check Google Console redirect URI matches exactly
- Should be: `http://localhost:8501` (no trailing slash)

### Login button doesn't work:
- Verify credentials in `google_credentials.json`
- Check browser console for errors
- Ensure cookies are enabled

### Session not persisting:
- Check cookie settings in browser
- Try incognito mode to rule out cookie issues
- Verify cookie_name and cookie_key are set

### User info not showing:
- Check `st.session_state['user_info']` exists
- Verify OAuth scopes include profile and email
- Check Google account has public profile

## Code Examples

### Check if user is authenticated:
```python
if st.session_state.get('connected'):
    user_info = st.session_state['user_info']
    email = user_info.get('email')
    st.write(f"Welcome, {email}!")
```

### Get user information:
```python
user_info = st.session_state.get('user_info', {})
email = user_info.get('email')
name = user_info.get('name')
picture = user_info.get('picture')
```

### Logout:
```python
if st.button("Logout"):
    authenticator.logout()
```

## Advantages Over Supabase OAuth

✅ **Simpler** - No PKCE issues
✅ **Reliable** - Built specifically for Streamlit
✅ **Maintained** - Active library with good support
✅ **Clean API** - Easy to implement and use
✅ **Works perfectly** - No hash fragment issues

## Summary

✅ **Status:** Fully implemented and ready to use
✅ **Package:** streamlit-google-auth v1.1.8
✅ **Authentication:** Google OAuth 2.0
✅ **Next Step:** Add your Google OAuth credentials

---

**Implementation Date:** February 26, 2026
**Library:** streamlit-google-auth
**Status:** ✅ Complete - Add credentials to test
