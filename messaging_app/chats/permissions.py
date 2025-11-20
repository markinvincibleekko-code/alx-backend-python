# messaging_app/chats/permissions.py

from rest_framework import permissions


class IsParticipantOfConversation(permissions.BasePermission):
    """
    Custom permission to only allow participants of a conversation to access it.
    This permission ensures:
    - Only authenticated users can access the API
    - Only participants can send, view, update, and delete messages
    """
    
    def has_permission(self, request, view):
        """
        Check if user is authenticated before accessing any view.
        """
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        """
        Check if user is a participant of the conversation.
        Works for both Conversation and Message objects.
        """
        # If the object is a Conversation
        if hasattr(obj, 'participants'):
            return request.user in obj.participants.all()
        
        # If the object is a Message, check the conversation's participants
        if hasattr(obj, 'conversation'):
            return request.user in obj.conversation.participants.all()
        
        # If the object has a sender field (Message model)
        if hasattr(obj, 'sender'):
            # User must be either the sender or a participant in the conversation
            return (obj.sender == request.user or 
                    request.user in obj.conversation.participants.all())
        
        return False


class IsMessageSender(permissions.BasePermission):
    """
    Custom permission to only allow the message sender to update or delete it.
    Viewing is allowed for all conversation participants.
    """
    
    def has_permission(self, request, view):
        """
        Only authenticated users can access messages.
        """
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        """
        - Read permissions: any participant in the conversation
        - Write/Delete permissions: only the message sender
        """
        # For safe methods (GET, HEAD, OPTIONS), check if user is a participant
        if request.method in permissions.SAFE_METHODS:
            if hasattr(obj, 'conversation'):
                return request.user in obj.conversation.participants.all()
        
        # For unsafe methods (PUT, PATCH, DELETE), check if user is the sender
        if hasattr(obj, 'sender'):
            return obj.sender == request.user
        
        return False


class IsConversationParticipant(permissions.BasePermission):
    """
    Permission to check if user is a participant in the conversation.
    Used for conversation-level operations.
    """
    
    def has_permission(self, request, view):
        """
        Only authenticated users can access conversations.
        """
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        """
        User must be a participant of the conversation.
        """
        if hasattr(obj, 'participants'):
            return request.user in obj.participants.all()
        return False