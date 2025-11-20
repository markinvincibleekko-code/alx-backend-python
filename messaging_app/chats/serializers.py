# messaging_app/chats/serializers.py

from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Conversation, Message

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for User model (basic info).
    """
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
        read_only_fields = ['id']


class MessageSerializer(serializers.ModelSerializer):
    """
    Serializer for Message model.
    """
    sender = UserSerializer(read_only=True)
    sender_id = serializers.IntegerField(write_only=True, required=False)
    
    class Meta:
        model = Message
        fields = [
            'message_id',
            'conversation',
            'sender',
            'sender_id',
            'message_body',
            'sent_at',
            'updated_at',
            'is_read'
        ]
        read_only_fields = ['message_id', 'sender', 'sent_at', 'updated_at']
    
    def validate(self, data):
        """
        Validate that the sender is a participant in the conversation.
        """
        request = self.context.get('request')
        conversation = data.get('conversation')
        
        if request and conversation:
            if request.user not in conversation.participants.all():
                raise serializers.ValidationError(
                    "You must be a participant in the conversation to send messages."
                )
        
        return data


class ConversationSerializer(serializers.ModelSerializer):
    """
    Serializer for Conversation model.
    """
    participants = UserSerializer(many=True, read_only=True)
    participant_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )
    last_message = MessageSerializer(read_only=True)
    message_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Conversation
        fields = [
            'conversation_id',
            'participants',
            'participant_ids',
            'created_at',
            'updated_at',
            'last_message',
            'message_count'
        ]
        read_only_fields = ['conversation_id', 'created_at', 'updated_at']
    
    def get_message_count(self, obj):
        """
        Get the total number of messages in the conversation.
        """
        return obj.messages.count()
    
    def create(self, validated_data):
        """
        Create a new conversation with participants.
        """
        participant_ids = validated_data.pop('participant_ids', [])
        conversation = Conversation.objects.create()
        
        # Add participants
        if participant_ids:
            users = User.objects.filter(id__in=participant_ids)
            conversation.participants.set(users)
        
        return conversation
    
    def update(self, instance, validated_data):
        """
        Update conversation participants.
        """
        participant_ids = validated_data.pop('participant_ids', None)
        
        if participant_ids is not None:
            users = User.objects.filter(id__in=participant_ids)
            instance.participants.set(users)
        
        instance.save()
        return instance