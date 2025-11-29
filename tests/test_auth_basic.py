"""
Basic tests for the authentication module.

These tests verify the core functionality of the authentication system
without requiring a full Streamlit environment.

Requirements: 2.1, 2.2, 2.3, 2.4, 2.5
"""

import pytest
import sys
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
import yaml

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.auth import AuthenticationManager


class TestAuthenticationManager:
    """Test suite for AuthenticationManager class"""
    
    @pytest.fixture
    def mock_streamlit(self):
        """Mock streamlit session state"""
        with patch('utils.auth.st') as mock_st:
            # Create a mock session state
            mock_st.session_state = {}
            yield mock_st
    
    @pytest.fixture
    def temp_config_path(self, tmp_path):
        """Create a temporary config path"""
        config_dir = tmp_path / "config"
        config_dir.mkdir()
        return str(config_dir / "credentials.yaml")
    
    def test_init_creates_default_config(self, temp_config_path, mock_streamlit):
        """Test that initialization creates a default config file if it doesn't exist"""
        # Verify config doesn't exist
        assert not Path(temp_config_path).exists()
        
        # Initialize auth manager (should create config)
        with patch('utils.auth.stauth.Authenticate'):
            auth = AuthenticationManager(config_path=temp_config_path)
        
        # Verify config was created
        assert Path(temp_config_path).exists()
        
        # Verify config structure
        with open(temp_config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        assert 'credentials' in config
        assert 'usernames' in config['credentials']
        assert 'cookie' in config
        assert 'demo_user' in config['credentials']['usernames']
        assert 'test_user' in config['credentials']['usernames']
    
    def test_create_session(self, temp_config_path, mock_streamlit):
        """Test session creation stores correct information"""
        with patch('utils.auth.stauth.Authenticate'):
            auth = AuthenticationManager(config_path=temp_config_path)
        
        # Create session
        auth._create_session("Test User", "testuser")
        
        # Verify session state
        assert 'user_name' in mock_streamlit.session_state
        assert 'username' in mock_streamlit.session_state
        assert 'session_created_at' in mock_streamlit.session_state
        assert 'last_activity' in mock_streamlit.session_state
        
        assert mock_streamlit.session_state['user_name'] == "Test User"
        assert mock_streamlit.session_state['username'] == "testuser"
    
    def test_terminate_session(self, temp_config_path, mock_streamlit):
        """Test session termination clears session data"""
        with patch('utils.auth.stauth.Authenticate'):
            auth = AuthenticationManager(config_path=temp_config_path)
        
        # Create session first
        mock_streamlit.session_state['user_name'] = "Test User"
        mock_streamlit.session_state['username'] = "testuser"
        mock_streamlit.session_state['session_created_at'] = datetime.now()
        mock_streamlit.session_state['last_activity'] = datetime.now()
        
        # Terminate session
        auth._terminate_session()
        
        # Verify session data is cleared
        assert 'user_name' not in mock_streamlit.session_state
        assert 'username' not in mock_streamlit.session_state
        assert 'session_created_at' not in mock_streamlit.session_state
        assert 'last_activity' not in mock_streamlit.session_state
    
    def test_is_authenticated_true(self, temp_config_path, mock_streamlit):
        """Test is_authenticated returns True when authenticated"""
        with patch('utils.auth.stauth.Authenticate'):
            auth = AuthenticationManager(config_path=temp_config_path)
        
        # Set authentication status
        mock_streamlit.session_state['authentication_status'] = True
        
        # Verify authentication check
        assert auth.is_authenticated() == True
    
    def test_is_authenticated_false(self, temp_config_path, mock_streamlit):
        """Test is_authenticated returns False when not authenticated"""
        with patch('utils.auth.stauth.Authenticate'):
            auth = AuthenticationManager(config_path=temp_config_path)
        
        # Set authentication status to False
        mock_streamlit.session_state['authentication_status'] = False
        
        # Verify authentication check
        assert auth.is_authenticated() == False
    
    def test_is_authenticated_none(self, temp_config_path, mock_streamlit):
        """Test is_authenticated returns False when status is None"""
        with patch('utils.auth.stauth.Authenticate'):
            auth = AuthenticationManager(config_path=temp_config_path)
        
        # Don't set authentication status (defaults to None)
        
        # Verify authentication check
        assert auth.is_authenticated() == False
    
    def test_check_session_expiration_valid(self, temp_config_path, mock_streamlit):
        """Test session expiration check with valid session"""
        with patch('utils.auth.stauth.Authenticate'):
            auth = AuthenticationManager(config_path=temp_config_path)
        
        # Set up authenticated session with recent activity
        mock_streamlit.session_state['authentication_status'] = True
        mock_streamlit.session_state['last_activity'] = datetime.now()
        
        # Check expiration (should be valid)
        assert auth.check_session_expiration(max_inactive_minutes=60) == True
        
        # Verify last_activity was updated
        assert 'last_activity' in mock_streamlit.session_state
    
    def test_check_session_expiration_expired(self, temp_config_path, mock_streamlit):
        """Test session expiration check with expired session"""
        with patch('utils.auth.stauth.Authenticate'):
            auth = AuthenticationManager(config_path=temp_config_path)
        
        # Set up authenticated session with old activity
        mock_streamlit.session_state['authentication_status'] = True
        mock_streamlit.session_state['last_activity'] = datetime.now() - timedelta(minutes=61)
        
        # Check expiration (should be expired)
        assert auth.check_session_expiration(max_inactive_minutes=60) == False
        
        # Verify authentication status was cleared
        assert mock_streamlit.session_state.get('authentication_status') is None
    
    def test_check_session_expiration_not_authenticated(self, temp_config_path, mock_streamlit):
        """Test session expiration check when not authenticated"""
        with patch('utils.auth.stauth.Authenticate'):
            auth = AuthenticationManager(config_path=temp_config_path)
        
        # Don't set authentication status
        
        # Check expiration (should return False)
        assert auth.check_session_expiration() == False
    
    def test_check_session_expiration_no_activity(self, temp_config_path, mock_streamlit):
        """Test session expiration check with no last_activity"""
        with patch('utils.auth.stauth.Authenticate'):
            auth = AuthenticationManager(config_path=temp_config_path)
        
        # Set authenticated but no last_activity
        mock_streamlit.session_state['authentication_status'] = True
        
        # Check expiration (should return False)
        assert auth.check_session_expiration() == False
    
    def test_default_config_has_correct_structure(self, temp_config_path, mock_streamlit):
        """Test that default config has all required fields"""
        with patch('utils.auth.stauth.Authenticate'):
            auth = AuthenticationManager(config_path=temp_config_path)
        
        # Load config
        with open(temp_config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        # Verify structure
        assert 'credentials' in config
        assert 'usernames' in config['credentials']
        assert 'cookie' in config
        assert 'name' in config['cookie']
        assert 'key' in config['cookie']
        assert 'expiry_days' in config['cookie']
        assert 'preauthorized' in config
        
        # Verify demo users
        usernames = config['credentials']['usernames']
        assert 'demo_user' in usernames
        assert 'test_user' in usernames
        
        # Verify user structure
        for username in ['demo_user', 'test_user']:
            user = usernames[username]
            assert 'name' in user
            assert 'password' in user
            assert 'email' in user
    
    def test_session_creation_timestamp(self, temp_config_path, mock_streamlit):
        """Test that session creation records timestamp"""
        with patch('utils.auth.stauth.Authenticate'):
            auth = AuthenticationManager(config_path=temp_config_path)
        
        before = datetime.now()
        auth._create_session("Test User", "testuser")
        after = datetime.now()
        
        # Verify timestamp is within expected range
        created_at = mock_streamlit.session_state['session_created_at']
        assert before <= created_at <= after
        
        last_activity = mock_streamlit.session_state['last_activity']
        assert before <= last_activity <= after


class TestConvenienceFunctions:
    """Test suite for convenience functions"""
    
    @pytest.fixture
    def mock_streamlit(self):
        """Mock streamlit session state"""
        with patch('utils.auth.st') as mock_st:
            mock_st.session_state = {}
            yield mock_st
    
    def test_get_auth_manager_singleton(self, mock_streamlit):
        """Test that get_auth_manager returns the same instance"""
        from utils.auth import get_auth_manager
        
        with patch('utils.auth.stauth.Authenticate'):
            # Get manager twice
            manager1 = get_auth_manager()
            manager2 = get_auth_manager()
            
            # Should be the same instance
            assert manager1 is manager2
    
    def test_is_authenticated_convenience(self, mock_streamlit):
        """Test is_authenticated convenience function"""
        from utils.auth import is_authenticated
        
        with patch('utils.auth.stauth.Authenticate'):
            # Not authenticated
            assert is_authenticated() == False
            
            # Set authenticated
            mock_streamlit.session_state['authentication_status'] = True
            assert is_authenticated() == True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
