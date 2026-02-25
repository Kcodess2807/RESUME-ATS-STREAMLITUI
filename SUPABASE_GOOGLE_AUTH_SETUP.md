# Supabase Google Authentication Setup Guide

## ⚠️ Important Limitation

**The Supabase Python client cannot fully handle OAuth callbacks in Streamlit apps** because OAuth tokens are returned in URL fragments (`#access_token=...`) which are only accessible client-side via JavaScript, not server-side Python.

## Recommended Approach

For your ATS Resume Scorer, **Guest Mode is the best solution** because:
- ✅ Works immediately, no configuration needed
- ✅ Perfect for one-time resume analysis
- ✅ Users can download PDF reports
- ✅ No privacy concerns
- ✅ Simpler user experience

## If You Need Google Sign-In

You have these options:

### Option 1: Keep It Simple - Use Guest Mode Only

The current implementation already has Guest mode working perfectly. Just remove the Google sign-in button and keep only Guest mode.

### Option 2: Implement JavaScript-Based Auth

Use Streamlit components with Supabase JavaScript SDK to handle OAuth properly. This requires:
1. Creating a custom Streamlit component
2. Using `st.components.v1.html()` with Supabase JS SDK
3. Handling auth state via postMessage between iframe and Streamlit

See `SUPABASE_AUTH_NOTE.md` for implementation details.

### Option 3: Use Alternative Auth Methods

- **Streamlit Cloud Authentication**: Built-in for deployed apps
- **Email/Password**: Simpler than OAuth, works with Supabase Python client
- **Magic Links**: Email-based passwordless auth (works with Python client)
- **Auth0 or Firebase**: Better web SDK support

## Current Implementation Status

