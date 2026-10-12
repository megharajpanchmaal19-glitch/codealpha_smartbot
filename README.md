# 🤖 SmartBot - Basic Rule-Based Chatbot Website

A modern, fully functional, responsive, and user-friendly chatbot web application built with **HTML5, CSS3, Vanilla JavaScript, Python Django Framework**, and **MySQL running in XAMPP**.

---

## 🌟 Key Features

- **Rule-Based Conversational Engine (`chatbot/chatbot_logic.py`)**:
  - Deterministic keyword and phrase recognition.
  - Case-insensitive matching and whitespace normalization.
  - Predefined intents for greetings, status questions, capabilities, help, identity, and farewells.
  - Safe default responses for unrecognized or invalid messages.
  - Server-side validation against empty inputs and excessive message lengths (max 500 chars).
- **Session-Isolated Conversation Memory**:
  - Automatically isolates chat history per visitor using Django sessions.
  - User A cannot view, access, or clear User B's conversation.
- **MySQL Database Persistence via XAMPP**:
  - All user queries and bot replies are stored in the `smartbot_db` MySQL database.
  - Chronological message history retrieval via REST API.
  - Clean `DELETE` endpoint to reset conversation history.
- **Modern, Accessible UI/UX**:
  - Beautiful responsive design for Desktop, Tablet, and Mobile devices.
  - Rounded chat bubbles with separate styling for User (gradient indigo) and Bot (card slate).
  - Animated 3-dot typing indicator.
  - Auto-scrolling to the latest message.
  - Enter key submission and quick prompt buttons (`Hello`, `How are you?`, `What can you do?`, `Help`, `Bye`).
  - XSS-safe DOM rendering using `textContent`.
  - Comprehensive CSRF security protection.

---

## 📂 Project Structure

```text
smart_project/
│
├── manage.py                     # Django administrative management entry point
├── requirements.txt              # Python project dependencies
├── .env.example                  # Environment variables template
├── .env                          # Active local environment settings
├── .gitignore                    # Git exclusions
├── README.md                     # Complete project documentation
│
├── smartbot_project/             # Django project configuration package
│   ├── __init__.py               # Includes PyMySQL fallback hook
│   ├── settings.py               # Django configuration (MySQL, static, sessions)
│   ├── urls.py                   # Master routing table
│   ├── wsgi.py                   # WSGI deployment hook
│   └── asgi.py                   # ASGI asynchronous entry point
│
├── chatbot/                      # Chatbot core application
│   ├── __init__.py
│   ├── apps.py                   # App configuration
│   ├── models.py                 # ChatMessage MySQL database model
│   ├── chatbot_logic.py          # Rule engine (keywords, normalization, responses)
│   ├── views.py                  # API endpoints (/api/chat/, /api/history/, etc.)
│   ├── urls.py                   # Chatbot URL routes
│   ├── admin.py                  # Django Admin model registration
│   ├── tests.py                  # Comprehensive unit & integration test suite
│   └── migrations/               # Database migration schemas
│       ├── __init__.py
│       └── 0001_initial.py
│
├── templates/                    # HTML5 templates
│   └── chatbot/
│       └── index.html            # Main single-page web UI
│
└── static/                       # Static assets
    ├── css/
    │   └── style.css             # Vanilla CSS3 styling & responsive design
    ├── js/
    │   └── script.js             # Vanilla JS Fetch API integration & DOM safety
    └── images/
        └── chatbot.svg           # High-resolution vector mascot & avatar
```

---

## 🔌 API Endpoints Reference

All endpoints return standard JSON responses and enforce appropriate HTTP status codes:

### 1. `POST /api/chat/`
Submits a user message and retrieves the rule-based response.
- **Headers:** `Content-Type: application/json`, `X-CSRFToken: <token>`
- **Request Body:**
  ```json
  {
    "message": "hello"
  }
  ```
- **Response (200 OK):**
  ```json
  {
    "user_message": "hello",
    "bot_response": "Hi! Welcome to SmartBot. How can I help you?"
  }
  ```
- **Error Response (400 Bad Request):**
  ```json
  {
    "error": "Message cannot be empty or contain only whitespace."
  }
  ```

### 2. `GET /api/history/`
Retrieves previous messages for the active session in chronological order.
- **Response (200 OK):**
  ```json
  {
    "messages": [
      {
        "id": 1,
        "session_key": "4f92bc...",
        "sender": "User",
        "message": "hello",
        "created_at": "2026-10-11 12:00:00"
      },
      {
        "id": 2,
        "session_key": "4f92bc...",
        "sender": "Bot",
        "message": "Hi! Welcome to SmartBot. How can I help you?",
        "created_at": "2026-10-11 12:00:01"
      }
    ]
  }
  ```

### 3. `DELETE /api/history/clear/`
Deletes all stored chat messages for the current session from MySQL.
- **Headers:** `X-CSRFToken: <token>`
- **Response (200 OK):**
  ```json
  {
    "status": "success",
    "message": "Chat history cleared successfully.",
    "deleted_count": 2
  }
  ```

### 4. `GET /api/health/`
Verifies backend operational status and database connectivity.
- **Response (200 OK):**
  ```json
  {
    "status": "healthy",
    "service": "SmartBot Assistant Backend",
    "database": "connected"
  }
  ```

