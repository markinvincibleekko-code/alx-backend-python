# messaging_app/chats/filters.py

import django_filters
from django.contrib.auth import get_user_model
from .models import Message, Conversation

User = get_user_model()


class MessageFilter(django_filters.FilterSet):
    """
    Filter class for Message model.
    Allows filtering messages by:
    - Sender (user ID or username)
    - Conversation
    - Date range (sent_at)
    - Message content (search)
    """
    # Filter by sender username
    sender_username = django_filters.CharFilter(
        field_name='sender__username',
        lookup_expr='icontains',
        label='Sender Username'
    )
    
    # Filter by sender ID
    sender_id = django_filters.NumberFilter(
        field_name='sender__id',
        label='Sender ID'
    )
    
    # Filter by conversation ID
    conversation_id = django_filters.UUIDFilter(
        field_name='conversation__conversation_id',
        label='Conversation ID'
    )
    
    # Filter messages within a time range
    sent_at_after = django_filters.DateTimeFilter(
        field_name='sent_at',
        lookup_expr='gte',
        label='Sent After'
    )
    
    sent_at_before = django_filters.DateTimeFilter(
        field_name='sent_at',
        lookup_expr='lte',
        label='Sent Before'
    )
    
    # Date range filter
    sent_at_range = django_filters.DateFromToRangeFilter(
        field_name='sent_at',
        label='Sent Date Range'
    )
    
    # Filter by message content
    message_body = django_filters.CharFilter(
        field_name='message_body',
        lookup_expr='icontains',
        label='Message Content'
    )
    
    # Filter by read status
    is_read = django_filters.BooleanFilter(
        field_name='is_read',
        label='Is Read'
    )
    
    class Meta:
        model = Message
        fields = [
            'sender_username',
            'sender_id',
            'conversation_id',
            'sent_at_after',
            'sent_at_before',
            'sent_at_range',
            'message_body',
            'is_read'
        ]


class ConversationFilter(django_filters.FilterSet):
    """
    Filter class for Conversation model.
    Allows filtering conversations by:
    - Participants (user ID or username)
    - Date range (created_at)
    """
    # Filter by participant username
    participant_username = django_filters.CharFilter(
        field_name='participants__username',
        lookup_expr='icontains',
        label='Participant Username'
    )
    
    # Filter by participant ID
    participant_id = django_filters.NumberFilter(
        field_name='participants__id',
        label='Participant ID'
    )
    
    # Filter conversations created after a certain date
    created_at_after = django_filters.DateTimeFilter(
        field_name='created_at',
        lookup_expr='gte',
        label='Created After'
    )
    
    # Filter conversations created before a certain date
    created_at_before = django_filters.DateTimeFilter(
        field_name='created_at',
        lookup_expr='lte',
        label='Created Before'
    )
    
    # Date range filter for creation date
    created_at_range = django_filters.DateFromToRangeFilter(
        field_name='created_at',
        label='Created Date Range'
    )
    
    # Filter by updated date
    updated_at_after = django_filters.DateTimeFilter(
        field_name='updated_at',
        lookup_expr='gte',
        label='Updated After'
    )
    
    updated_at_before = django_filters.DateTimeFilter(
        field_name='updated_at',
        lookup_expr='lte',
        label='Updated Before'
    )
    
    class Meta:
        model = Conversation
        fields = [
            'participant_username',
            'participant_id',
            'created_at_after',
            'created_at_before',
            'created_at_range',
            'updated_at_after',
            'updated_at_before'
        ]