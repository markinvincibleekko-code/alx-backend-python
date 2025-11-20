# messaging_app/chats/auth.py
from rest_framework.authentication import SessionAuthentication

class CustomSessionAuthentication(SessionAuthentication):
    """
    Custom session authentication to handle CSRF for session auth
    while allowing JWT to work without CSRF.
    """
    def enforce_csrf(self, request):
        # Skip CSRF for API requests when using JWT
        if request.path.startswith('/api/'):
            return
        return super().enforce_csrf(request)