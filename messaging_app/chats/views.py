from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth.models import User
from django.db.models import Q
from .models import Conversation, Message
from .serializers import (
    ConversationSerializer, 
    MessageSerializer, 
    ConversationCreateSerializer,
    UserSerializer
)
from .permissions import IsParticipantOfConversation
from .filters import MessageFilter


class ConversationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing conversations.
    Only participants can view and access conversations.
    """
    permission_classes = [IsAuthenticated, IsParticipantOfConversation]
    
    def get_queryset(self):
        """
        Users can only see conversations they are part of
        """
        return Conversation.objects.filter(participants=self.request.user).distinct()
    
    def get_serializer_class(self):
        if self.action == 'create':
            return ConversationCreateSerializer
        return ConversationSerializer
    
    def perform_create(self, serializer):
        """
        Create conversation and ensure current user is added as participant
        """
        serializer.save()

    def retrieve(self, request, *args, **kwargs):
        """
        Override retrieve to ensure permission check on the object
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def messages(self, request, pk=None):
        """
        Custom action to get messages for a specific conversation
        """
        conversation = self.get_object()
        messages = conversation.messages.all()
        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def my_conversations(self, request):
        """
        Custom action to get all conversations for the current user
        """
        conversations = self.get_queryset()
        serializer = self.get_serializer(conversations, many=True)
        return Response(serializer.data)


class MessageViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing messages.
    Only participants of the conversation can view messages.
    Only the sender can update/delete their own messages.
    """
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated, IsParticipantOfConversation]
    filter_backends = [DjangoFilterBackend]
    filterset_class = MessageFilter
    
    def get_queryset(self):
        """
        Users can only see messages from conversations they are part of
        """
        return Message.objects.filter(conversation__participants=self.request.user).select_related('sender', 'conversation')
    
    def perform_create(self, serializer):
        """
        Ensure the sender is set to current user and validate participation
        """
        conversation = serializer.validated_data['conversation']
        
        # Double-check that user is a participant of the conversation
        if not conversation.participants.filter(id=self.request.user.id).exists():
            return Response(
                {"detail": "You are not a participant of this conversation."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer.save(sender=self.request.user)

    def perform_update(self, serializer):
        """
        Ensure only the message sender can update their message
        """
        message = self.get_object()
        if message.sender != self.request.user:
            return Response(
                {"detail": "You can only edit your own messages."},
                status=status.HTTP_403_FORBIDDEN
            )
        serializer.save()

    def perform_destroy(self, instance):
        """
        Ensure only the message sender can delete their message
        """
        if instance.sender != self.request.user:
            return Response(
                {"detail": "You can only delete your own messages."},
                status=status.HTTP_403_FORBIDDEN
            )
        instance.delete()

    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        """
        Custom action to mark a message as read
        """
        message = self.get_object()
        if request.user in message.conversation.participants.all():
            message.is_read = True
            message.save()
            return Response({"status": "message marked as read"})
        return Response(
            {"detail": "You are not a participant of this conversation."},
            status=status.HTTP_403_FORBIDDEN
        )

    @action(detail=False, methods=['get'])
    def unread(self, request):
        """
        Custom action to get all unread messages for the current user
        """
        unread_messages = self.get_queryset().filter(
            conversation__participants=request.user,
            is_read=False
        ).exclude(sender=request.user)  # Exclude messages sent by the user themselves
        
        page = self.paginate_queryset(unread_messages)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(unread_messages, many=True)
        return Response(serializer.data)


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing users.
    Only authenticated users can view the user list.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """
        Optionally filter users by search query
        """
        queryset = User.objects.all()
        username = self.request.query_params.get('username', None)
        if username is not None:
            queryset = queryset.filter(username__icontains=username)
        return queryset