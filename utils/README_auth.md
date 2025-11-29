# Authentication Module

## Overview

The authentication module provides secure user authentication and session management for the ATS Resume Scorer application using `streamlit-authenticator`.

## Features

- **User Login**: Secure authentication with username/password
- **Session Management**: Automatic session creation and tracking
- **Session Expiration**: Configurable inactivity timeout (default: 60 minutes)
- **Protected Pages**: Easy-to-use decorators for page protection
- **User Information Display**: Show logged-in user details in sidebar
- **Logout Functionality**: Clean session termination

## Requirements Addressed

- **2.1**: Unauthenticated access protection with redirect to login
- **2.2**: Valid credential acceptance with session creation
- **2.3**: Session information display in sidebar
- **2.4**: Logout functionality with session termination
- **2.5**: Expired session re-authentication

## Configuration

The authentication system uses a YAML configuration file located at `config/credentials.yaml`. If this file doesn't exist, a default configuration is created automatically with demo users.

### Default Users

- **Username**: `demo_user`, **Password**: `demo123`
- **Username**: `test_user`, **Password**: `test123`

### Configuration Structure

```yaml
credentials:
  usernames:
    demo_user:
      name: Demo User
      password: <hashed_password>
      email: demo@example.com

cookie:
  name: ats_scorer_auth
  key: <secret_key>
  expiry_days: 30

preauthorized:
  emails: []
```

## Usage

### Basic Usage - Protect a Page

```python
import streamlit as st
from utils.auth import require_authentication, display_user_info, logout_button

# Require authentication for this page
require_authentication("Please log in to access the ATS Scorer.")

# Your page content here
st.title("ATS Resume Scorer")

# Display user info in sidebar
display_user_info(location='sidebar')

# Display logout button
logout_button(location='sidebar')
```

### Advanced Usage - Custom Authentication Flow

```python
from utils.auth import AuthenticationManager

# Create authentication manager
auth = AuthenticationManager()

# Display login form
name, authentication_status, username = auth.login(location='main')

if authentication_status:
    st.success(f"Welcome {name}!")
    
    # Your authenticated content here
    st.write("This is protected content")
    
    # Display user info
    auth.display_user_info(location='sidebar')
    
    # Logout button
    auth.logout(location='sidebar')
elif authentication_status == False:
    st.error("Username/password is incorrect")
else:
    st.info("Please enter your credentials")
```

### Check Authentication Status

```python
from utils.auth import is_authenticated

if is_authenticated():
    st.write("User is logged in")
else:
    st.write("User is not logged in")
```

### Session Expiration

The system automatically checks for session expiration based on inactivity. The default timeout is 60 minutes, but this can be customized:

```python
auth = AuthenticationManager()

# Check session with custom timeout (30 minutes)
if auth.check_session_expiration(max_inactive_minutes=30):
    st.write("Session is active")
else:
    st.warning("Session expired. Please log in again.")
```

## API Reference

### AuthenticationManager Class

#### `__init__(config_path: str = "config/credentials.yaml")`
Initialize the authentication manager with optional custom config path.

#### `login(location: str = 'main') -> Tuple[Optional[str], Optional[str], Optional[str]]`
Display login form and handle authentication.
- **Returns**: (name, authentication_status, username)

#### `logout(location: str = 'sidebar')`
Display logout button and handle session termination.

#### `is_authenticated() -> bool`
Check if the current user is authenticated.

#### `check_session_expiration(max_inactive_minutes: int = 60) -> bool`
Check if the current session has expired due to inactivity.

#### `require_authentication(redirect_message: str = "Please log in to access this page.")`
Require authentication for the current page. Stops execution if not authenticated.

#### `display_user_info(location: str = 'sidebar')`
Display user information (name, username, session duration).

### Convenience Functions

#### `get_auth_manager() -> AuthenticationManager`
Get or create the global authentication manager instance.

#### `require_authentication(redirect_message: str = "Please log in to access this page.")`
Convenience function to require authentication for a page.

#### `display_user_info(location: str = 'sidebar')`
Convenience function to display user information.

#### `logout_button(location: str = 'sidebar')`
Convenience function to display logout button.

#### `is_authenticated() -> bool`
Convenience function to check if user is authenticated.

## Security Considerations

1. **Password Hashing**: All passwords are hashed using `streamlit-authenticator`'s built-in hasher
2. **Cookie Security**: Session cookies are used for persistent authentication
3. **Session Expiration**: Automatic timeout after inactivity
4. **Secret Key**: In production, replace the default cookie key with a secure random key

## Adding New Users

To add new users, edit the `config/credentials.yaml` file:

```python
import streamlit_authenticator as stauth

# Generate hashed password
hashed_passwords = stauth.Hasher(['new_password']).generate()
print(hashed_passwords[0])  # Use this in the config file
```

Then add the user to the config:

```yaml
credentials:
  usernames:
    new_user:
      name: New User Name
      password: <hashed_password_from_above>
      email: newuser@example.com
```

## Integration with Streamlit Pages

### Landing Page (Home.py)
No authentication required - public access.

### Protected Pages (e.g., ATS Scorer)
```python
import streamlit as st
from utils.auth import require_authentication, display_user_info, logout_button

# Protect the page
require_authentication()

# Page content
st.title("🎯 ATS Resume Scorer")

# Sidebar with user info and logout
display_user_info(location='sidebar')
logout_button(location='sidebar')
```

## Troubleshooting

### Issue: "Module 'streamlit_authenticator' not found"
**Solution**: Install the package: `pip install streamlit-authenticator>=0.2.3`

### Issue: Login form not appearing
**Solution**: Make sure you're calling `login()` or `require_authentication()` in your page.

### Issue: Session expires too quickly
**Solution**: Adjust the `max_inactive_minutes` parameter in `check_session_expiration()` or increase `expiry_days` in the config file.

### Issue: Can't log in with default credentials
**Solution**: Delete the `config/credentials.yaml` file and restart the app to regenerate default users.

## Example: Complete Protected Page

```python
import streamlit as st
from utils.auth import require_authentication, display_user_info, logout_button

# Configure page
st.set_page_config(
    page_title="ATS Scorer",
    page_icon="🎯",
    layout="wide"
)

# Require authentication
require_authentication("Please log in to access the ATS Resume Scorer.")

# Main content
st.title("🎯 ATS Resume Scorer")
st.write("Welcome to the ATS Resume Scorer!")

# File upload
uploaded_file = st.file_uploader("Upload your resume", type=['pdf', 'docx', 'doc'])

if uploaded_file:
    st.success("File uploaded successfully!")
    # Process the file...

# Sidebar
with st.sidebar:
    st.title("Navigation")
    display_user_info(location='sidebar')
    logout_button(location='sidebar')
```

## Testing

The authentication module can be tested with the default demo users:
- Username: `demo_user`, Password: `demo123`
- Username: `test_user`, Password: `test123`

For automated testing, you can programmatically set session state:

```python
import streamlit as st

# Simulate authenticated session
st.session_state['authentication_status'] = True
st.session_state['name'] = 'Test User'
st.session_state['username'] = 'test_user'
```
