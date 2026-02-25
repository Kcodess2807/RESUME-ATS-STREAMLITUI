# Important Note: Supabase Python Client Limitation

## Issue with Current Implementation

The Supabase Python client (`supabase-py`) has a limitation: **it doesn't automatically handle OAuth callbacks in web applications**. 

The OAuth flow works like this:
1. User clicks "Sign in with Google"
2. Redirected to Google
3. Google redirects back with tokens in URL **fragments** (`#access_token=...`)
4. **Problem**: Python runs server-side and can't access URL fragments (they're client-side only)

## Recommended Solution

For production Supabase authentication with Streamlit, you have two options:

### Option 1: Use Supabase JavaScript Client (Recommended)

Use Streamlit's `st.components.v1.html()` to embed JavaScript that handles the OAuth flow:

```python
import streamlit.components.v1 as components

def supabase_auth_component():
    auth_html = """
    <script src="https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2"></script>
    <script>
        const supabase = supabase.createClient(
            'YOUR_SUPABASE_URL',
            'YOUR_SUPABASE_ANON_KEY'
        );
        
        // Handle OAuth
        async function signInWithGoogle() {
            const { data, error } = await supabase.auth.signInWithOAuth({
                provider: 'google'
            });
        }
        
        // Check session
        supabase.auth.onAuthStateChange((event, session) => {
            if (session) {
                // Send session to Streamlit
                window.parent.postMessage({
                    type: 'supabase-auth',
                    session: session
                }, '*');
            }
        });
    </script>
    """
    components.html(auth_html, height=0)
```

### Option 2: Use Guest Mode Only (Current Fallback)

The simplest solution is to use only Guest mode authentication, which works perfectly and doesn't require OAuth complexity.

## Current Status

The code is set up for Supabase OAuth, but **it won't work properly** until you either:
1. Implement the JavaScript component solution above
2. Use a different authentication method
3. Stick with Guest mode (which works great!)

## Why Guest Mode is Actually Good

For an ATS Resume Scorer:
- Users don't need persistent accounts
- Analysis results can be downloaded as PDF
- No privacy concerns about storing user data
- Simpler, faster user experience
- No OAuth configuration headaches

## If You Really Need Google Sign-In

Consider these alternatives:
1. **Streamlit's built-in authentication** (for Streamlit Cloud deployments)
2. **Auth0** or **Firebase Auth** with proper web SDKs
3. **Custom backend API** that handles OAuth server-side
4. **Session-based auth** with email/password (simpler than OAuth)

---

**Bottom Line**: The current implementation has the structure in place, but Supabase OAuth won't work properly with the Python client alone. Guest mode is your best bet for now!
