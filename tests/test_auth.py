from gfuncs import auth


def test_info():
    """Test that info is printed correctly."""
    auth.info()


def test_service_gmail():
    """Test that Gmail service is created correctly."""
    auth.service("gmail")


def test_service_drive():
    """Test that Drive service is created correctly."""
    auth.service("drive")


def test_username():
    """Test that the username is returned correctly."""
    username = auth.username()
    assert isinstance(username, str)
    assert "@" in username
    assert "." in username
