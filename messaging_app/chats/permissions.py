from rest_framework import permissions
from .models import Conversation

class IsParticipantOfConversation(permissions.BasePermission):
    """
    Custom permission to only allow participants of a conversation to access it.
    """
    
    def has_object_permission(self, request, view, obj):
        # Check if the user is a participant in the conversation
        if isinstance(obj, Conversation):
            return request.user in obj.participants.all()
        return False