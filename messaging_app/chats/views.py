# messaging_app/chats/views.py

from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth import get_user_model
from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer
from .permissions import (
    IsParticipantOfConversation,
    IsMessageSender,
    IsConversationParticipant
)
from .filters import MessageFilter, ConversationFilter
from .pagination import MessagePagination, ConversationPagination

User = get_user_model()


class ConversationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing conversations.
    Only participants can view and interact with conversations.
    
    Supports filtering by:
    - participant_username: Filter by participant's username
    - participant_id: Filter by participant's ID
    - created_at_after: Conversations created after this date
    - created_at_before: Conversations created before this date
    """
    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated, IsConversationParticipant]
    pagination_class = ConversationPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ConversationFilter
    search_fields = ['participants__username', 'participants__email']
    ordering_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """
        Return only conversations where the current user is a participant.
        """
        return Conversation.objects.filter(
            participants=self.request.user
        ).distinct().prefetch_related('participants', 'messages')
    
    def perform_create(self, serializer):
        """
        When creating a conversation, automatically add the creator as a participant.
        """
        conversation = serializer.save()
        conversation.participants.add(self.request.user)
    
    @action(detail=True, methods=['post'], permission_classes=[IsConversationParticipant])
    def add_participant(self, request, pk=None):
        """
        Add a new participant to the conversation.
        Only existing participants can add new participants.
        """
        conversation = self.get_object()
        user_id = request.data.get('user_id')
        
        if not user_id:
            return Response(
                {'error': 'user_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            user_to_add = User.objects.get(id=user_id)
            
            # Check if user is already a participant
            if user_to_add in conversation.participants.all():
                return Response(
                    {'message': 'User is already a participant'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            conversation.participants.add(user_to_add)
            return Response(
                {'message': f'User {user_to_add.username} added to conversation'},
                status=status.HTTP_200_OK
            )
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['post'], permission_classes=[IsConversationParticipant])
    def remove_participant(self, request, pk=None):
        """
        Remove a participant from the conversation.
        Only existing participants can remove participants.
        """
        conversation = self.get_object()
        user_id = request.data.get('user_id')
        
        if not user_id:
            return Response(
                {'error': 'user_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            user_to_remove = User.objects.get(id=user_id)
            
            if user_to_remove not in conversation.participants.all():
                return Response(
                    {'error': 'User is not a participant'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            conversation.participants.remove(user_to_remove)
            return Response(
                {'message': f'User {user_to_remove.username} removed from conversation'},
                status=status.HTTP_200_OK
            )
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found'},
                status=status.HTTP_404_NOT_FOUND
            )


class MessageViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing messages.
    Only conversation participants can view messages.
    Only message senders can update/delete their messages.
    
    Features:
    - Pagination: 20 messages per page
    - Filtering by:
        - sender_username: Filter by sender's username
        - sender_id: Filter by sender's ID
        - conversation_id: Filter by conversation
        - sent_at_after: Messages sent after this date
        - sent_at_before: Messages sent before this date
        - sent_at_range: Messages within a date range
        - message_body: Search message content
        - is_read: Filter by read status
    - Search: message_body, sender__username
    - Ordering: sent_at, updated_at
    """
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated, IsParticipantOfConversation, IsMessageSender]
    pagination_class = MessagePagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = MessageFilter
    search_fields = ['message_body', 'sender__username']
    ordering_fields = ['sent_at', 'updated_at']
    ordering = ['sent_at']
    
    def get_queryset(self):
        """
        Return only messages from conversations where the user is a participant.
        Optimized with select_related to reduce database queries.
        """
        user_conversations = Conversation.objects.filter(
            participants=self.request.user
        )
        return Message.objects.filter(
            conversation__in=user_conversations
        ).select_related('sender', 'conversation').order_by('-sent_at')
    
    def perform_create(self, serializer):
        """
        Automatically set the sender as the current user when creating a message.
        Verify user is a participant in the conversation.
        """
        conversation = serializer.validated_data.get('conversation')
        
        # Verify user is a participant in the conversation
        if self.request.user not in conversation.participants.all():
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("You are not a participant in this conversation.")
        
        serializer.save(sender=self.request.user)
    
    @action(detail=False, methods=['get'])
    def my_messages(self, request):
        """
        Get all messages sent by the current user.
        Supports pagination and filtering.
        """
        messages = self.filter_queryset(
            Message.objects.filter(sender=request.user)
        )
        
        page = self.paginate_queryset(messages)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(messages, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def conversation_messages(self, request):
        """
        Get all messages for a specific conversation.
        Requires conversation_id as a query parameter.
        Supports pagination and filtering.
        """
        conversation_id = request.query_params.get('conversation_id')
        
        if not conversation_id:
            return Response(
                {'error': 'conversation_id parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            conversation = Conversation.objects.get(conversation_id=conversation_id)
            
            # Check if user is a participant
            if request.user not in conversation.participants.all():
                return Response(
                    {'error': 'You are not a participant in this conversation'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            messages = self.filter_queryset(
                Message.objects.filter(conversation=conversation)
            )
            
            page = self.paginate_queryset(messages)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            
            serializer = self.get_serializer(messages, many=True)
            return Response(serializer.data)
            
        except Conversation.DoesNotExist:
            return Response(
                {'error': 'Conversation not found'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['get'])
    def unread_messages(self, request):
        """
        Get all unread messages for the current user.
        Supports pagination and filtering.
        """
        user_conversations = Conversation.objects.filter(
            participants=request.user
        )
        messages = self.filter_queryset(
            Message.objects.filter(
                conversation__in=user_conversations,
                is_read=False
            ).exclude(sender=request.user)
        )
        
        page = self.paginate_queryset(messages)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(messages, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def mark_as_read(self, request, pk=None):
        """
        Mark a message as read.
        Only participants in the conversation can mark messages as read.
        """
        message = self.get_object()
        message.is_read = True
        message.save()
        
        serializer = self.get_serializer(message)
        return Response(serializer.data)