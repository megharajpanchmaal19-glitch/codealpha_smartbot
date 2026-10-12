from django.db import models


class ChatMessage(models.Model):
    SENDER_USER = 'User'
    SENDER_BOT = 'Bot'

    SENDER_CHOICES = [
        (SENDER_USER, 'User'),
        (SENDER_BOT, 'Bot'),
    ]

    id = models.BigAutoField(primary_key=True)
    session_key = models.CharField(
        max_length=255,
        db_index=True,
        help_text="Unique session identifier isolating conversations per user."
    )
    sender = models.CharField(
        max_length=10,
        choices=SENDER_CHOICES,
        help_text="Identifies whether the message originated from the User or Bot."
    )
    message = models.TextField(
        max_length=1000,
        help_text="The text payload of the message (max 1000 characters)."
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when the message was recorded."
    )

    class Meta:
        db_table = 'chatbot_chatmessage'
        ordering = ['created_at']
        verbose_name = 'Chat Message'
        verbose_name_plural = 'Chat Messages'

    def __str__(self):
        formatted_time = self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else ''
        snippet = (self.message[:35] + '...') if len(self.message) > 35 else self.message
        return f"[{formatted_time}] {self.sender}: {snippet}"

    def to_dict(self):
        return {
            'id': self.id,
            'session_key': self.session_key,
            'sender': self.sender,
            'message': self.message,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else '',
        }
