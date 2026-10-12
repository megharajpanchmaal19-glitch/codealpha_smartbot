from django.contrib import admin
from .models import ChatMessage


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'session_key_short', 'sender', 'message_snippet', 'created_at')
    list_filter = ('sender', 'created_at')
    search_fields = ('session_key', 'message')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)
    list_per_page = 25

    def session_key_short(self, obj):
        return f"{obj.session_key[:12]}..." if len(obj.session_key) > 12 else obj.session_key
    session_key_short.short_description = "Session"

    def message_snippet(self, obj):
        return (obj.message[:50] + '...') if len(obj.message) > 50 else obj.message
    message_snippet.short_description = "Message"
