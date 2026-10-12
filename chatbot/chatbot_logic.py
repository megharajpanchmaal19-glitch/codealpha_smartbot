import re

MAX_MESSAGE_LENGTH = 500

DEFAULT_UNKNOWN_RESPONSE = "Sorry, I didn't understand that. Please try another message."

RULES = [
    {
        'intent': 'greeting',
        'triggers': [
            'hello', 'hi', 'hey', 'greetings', 'good morning',
            'good afternoon', 'good evening', 'hello bot', 'hi there'
        ],
        'response': "Hi! Welcome to SmartBot. How can I help you?"
    },
    {
        'intent': 'status',
        'triggers': [
            'how are you', 'how are you doing', 'how do you do',
            'how r u', 'how is it going', 'are you okay'
        ],
        'response': "I'm fine, thanks! How can I help you today?"
    },
    {
        'intent': 'capabilities',
        'triggers': [
            'what can you do', 'what can u do', 'features',
            'what are your capabilities', 'what do you do', 'help me understand'
        ],
        'response': "I can respond to greetings, answer basic questions, and help you explore my features."
    },
    {
        'intent': 'help',
        'triggers': [
            'help', 'support', 'commands', 'options', 'what can i say'
        ],
        'response': "You can say hello, ask how I am, ask what I can do, or say bye."
    },
    {
        'intent': 'farewell',
        'triggers': [
            'bye', 'goodbye', 'see you', 'see ya', 'farewell', 'good night', 'cya'
        ],
        'response': "Goodbye! Have a great day!"
    },
    {
        'intent': 'identity',
        'triggers': [
            'who are you', 'what is your name', 'what is your title', 'who made you'
        ],
        'response': "I am SmartBot Assistant, a rule-based AI chatbot built with Django and MySQL."
    },
    {
        'intent': 'gratitude',
        'triggers': [
            'thank you', 'thanks', 'thx', 'appreciate it', 'thank you very much'
        ],
        'response': "You're very welcome! Feel free to ask if you need anything else."
    },
]


def normalize_text(text: str) -> str:

    if not text:
        return ""
    cleaned = text.strip().lower()
    cleaned = re.sub(r'\s+', ' ', cleaned)
    cleaned = re.sub(r'^[^\w]+|[^\w]+$', '', cleaned)
    return cleaned


def validate_user_message(raw_message: str):

    if raw_message is None:
        return False, "Message is missing.", ""

    trimmed = raw_message.strip()

    if not trimmed:
        return False, "Message cannot be empty or contain only whitespace.", ""

    if len(raw_message) > MAX_MESSAGE_LENGTH:
        return False, f"Message exceeds maximum allowed length of {MAX_MESSAGE_LENGTH} characters.", ""

    normalized = normalize_text(trimmed)
    return True, "", normalized


def get_bot_response(user_message: str) -> str:

    is_valid, _, normalized = validate_user_message(user_message)
    if not is_valid:
        return DEFAULT_UNKNOWN_RESPONSE

    # Step 1: Check for exact trigger matches first
    for rule in RULES:
        for trigger in rule['triggers']:
            if normalized == trigger:
                return rule['response']

    # Step 2: Check for phrase/keyword boundary matches
    for rule in RULES:
        for trigger in rule['triggers']:
            pattern = r'\b' + re.escape(trigger) + r'\b'
            if re.search(pattern, normalized):
                return rule['response']

    # Step 3: Default fallback response
    return DEFAULT_UNKNOWN_RESPONSE
