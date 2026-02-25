# Google Auth Fix Guide

## What Was Fixed

The Google OAuth authentication with Supabase wasn't working due to issues with PKCE (Proof Key for Code Exchange) flow implementation. Here's what was fixed:

### 1. Improved Code Verifier Extraction

The original code tried to extract the `code_verifier` from Supabase SDK's internal storage, but this wasn't reliable. The fix:

- Added multiple fallback methods to extract the code_verifier
- Added better error handling and logging
- Added a fallback to generate a new code_verifier if needed

### 2. Better Error Messages

- Added more descriptive error messages for users
- Added detailed logging for debugging
- Suggested Guest login as fallback when OAuth fails

### 3. Added Debug Tool

Created `debug_google_auth.py` to help diagnose configuration issues.

## How to Test the Fix

### Step 1: Run the Debug Tool

```bash
python debug_google_auth.py
```

This will check:
- ✅ Supabase connection
- ✅ OAuth URL generation
- ✅ Code verifier extraction
- ✅ Configuration checklist

### Step 2: Verify Supabase Configuration

Go to your Supabase Dashboard and verify:

#### A. Google Provider Settings
1. Navigate to: **Authentication → Providers → Google**
2. Ensure:
   - ✅ Google provider is **ENABLED** (toggle is green)
   - ✅ **Client ID** is filled in (from Google Cloud Console)
   - ✅ **Client Secret** is filled in (from Google Cloud Console)
   - ✅ Click **Save**

#### B. URL Configuration
1. Navigate to: **Authentication → URL Configuration**
2. Set:
   - **Site URL**: `http://localhost:8501` (for local) or your production URL
   - **Redirect URLs**: Add `http://localhost:8501/**` (for local)

### Step 3: Verify Google Cloud Console

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Navigate to: **APIs & Services → Credentials**
3. Click on your OAuth 2.0 Client ID
4. Under **Authorized redirect URIs**, ensure you have:
   ```
   https://cbulptkxvnefcytfyrln.supabase.co/auth/v1/callback
   ```
5. Click **Save**

### Step 4: Test in Your App

```bash
streamlit run main.py
```

1. Click "Continue with Google"
2. Sign in with your Google account
3. You should be redirected back and authenticated

## Troubleshooting

### Issue: "Authentication failed — session expired during sign-in"

**Cause**: The code_verifier wasn't saved or couldn't be retrieved.

**Solutions**:
1. Check file permissions on `/tmp/streamlit_pkce/` directory
2. Try clearing the temp directory: `rm -rf /tmp/streamlit_pkce/`
3. Use Guest login as alternative

### Issue: "Invalid redirect URI"

**Cause**: Mismatch between Google Cloud Console and Supabase callback URL.

**Solution**:
1. Verify the redirect URI in Google Cloud Console is exactly:
   ```
   https://cbulptkxvnefcytfyrln.supabase.co/auth/v1/callback
   ```
2. No trailing slashes
3. Must match exactly (case-sensitive)

### Issue: "OAuth provider not enabled"

**Cause**: Google provider not enabled in Supabase.

**Solution**:
1. Go to Supabase Dashboard
2. Authentication → Providers → Google
3. Toggle to **Enabled**
4. Add Client ID and Secret
5. Click **Save**

### Issue: Authentication works but user info not showing

**Cause**: Session state not being set correctly.

**Solution**:
1. Check browser console for errors
2. Clear browser cache and cookies
3. Try in incognito/private mode

## Alternative: Use Guest Mode

If Google OAuth continues to have issues, Guest mode is already working perfectly:

```python
# In app/config/auth.py, simplify require_authentication():

def require_authentication(redirect_message: str = "Please log in to access this page."):
    """Guard function - blocks page access if user is not logged in."""
    init_session_state()
    
    if st.session_state.authenticated:
        return
    
    st.warning(redirect_message)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("### 🚀 Get Started")
        if st.button("📄 Analyze My Resume", use_container_width=True, type="primary"):
            login_as_guest()
            st.rerun()
    
    st.stop()
```

## Understanding the PKCE Flow

Here's what happens during Google OAuth with PKCE:

```
1. User clicks "Continue with Google"
   ↓
2. App generates code_verifier and code_challenge
   ↓
3. App saves code_verifier to /tmp/streamlit_pkce/latest_verifier.json
   ↓
4. User redirected to Google with code_challenge
   ↓
5. User authorizes on Google
   ↓
6. Google redirects to Supabase with auth code
   ↓
7. Supabase redirects back to app with ?code=<auth_code>
   ↓
8. App loads code_verifier from file
   ↓
9. App exchanges code + code_verifier for session
   ↓
10. User authenticated!
```

The critical part is step 8 - the code_verifier must survive the browser redirect, which is why we save it to a file.

## Checking Logs

When testing, watch the terminal for log messages:

```bash
# Good signs:
✅ Saved PKCE code_verifier to /tmp/streamlit_pkce/latest_verifier.json
✅ Loaded PKCE code_verifier from /tmp/streamlit_pkce/latest_verifier.json
✅ PKCE login successful for: user@example.com

# Bad signs:
❌ No code_verifier found!
❌ PKCE code exchange failed
❌ Failed to generate OAuth URL
```

## Files Modified

1. **app/config/auth.py**
   - Improved `_generate_oauth_url_and_save_verifier()` function
   - Better error handling in `check_supabase_session()`
   - Added more detailed logging

2. **debug_google_auth.py** (new)
   - Debug tool to test OAuth configuration

## Next Steps

If Google OAuth still doesn't work after following this guide:

1. **Option 1**: Use Guest mode only (simplest, already working)
2. **Option 2**: Implement email/password auth (works better with Python SDK)
3. **Option 3**: Use Streamlit Cloud's built-in authentication
4. **Option 4**: Implement custom JavaScript-based OAuth using Streamlit components

## Support

If you need more help:
1. Run `python debug_google_auth.py` and share the output
2. Check Supabase logs in Dashboard → Logs
3. Check browser console for JavaScript errors
4. Share terminal logs when clicking "Continue with Google"