---

## 🚀 Setup & Execution Guide (macOS & Windows)

### Prerequisites
- Python 3.9, 3.10, 3.11, or 3.12 installed.
- [XAMPP](https://www.apachefriends.org/) installed on your machine.
- Visual Studio Code or PyCharm.

---

### Step 1: Open Project in VS Code
Open your terminal and navigate to the project directory:
```bash
cd /path/to/smart_project
```
Or open the `smart_project` folder in VS Code (`File > Open Folder...`).

---

### Step 2: Create and Activate Python Virtual Environment

#### On macOS / Linux:
```bash
python3 -m venv venv
source venv/bin/activate
```

#### On Windows (PowerShell / Command Prompt):
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

---

### Step 3: Install Dependencies
Install all required libraries using `pip`:
```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

> **Note on MySQL Drivers:**
> - `mysqlclient` is the default high-performance C driver for Django MySQL.
> - On macOS, if `mysqlclient` encounters header compilation errors during install, install MySQL client libraries via Homebrew:
>   ```bash
>   brew install mysql pkg-config
>   pip install mysqlclient
>   ```
> - **Zero-Config Fallback:** `smartbot_project/__init__.py` includes an automatic `pymysql` hook. If `mysqlclient` cannot be compiled on your system, simply install `pymysql` (`pip install pymysql`) and Django will automatically use it without any configuration changes!

---

### Step 4: Start MySQL in XAMPP

1. Open the **XAMPP Control Panel** (or XAMPP application on macOS).
2. Locate the **MySQL** module.
3. Click the **Start** button next to MySQL.
4. Verify that the MySQL status turns green and is running on port **3306**.

---

### Step 5: Create Database in phpMyAdmin

1. Open your web browser and navigate to:
   ```
   http://localhost/phpmyadmin/
   ```
2. Click on the **New** button on the left sidebar.
3. In the **Database name** field, enter:
   ```
   smartbot_db
   ```
4. Leave the collation as `utf8mb4_general_ci` or default.
5. Click **Create**.

---

### Step 6: Configure Environment Variables

The project includes `.env` and `.env.example`.
Ensure the `.env` file contains your XAMPP settings:
```ini
SECRET_KEY=django-insecure-smartbot-rule-based-chatbot-secret-key-2026
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost

DB_NAME=smartbot_db
DB_USER=root
DB_PASSWORD=
DB_HOST=127.0.0.1
DB_PORT=3306
```
*(Default XAMPP MySQL installations use username `root` with no password `""` on `127.0.0.1:3306`)*

---

### Step 7: Apply Django Migrations

Run Django migrations to create the database tables (including `chatbot_chatmessage` and Django session tables):
```bash
python manage.py makemigrations
python manage.py migrate
```

You can refresh phpMyAdmin to verify that the tables have been created inside `smartbot_db`.

---

### Step 8: (Optional) Create an Admin Superuser
To inspect saved conversations inside Django's administration interface:
```bash
python manage.py createsuperuser
```
Follow the prompts to enter a username and password.

---

### Step 9: Start the Django Development Server

Run the development server:
```bash
python manage.py runserver
```

You will see output similar to:
```text
System check identified no issues (0 silenced).
October 11, 2026 - 12:00:00
Django version 4.2.x, using settings 'smartbot_project.settings'
Starting development server at http://127.0.0.1:8000/
Quit the server with CONTROL-C.
```

---

### Step 10: Open Website in Browser

1. Open your browser and navigate to:
   ```
   http://127.0.0.1:8000/
   ```
2. Click **Start Chatting** or scroll to the Chatbot section.
3. Click the Quick Prompts (`Hello`, `How are you?`, `What can you do?`, `Help`, `Bye`) or type any custom greetings.
4. Refresh the page to verify that your session chat history is preserved!
5. Click **Clear Chat** to test the history deletion.
6. Verify records inside phpMyAdmin by inspecting the `chatbot_chatmessage` table.

---

## 🧪 Running Automated Unit Tests

To execute the unit and integration tests covering chatbot rules, input validations, REST APIs, and session isolation:

```bash
python manage.py test chatbot
```

Expected output:
```text
Found 15 test(s).
Creating test database for alias 'default'...
...............
----------------------------------------------------------------------
Ran 15 tests in 0.420s

OK
Destroying test database for alias 'default'...
```

---

## 🛡️ Security & Best Practices Implemented

1. **Server-Side Validation**: All incoming messages are validated on the backend before processing.
2. **XSS Protection**: User messages are rendered via Vanilla JavaScript using `textContent` and `document.createElement`, avoiding unsafe `innerHTML` assignments.
3. **SQL Injection Prevention**: All database interactions use Django's ORM parameterized queries.
4. **CSRF Protection**: Native Django CSRF tokens are enforced on all `POST` and `DELETE` requests via `X-CSRFToken` request headers.
5. **Session Isolation**: Chat queries are indexed and filtered by unique `session_key` strings, isolating conversations per browser session.
6. **Credential Privacy**: Sensitive database parameters and secret keys are managed through `.env` environment variables.
