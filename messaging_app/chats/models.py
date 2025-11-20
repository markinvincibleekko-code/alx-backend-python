# messaging_app/chats/models.py

from django.db import models
from django.contrib.auth import get_user_model
import uuid

User = get_user_model()


class Conversation(models.Model):
    """
    Model representing a conversation between multiple users.
    """
    conversation_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    participants = models.ManyToManyField(
        User,
        related_name='conversations',
        help_text="Users participating in this conversation"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Conversation'
        verbose_name_plural = 'Conversations'
    
    def __str__(self):
        participant_names = ', '.join([user.username for user in self.participants.all()[:3]])
        return f"Conversation {self.conversation_id} - {participant_names}"
    
    @property
    def last_message(self):
        """Get the last message in this conversation."""
        return self.messages.order_by('-sent_at').first()


class Message(models.Model):
    """
    Model representing a message in a conversation.
    """
    message_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name='messages',
        help_text="The conversation this message belongs to"
    )
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sent_messages',
        help_text="The user who sent this message"
    )
    message_body = models.TextField(
        help_text="The content of the message"
    )
    sent_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_read = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['sent_at']
        verbose_name = 'Message'
        verbose_name_plural = 'Messages'
        indexes = [
            models.Index(fields=['-sent_at']),
            models.Index(fields=['conversation', '-sent_at']),
        ]
    
    def __str__(self):
        return f"Message from {self.sender.username} in {self.conversation.conversation_id}"
    
    def save(self, *args, **kwargs):
        """
        Override save to ensure sender is a participant in the conversation.
        """
        if self.sender not in self.conversation.participants.all():
            raise ValueError("Sender must be a participant in the conversation")
        super().save(*args, **kwargs)