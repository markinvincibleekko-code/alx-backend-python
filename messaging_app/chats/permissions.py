# messaging_app/chats/permissions.py
from rest_framework import permissions
from .models import Conversation, Message

class IsParticipantOfConversation(permissions.BasePermission):
    """
    Custom permission to only allow participants of a conversation to access it.
    """
    
    def has_permission(self, request, view):
        # Allow all authenticated users to access the API
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        # Check if the user is a participant in the conversation
        if isinstance(obj, Conversation):
            return request.user in obj.participants.all()
        elif isinstance(obj, Message):
            return request.user in obj.conversation.participants.all()
        return False

class IsMessageSenderOrParticipant(permissions.BasePermission):
    """
    Allow users to delete/edit only their own messages, but view if participant.
    """
    
    def has_object_permission(self, request, view, obj):
        if request.method in ['DELETE', 'PUT', 'PATCH']:
            return obj.sender == request.user
        return request.user in obj.conversation.participants.all()