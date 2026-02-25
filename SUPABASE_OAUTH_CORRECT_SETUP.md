# Correct Supabase OAuth Setup

Based on your screenshot, here's what you need to configure:

## In Supabase Dashboard

### 1. OAuth Server Settings (What you showed in screenshot)

**Enable the Supabase OAuth Server**: ✅ Already enabled (green toggle)

**Site URL**: This should be your application URL
- Local: `http://localhost:8501`
- Production: `https://your-app.streamlit.app`

**Authorization Path**: `/oauth/consent` (default, leave as is)

**Allow Dynamic OAuth Apps**: ✅ Enabled (green toggle)

### 2. Google Provider Settings

Go to **Authentication** → **Providers** → **Google**

- **Enabled**: ✅ Turn on
- **Client ID**: Your Google OAuth Client ID
- **Client Secret**: Your Google OAuth Client Secret
- **Redirect URL**: This is shown by Supabase, should be:
  ```
  https://cbulptkxvnefcytfyrln.supabase.co/auth/v1/callback
  ```

## In Google Cloud Console

### Authorized Redirect URIs

Add these URLs to your Google OAuth Client:

1. **Supabase callback** (REQUIRED):
   ```
   https://cbulptkxvnefcytfyrln.supabase.co/auth/v1/callback
   ```

2. **Your app URL** (for reference, though Supabase handles the actual callback):
   ```
   http://localhost:8501
   ```

## In Your Application (.env file)

```env
SUPABASE_URL=https://cbulptkxvnefcytfyrln.supabase.co
SUPABASE_KEY=your_anon_key_here
SUPABASE_REDIRECT_URL=http://localhost:8501
```

## The Flow

Here's what happens:

1. User clicks "Sign in with Google" in your app
2. Your app calls Supabase: `client.auth.sign_in_with_oauth({"provider": "google"})`
3. Supabase generates OAuth URL and redirects user to Google
4. User authorizes on Google
5. **Google redirects to**: `https://cbulptkxvnefcytfyrln.supabase.co/auth/v1/callback`
6. **Supabase processes the callback** and creates a session
7. **Supabase redirects back to**: `http://localhost:8501` (your SUPABASE_REDIRECT_URL)
8. Your app checks for session with `client.auth.get_session()`

## The Python Client Issue

The problem is in step 8 - the Supabase Python client **cannot automatically detect the session** after the redirect because:

- OAuth tokens are in URL fragments (`#access_token=...`)
- Python runs server-side and can't read URL fragments
- The session needs to be established client-side first

## Working Solution

Since the Python client limitation exists, your best options are:

### Option 1: Guest Mode Only (Recommended)
Remove Google OAuth and just use Guest mode - it works perfectly for your use case.

### Option 2: Email/Password Auth
Use Supabase email/password authentication instead - this works with the Python client:

```python
# Sign up
client.auth.sign_up({"email": email, "password": password})

# Sign in
client.auth.sign_in_with_password({"email": email, "password": password})

# Check session
session = client.auth.get_session()
```

### Option 3: Use Supabase JS SDK
Implement authentication using JavaScript in a Streamlit component, then pass the session to Python.

## Current Status

Your Supabase OAuth is configured correctly, but the Python client can't complete the flow. The Google sign-in button will redirect to Google, but won't complete the login when it comes back to your app.

**Recommendation**: Use Guest mode or implement email/password auth instead.
