# Mental Health Support Chatbot

A supportive AI chatbot designed to provide empathetic conversation and support for mental health and addiction recovery. This enhanced version includes PostgreSQL database integration for conversation history, user-specific analysis, and contextual AI responses.

## 🚀 Features

### Core Features
- **Empathetic AI Responses**: Powered by Google Gemini 2.0 Flash for warm, supportive conversations
- **User-Specific Conversations**: Persistent storage with user_id for personalized experiences
- **Conversation History**: Track all conversations per user
- **Contextual Analysis**: AI analyzes previous messages to provide personalized responses
- **User Sentiment Tracking**: Monitors individual user sentiment trends over time
- **Crisis Detection**: Identifies crisis keywords and provides appropriate resources
- **Topic Analysis**: Tracks common discussion topics for better context
- **Multi-User Support**: Complete isolation and personalization per user

### Technical Features
- **FastAPI Backend**: Modern, fast API framework with automatic documentation
- **PostgreSQL Database**: Robust data storage with SQLAlchemy ORM and user indexing
- **User-Specific Management**: Complete user isolation with efficient database queries
- **Real-time Analysis**: Immediate message analysis for response tailoring
- **Health Monitoring**: Built-in health checks and logging
- **Database Indexing**: Optimized queries with composite indexes for user_id

## 📋 Prerequisites

- Python 3.8+
- PostgreSQL database
- Google Gemini API key

## 🛠️ Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd mental-health-chatbot
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   Create a `.env` file in the root directory:
   ```env
   # Gemini AI API Key
   GEMINI_API_KEY=your_gemini_api_key_here
   
   # PostgreSQL Database Configuration
   DATABASE_URL=postgresql://username:password@localhost:5432/chatbot_db
   ```

4. **Set up the database**
   ```bash
   python setup_database.py
   # If upgrading from a previous version, run:
   python migrate_database.py
   ```

5. **Run the application**
   ```bash
   python main.py
   ```

The API will be available at `http://localhost:8000`

## 📚 API Endpoints

### Chat Endpoint
- **POST** `/chat`
  - Send a message and receive a contextual response
  - Request body:
    ```json
    {
      "message": "I'm feeling anxious today",
      "user_id": "user123"
    }
    ```
  - Response:
    ```json
    {
      "response": "It's okay to feel anxious. Remember to take deep breaths and be kind to yourself.\nWould you like to talk more about what's making you feel this way?",
      "response_html": "It's okay to feel anxious. Remember to take deep breaths and be kind to yourself.<br>Would you like to talk more about what's making you feel this way?",
      "user_id": "user123",
      "message_id": 42,
      "context_analysis": {
        "user_id": "user123",
        "total_messages": 15,
        "engagement_level": "medium",
        "sentiment_trend": "negative",
        "common_topics": ["anxiety", "stress", "work"],
        "current_message_analysis": {
          "is_crisis": false,
          "urgency_level": "low",
          "is_negative": true,
          "message_length": 25,
          "has_question": false
        }
      }
    }
    ```

#### Response Formatting
- `response`: The raw text, with `\n` for newlines (for plain text or chat apps)
- `response_html`: The same text, but with `\n` replaced by `<br>` for easy HTML/web display

**Frontend best practices:**
- For web: Render `response_html` as HTML (e.g., `dangerouslySetInnerHTML` in React, or `v-html` in Vue)
- For mobile: Split `response` on `\n` and display as separate lines or paragraphs
- For chat apps: Use `response` as-is, most chat UIs handle `\n` as newlines

### Conversation History
- **GET** `/conversation/{user_id}/history?limit=20`
  - Retrieve conversation history for a specific user

### User Analysis
- **GET** `/user/{user_id}/analysis`
  - Get comprehensive analysis of user's conversation patterns and sentiment

### User Summary
- **GET** `/user/{user_id}/summary`
  - Get a summary of all user's conversations and patterns

### Health Check
- **GET** `/health`
  - Check API health status

## 🧑‍💻 Displaying AI Responses in Your Frontend

- **Web (HTML/React/Vue):**
  - Use the `response_html` field and render as HTML for proper line breaks.
  - Example (React):
    ```jsx
    <div dangerouslySetInnerHTML={{ __html: response_html }} />
    ```
  - Example (Vue):
    ```html
    <div v-html="response_html"></div>
    ```
- **Mobile (React Native/Flutter):**
  - Split the `response` string on `\n` and render each line as a separate `<Text>` or widget.
- **Chat Apps:**
  - Use the `response` field; most chat UIs will display `\n` as newlines.

## 🧠 AI Features

- Contextual, empathetic responses
- User-specific sentiment and topic analysis
- Crisis detection and support
- Personalized engagement tracking

## 🚨 Crisis Support

The chatbot includes built-in crisis detection and will automatically provide:
- National Suicide Prevention Lifeline: 988 or 1-800-273-8255
- Crisis Text Line: Text HOME to 741741
- Emergency services information

## 📊 Monitoring and Logging

- Comprehensive logging of all user interactions
- User-specific error tracking and reporting
- Performance monitoring per user
- Crisis detection alerts with user identification
- Database query optimization monitoring

## 🔒 Security Considerations

- Complete user data isolation with user_id
- No sensitive data is stored in plain text
- Database connections use environment variables
- API responses are sanitized
- Crisis detection logs are maintained for safety
- User-specific conversation boundaries

## 🧪 Testing

Test the API using curl or any HTTP client:

```bash
# Send a message for a specific user
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "I need someone to talk to", "user_id": "user123"}'

# Get conversation history for a specific user
curl "http://localhost:8000/conversation/user123/history"

# Get user analysis
curl "http://localhost:8000/user/user123/analysis"

# Get user summary
curl "http://localhost:8000/user/user123/summary"

# Run comprehensive tests
python test_api.py
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## ⚠️ Disclaimer

This chatbot is designed to provide supportive conversation and is not a replacement for professional mental health care. Users experiencing crisis should contact emergency services or crisis hotlines immediately. 