The code structure is in place for Supabase OAuth, but it won't work properly due to the Python client limitation. The app will:
- ✅ Show Google sign-in button
- ✅ Redirect to Google
- ❌ **Not complete the callback** (tokens in URL fragments can't be read by Python)
- ✅ Guest mode works perfectly as fallback

## Quick Fix: Remove Google Button

If you want to simplify, just use Guest mode:

### 1.1 Create OAuth Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Navigate to **APIs & Services** → **Credentials**
4. Click **Create Credentials** → **OAuth 2.0 Client ID**
5. Configure the consent screen if prompted:
   - User Type: External
   - App name: "ATS Resume Scorer"
   - User support email: your email
   - Developer contact: your email
6. Application type: **Web application**
7. Name: "ATS Resume Scorer"

### 1.2 Add Authorized Redirect URIs

You need to add your Supabase callback URL. The format is:
```
https://<your-project-ref>.supabase.co/auth/v1/callback
```

For your project:
```
https://cbulptkxvnefcytfyrln.supabase.co/auth/v1/callback
```

Add this URL to **Authorized redirect URIs**

8. Click **Create**
9. Copy your **Client ID** and **Client Secret** (you'll need these next)

## Step 2: Configure Supabase

### 2.1 Enable Google Provider

1. Go to your [Supabase Dashboard](https://app.supabase.com/)
2. Select your project: `cbulptkxvnefcytfyrln`
3. Navigate to **Authentication** → **Providers**
4. Find **Google** in the list
5. Toggle it to **Enabled**
6. Paste your Google **Client ID**
7. Paste your Google **Client Secret**
8. Click **Save**

### 2.2 Configure Site URL

1. In Supabase Dashboard, go to **Authentication** → **URL Configuration**
2. Set **Site URL** to:
   - Local development: `http://localhost:8501`
   - Production: Your deployed app URL (e.g., `https://your-app.streamlit.app`)
3. Add **Redirect URLs**:
   - `http://localhost:8501/**` (for local development)
   - Your production URL with wildcard (for deployment)

## Step 3: Update Your Application

Your application is already configured! The code in `app/config/auth.py` handles:
- Initiating Google OAuth flow
- Checking for existing sessions
- Extracting user information
- Managing logout

### Environment Variables

Make sure your `.env` file has:
```env
SUPABASE_URL=https://cbulptkxvnefcytfyrln.supabase.co
SUPABASE_KEY=your_supabase_anon_key
SUPABASE_REDIRECT_URL=http://localhost:8501
```

For production deployment, update `SUPABASE_REDIRECT_URL` to your production URL.

## Step 4: Test the Authentication

1. Start your Streamlit app:
   ```bash
   streamlit run app/app.py
   ```

2. Click "Continue with Google"
3. You should be redirected to Google's login page
4. After signing in, you'll be redirected back to your app
5. Your profile information should appear in the sidebar

## How It Works

### Authentication Flow

```
User clicks "Continue with Google"
    ↓
App calls Supabase auth.sign_in_with_oauth()
    ↓
User redirected to Google login
    ↓
User authorizes the app
    ↓
Google redirects to Supabase callback URL
    ↓
Supabase processes the OAuth response
    ↓
Supabase redirects to your app with session
    ↓
App checks session and extracts user info
    ↓
User is authenticated!
```

### Session Management

- Supabase automatically manages JWT tokens
- Sessions persist across page reloads
- Tokens are stored securely in browser storage
- `check_supabase_session()` verifies the session on each page load

## Features

✅ **Google Sign-In**: One-click authentication with Google accounts
✅ **Profile Pictures**: Automatically fetches user's Google profile picture
✅ **Secure**: Industry-standard OAuth 2.0 protocol
✅ **Persistent Sessions**: Users stay logged in across browser sessions
✅ **Guest Mode**: Still available for users who don't want to sign in

## Troubleshooting

### "Invalid redirect URI" error
- Verify the callback URL in Google Cloud Console matches exactly:
  `https://cbulptkxvnefcytfyrln.supabase.co/auth/v1/callback`
- No trailing slashes
- Must use HTTPS (except localhost)

### "OAuth provider not enabled" error
- Check that Google provider is enabled in Supabase Dashboard
- Verify Client ID and Secret are correctly entered
- Make sure you clicked "Save"

### User not staying logged in
- Check that Site URL is configured in Supabase
- Verify redirect URLs include your app URL
- Clear browser cache and cookies

### "Supabase is not configured" error
- Verify `SUPABASE_URL` and `SUPABASE_KEY` are set in `.env`
- Check that the Supabase client is being created successfully
- Ensure `supabase` Python package is installed: `pip install supabase`

## Production Deployment

### For Streamlit Cloud:

1. Add secrets in Streamlit Cloud dashboard:
   ```toml
   SUPABASE_URL = "https://cbulptkxvnefcytfyrln.supabase.co"
   SUPABASE_KEY = "your_supabase_anon_key"
   SUPABASE_REDIRECT_URL = "https://your-app.streamlit.app"
   ```

2. Update Google Cloud Console:
   - Add production callback URL:
     `https://cbulptkxvnefcytfyrln.supabase.co/auth/v1/callback`

3. Update Supabase:
   - Add production URL to Site URL
   - Add production URL to Redirect URLs

### For AWS/Other Hosting:

1. Set environment variables on your server
2. Update Google Cloud Console with production callback URL
3. Update Supabase URL configuration

## Security Best Practices

✅ Never commit `.env` or `secrets.toml` to version control
✅ Use environment variables for all credentials
✅ Keep your Supabase anon key public-facing (it's designed for this)
✅ Keep your service role key private (never expose in frontend)
✅ Enable Row Level Security (RLS) in Supabase for data protection
✅ Regularly rotate your Google OAuth client secret

## Additional Resources

- [Supabase Auth Documentation](https://supabase.com/docs/guides/auth)
- [Supabase Google OAuth Guide](https://supabase.com/docs/guides/auth/social-login/auth-google)
- [Google OAuth 2.0 Documentation](https://developers.google.com/identity/protocols/oauth2)

---

**Need Help?** Check the Supabase logs in your dashboard for detailed error messages.


```python
# In app/config/auth.py, update require_authentication():

def require_authentication(redirect_message: str = "Please log in to access this page."):
    """Guard function - blocks page access if user is not logged in."""
    init_session_state()
    
    if st.session_state.authenticated:
        return
    
    st.warning(redirect_message)
    
    st.markdown("""
    <div style="text-align: center; padding: 2rem;">
        <h2>🎯 ATS Resume Scorer</h2>
        <p style="color: #666;">Analyze your resume instantly</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("### 🚀 Get Started")
        if st.button("📄 Analyze My Resume", use_container_width=True, type="primary"):
            login_as_guest()
            st.rerun()
    
    st.stop()
```

This removes the Google button and makes Guest mode the primary authentication method.

## Summary

**Current Status**: The Google OAuth button is visible but won't work properly due to Python client limitations. Guest mode works perfectly.

**Recommendation**: Either use Guest mode only (simplest) or implement email/password auth (if you need persistent accounts).

See `SUPABASE_AUTH_NOTE.md` for technical details about the limitation.
