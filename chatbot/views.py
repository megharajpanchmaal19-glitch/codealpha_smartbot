import json
import logging
from django.shortcuts import render
from django.http import JsonResponse, HttpResponseNotAllowed
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import ensure_csrf_cookie
from django.db import connection, DatabaseError

from .models import ChatMessage
from .chatbot_logic import get_bot_response, validate_user_message

logger = logging.getLogger(__name__)


def ensure_session(request):
    if not request.session.session_key:
        request.session.create()
    return request.session.session_key


@ensure_csrf_cookie
def index(request):
    ensure_session(request)
    return render(request, 'chatbot/index.html')


@require_http_methods(["POST"])
def chat_api(request):
    try:
        # 1. Parse JSON request body
        try:
            body = json.loads(request.body.decode('utf-8'))
        except (json.JSONDecodeError, UnicodeDecodeError):
            return JsonResponse(
                {'error': 'Invalid JSON format in request body.'},
                status=400
            )

        raw_message = body.get('message')

        # 2. Server-side validation
        is_valid, validation_error, _ = validate_user_message(raw_message)
        if not is_valid:
            return JsonResponse({'error': validation_error}, status=400)

        # 3. Retrieve user session key
        session_key = ensure_session(request)
        user_message_clean = raw_message.strip()

        # 4. Generate rule-based bot response
        bot_response = get_bot_response(user_message_clean)

        # 5. Persist both user and bot messages to MySQL using Django ORM
        try:
            ChatMessage.objects.create(
                session_key=session_key,
                sender=ChatMessage.SENDER_USER,
                message=user_message_clean
            )
            ChatMessage.objects.create(
                session_key=session_key,
                sender=ChatMessage.SENDER_BOT,
                message=bot_response
            )
        except DatabaseError as db_err:
            logger.error(f"Database error saving chat message: {db_err}")
            return JsonResponse(
                {
                    'error': 'Database error while saving conversation. Please verify MySQL service in XAMPP.',
                    'details': 'Database connection failed.'
                },
                status=500
            )

        # 6. Return response payload
        return JsonResponse({
            'user_message': user_message_clean,
            'bot_response': bot_response
        }, status=200)

    except Exception as exc:
        logger.exception("Unexpected server error in chat_api")
        return JsonResponse(
            {'error': 'An internal server error occurred. Please try again later.'},
            status=500
        )


@require_http_methods(["GET"])
def history_api(request):
    try:
        session_key = request.session.session_key
        if not session_key:
            return JsonResponse({'messages': []}, status=200)


        records = ChatMessage.objects.filter(session_key=session_key).order_by('created_at')
        messages_data = [msg.to_dict() for msg in records]

        return JsonResponse({'messages': messages_data}, status=200)

    except DatabaseError as db_err:
        logger.error(f"Database error fetching chat history: {db_err}")
        return JsonResponse(
            {'error': 'Unable to retrieve chat history from MySQL. Please check XAMPP.'},
            status=500
        )
    except Exception as exc:
        logger.exception("Unexpected error in history_api")
        return JsonResponse(
            {'error': 'Failed to retrieve chat history.'},
            status=500
        )


@require_http_methods(["DELETE"])
def clear_history_api(request):
    try:
        session_key = request.session.session_key
        if not session_key:
            return JsonResponse({
                'status': 'success',
                'message': 'No chat history found for the current session.',
                'deleted_count': 0
            }, status=200)

        deleted_count, _ = ChatMessage.objects.filter(session_key=session_key).delete()

        return JsonResponse({
            'status': 'success',
            'message': 'Chat history cleared successfully.',
            'deleted_count': deleted_count
        }, status=200)

    except DatabaseError as db_err:
        logger.error(f"Database error clearing chat history: {db_err}")
        return JsonResponse(
            {'error': 'Database error while clearing history in MySQL.'},
            status=500
        )
    except Exception as exc:
        logger.exception("Unexpected error in clear_history_api")
        return JsonResponse(
            {'error': 'Failed to clear chat history.'},
            status=500
        )


@require_http_methods(["GET"])
def health_check_api(request):
    db_status = "connected"
    status_code = 200

    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
    except Exception as db_err:
        db_status = f"database_error: {str(db_err)}"
        status_code = 503

    return JsonResponse({
        'status': 'healthy' if status_code == 200 else 'degraded',
        'service': 'SmartBot Assistant Backend',
        'database': db_status
    }, status=status_code)
