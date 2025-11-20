# messaging_app/chats/permissions.py

from rest_framework import permissions

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner of the object.
        return obj.user == request.user


class IsParticipantOfConversation(permissions.BasePermission):
    """
    Custom permission to only allow participants of a conversation to view it.
    """
    def has_object_permission(self, request, view, obj):
        # Check if user is a participant in the conversation
        return request.user in obj.participants.all()


class IsMessageOwner(permissions.BasePermission):
    """
    Custom permission to only allow message owners to view/edit their messages.
    """
    def has_object_permission(self, request, view, obj):
        # Allow read access if user is participant in the conversation
        if request.method in permissions.SAFE_METHODS:
            return request.user in obj.conversation.participants.all()
        
        # Write/Delete permissions only for message sender
        return obj.sender == request.user


class CanAccessOwnData(permissions.BasePermission):
    """
    Ensures users can only access their own messages and conversations.
    """
    def has_permission(self, request, view):
        # Must be authenticated
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        # Check if the object has a 'user' attribute
        if hasattr(obj, 'user'):
            return obj.user == request.user
        
        # Check if the object has 'participants' (like a Conversation model)
        if hasattr(obj, 'participants'):
            return request.user in obj.participants.all()
        
        # Check if the object has 'sender' (like a Message model)
        if hasattr(obj, 'sender'):
            return obj.sender == request.user or \
                   request.user in obj.conversation.participants.all()
        
        return False