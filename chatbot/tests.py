
import json
from django.test import TestCase, Client
from django.urls import reverse
from .models import ChatMessage
from .chatbot_logic import (
    get_bot_response,
    validate_user_message,
    normalize_text,
    DEFAULT_UNKNOWN_RESPONSE,
    MAX_MESSAGE_LENGTH,
)


class ChatbotLogicUnitTests(TestCase):
    def test_greeting_lowercase(self):
        response = get_bot_response("hello")
        self.assertEqual(response, "Hi! Welcome to SmartBot. How can I help you?")

    def test_greeting_uppercase_case_insensitivity(self):
        response = get_bot_response("HELLO")
        self.assertEqual(response, "Hi! Welcome to SmartBot. How can I help you?")

    def test_greeting_mixed_case_and_punctuation(self):
        response = get_bot_response("  HeLLo!!  ")
        self.assertEqual(response, "Hi! Welcome to SmartBot. How can I help you?")

    def test_how_are_you(self):
        response = get_bot_response("how are you")
        self.assertEqual(response, "I'm fine, thanks! How can I help you today?")

    def test_what_can_you_do(self):
        response = get_bot_response("what can you do")
        self.assertEqual(
            response,
            "I can respond to greetings, answer basic questions, and help you explore my features."
        )

    def test_help(self):
        response = get_bot_response("help")
        self.assertEqual(
            response,
            "You can say hello, ask how I am, ask what I can do, or say bye."
        )

    def test_bye(self):
        response = get_bot_response("bye")
        self.assertEqual(response, "Goodbye! Have a great day!")

    def test_unknown_message(self):
        response = get_bot_response("xyz random gibberish 12345")
        self.assertEqual(response, DEFAULT_UNKNOWN_RESPONSE)

    def test_empty_message_validation(self):
        is_valid, error, _ = validate_user_message("")
        self.assertFalse(is_valid)
        self.assertIn("cannot be empty", error)

    def test_whitespace_only_validation(self):
        is_valid, error, _ = validate_user_message("     ")
        self.assertFalse(is_valid)
        self.assertIn("cannot be empty", error)

    def test_excessive_length_validation(self):
        long_message = "a" * (MAX_MESSAGE_LENGTH + 1)
        is_valid, error, _ = validate_user_message(long_message)
        self.assertFalse(is_valid)
        self.assertIn("exceeds maximum allowed length", error)


class ChatbotAPIIntegrationTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.chat_url = reverse('chatbot:chat_api')
        self.history_url = reverse('chatbot:history_api')
        self.clear_url = reverse('chatbot:clear_history_api')
        self.health_url = reverse('chatbot:health_check_api')

    def test_post_chat_success_hello(self):
        payload = {'message': 'hello'}
        response = self.client.post(
            self.chat_url,
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data.get('user_message'), 'hello')
        self.assertEqual(data.get('bot_response'), "Hi! Welcome to SmartBot. How can I help you?")

        self.assertEqual(ChatMessage.objects.count(), 2)
        user_msg = ChatMessage.objects.filter(sender='User').first()
        bot_msg = ChatMessage.objects.filter(sender='Bot').first()
        self.assertEqual(user_msg.message, 'hello')
        self.assertEqual(bot_msg.message, "Hi! Welcome to SmartBot. How can I help you?")

    def test_post_chat_empty_message_rejected(self):
        payload = {'message': ''}
        response = self.client.post(
            self.chat_url,
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn('error', data)

    def test_post_chat_whitespace_only_rejected(self):
        payload = {'message': '    '}
        response = self.client.post(
            self.chat_url,
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn('error', data)

    def test_post_chat_message_too_long_rejected(self):
        payload = {'message': 'x' * 501}
        response = self.client.post(
            self.chat_url,
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn('error', data)

    def test_get_history_retrieves_chronological_messages(self):
        self.client.post(
            self.chat_url,
            data=json.dumps({'message': 'hello'}),
            content_type='application/json'
        )
        self.client.post(
            self.chat_url,
            data=json.dumps({'message': 'how are you'}),
            content_type='application/json'
        )

        response = self.client.get(self.history_url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        messages = data.get('messages', [])
        self.assertEqual(len(messages), 4)  # 2 user messages + 2 bot responses
        self.assertEqual(messages[0]['sender'], 'User')
        self.assertEqual(messages[0]['message'], 'hello')
        self.assertEqual(messages[1]['sender'], 'Bot')
        self.assertEqual(messages[2]['sender'], 'User')
        self.assertEqual(messages[2]['message'], 'how are you')
        self.assertEqual(messages[3]['sender'], 'Bot')

    def test_delete_clear_history(self):
        # Create message
        self.client.post(
            self.chat_url,
            data=json.dumps({'message': 'hello'}),
            content_type='application/json'
        )
        self.assertEqual(ChatMessage.objects.count(), 2)

        response = self.client.delete(self.clear_url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data.get('status'), 'success')

        history_response = self.client.get(self.history_url)
        self.assertEqual(len(history_response.json().get('messages')), 0)

    def test_session_isolation(self):
        client_a = Client()
        client_b = Client()

        client_a.post(
            self.chat_url,
            data=json.dumps({'message': 'message from client A'}),
            content_type='application/json'
        )

        response_b = client_b.get(self.history_url)
        self.assertEqual(response_b.status_code, 200)
        self.assertEqual(len(response_b.json().get('messages')), 0)

        client_b.post(
            self.chat_url,
            data=json.dumps({'message': 'message from client B'}),
            content_type='application/json'
        )

        response_a = client_a.get(self.history_url)
        self.assertEqual(len(response_a.json().get('messages')), 2)
        self.assertEqual(response_a.json()['messages'][0]['message'], 'message from client A')

        response_b2 = client_b.get(self.history_url)
        self.assertEqual(len(response_b2.json().get('messages')), 2)
        self.assertEqual(response_b2.json()['messages'][0]['message'], 'message from client B')

    def test_health_check_endpoint(self):
        response = self.client.get(self.health_url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('status', data)
        self.assertIn('database', data)
