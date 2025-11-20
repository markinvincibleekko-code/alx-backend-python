# messaging_app/chats/views.py

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer
from .permissions import IsParticipantOfConversation, IsMessageOwner, CanAccessOwnData


class ConversationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing conversations.
    Users can only see conversations they're part of.
    """
    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated, CanAccessOwnData]
    
    def get_queryset(self):
        """
        Filter conversations to only show those the user participates in.
        """
        return Conversation.objects.filter(participants=self.request.user)
    
    def perform_create(self, serializer):
        """
        Automatically add the creator as a participant.
        """
        conversation = serializer.save()
        conversation.participants.add(self.request.user)
    
    @action(detail=True, methods=['post'])
    def add_participant(self, request, pk=None):
        """
        Add a participant to the conversation.
        Only existing participants can add new ones.
        """
        conversation = self.get_object()
        user_id = request.data.get('user_id')
        
        try:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            user_to_add = User.objects.get(id=user_id)
            conversation.participants.add(user_to_add)
            return Response({'status': 'participant added'})
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found'},
                status=status.HTTP_404_NOT_FOUND
            )


class MessageViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing messages.
    Users can only see messages from their conversations.
    """
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated, IsMessageOwner]
    
    def get_queryset(self):
        """
        Filter messages to only show those from user's conversations.
        """
        user_conversations = Conversation.objects.filter(
            participants=self.request.user
        )
        return Message.objects.filter(conversation__in=user_conversations)
    
    def perform_create(self, serializer):
        """
        Automatically set the sender as the current user.
        """
        serializer.save(sender=self.request.user)
    
    @action(detail=False, methods=['get'])
    def my_messages(self, request):
        """
        Get all messages sent by the current user.
        """
        messages = Message.objects.filter(sender=request.user)
        serializer = self.get_serializer(messages, many=True)
        return Response(serializer.data)