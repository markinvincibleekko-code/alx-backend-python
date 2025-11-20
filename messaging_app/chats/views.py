from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth.models import User
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
    serializer_class = ConversationSerializer
    permission_classes = [IsParticipantOfConversation]
    
    def get_queryset(self):
        # Users can only see conversations they are part of
        return Conversation.objects.filter(participants=self.request.user)
    
    def get_serializer_class(self):
        if self.action == 'create':
            return ConversationCreateSerializer
        return ConversationSerializer
    
    def perform_create(self, serializer):
        serializer.save()

class MessageViewSet(viewsets.ModelViewSet):
    serializer_class = MessageSerializer
    permission_classes = [IsParticipantOfConversation]
    filter_backends = [DjangoFilterBackend]
    filterset_class = MessageFilter
    
    def get_queryset(self):
        # Users can only see messages from conversations they are part of
        return Message.objects.filter(conversation__participants=self.request.user)
    
    def perform_create(self, serializer):
        conversation = serializer.validated_data['conversation']
        # Check if user is participant of the conversation
        if self.request.user not in conversation.participants.all():
            raise PermissionError("You are not a participant of this conversation")
        serializer.save(sender=self.request.user)

class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer