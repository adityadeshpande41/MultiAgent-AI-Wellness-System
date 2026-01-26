# Multi-Agent AI Wellness System

A sophisticated AI-powered wellness assistant that uses multiple specialized agents to provide personalized fitness, nutrition, and health guidance. The system features intelligent routing with confidence-based clarification questions and a clean Streamlit interface.

## 🌟 Features

### 🤖 Multi-Agent Architecture
- **Fitness Coach Agent**: Workout routines, exercise guidance, training plans
- **Nutrition Specialist Agent**: Meal planning, calorie information, dietary advice
- **Doctor Avatar Agent**: Health concerns, symptoms, wellness tips
- **Router Agent**: Intelligent query routing with LLM-based confidence scoring
- **Orchestrator**: Coordinates agent workflows and manages conversations

### 🧠 Intelligent Routing System
- **Two-Option Approach**:
  1. **Unrelated Queries**: Polite redirection to wellness topics
  2. **Ambiguous Wellness Queries**: Clarifying questions to determine intent
  3. **Clear Wellness Queries**: Direct routing to appropriate specialist

### 💬 Smart Conversation Flow
- **Confidence-based routing** (70% threshold)
- **Context-aware clarification questions**
- **Conversation state management**
- **Graceful error handling**

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- OpenAI API key

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/your-username/MultiAgent-AI-Wellness-System.git
cd MultiAgent-AI-Wellness-System
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Set up environment variables**
Create a `.env` file in the root directory:
```env
OPENAI_API_KEY=your_openai_api_key_here
CHAT_MODEL=gpt-4o-mini
EMBEDDING_MODEL=text-embedding-3-small
```

4. **Run the application**

**Option A: Simple Chat Interface (Recommended for testing)**
```bash
streamlit run app/main_streamlit_simple.py
```

**Option B: Full Application (with database features)**
```bash
streamlit run app/main_streamlit.py
```

## 🧪 Testing the System

### Test Cases for Two-Option Routing

**🚫 Unrelated Queries** (should get polite redirection):
- "What is the color of the sky?"
- "What time is it?"
- "Tell me a joke"
- "How's the weather?"

**❓ Ambiguous Wellness Queries** (should ask clarifying questions):
- "I feel bad"
- "I have no energy"
- "I want to improve"
- "I'm struggling"
- "Something is wrong with me"

**✅ Clear Wellness Queries** (should route directly):
- "How many calories in pizza?" → Nutrition
- "I have a headache" → Health
- "I want to start working out" → Fitness
- "Show me my progress" → Tracking

## 📁 Project Structure

```
MultiAgent-AI-Wellness-System/
├── agents/                     # AI agent modules
│   ├── orchestrator.py        # Main workflow coordinator
│   ├── router.py              # LLM-based intelligent routing
│   ├── clarification_agent.py # Handles ambiguous queries
│   ├── fitness_coach.py       # Fitness guidance agent
│   ├── nutrition_specialist.py # Nutrition advice agent
│   ├── doctor_avatar.py       # Health consultation agent
│   ├── tracking_viz.py        # Progress tracking agent
│   ├── general_agent.py       # Out-of-domain handler
│   └── api_tool_agent.py      # External API integration
├── app/                       # Streamlit applications
│   ├── main_streamlit.py      # Full application
│   ├── main_streamlit_simple.py # Simple chat interface
│   └── config.py              # Configuration settings
├── tools/                     # Utility modules
│   ├── db.py                  # Database models
│   ├── rag.py                 # RAG search functionality
│   ├── nutrition_calculator.py # Nutrition calculations
│   ├── profile_analyzer.py    # User profile analysis
│   └── safety.py              # Safety checks
├── data/                      # Data storage
│   ├── embeddings.index       # FAISS vector index
│   ├── meta.json             # Metadata
│   └── seed_docs/            # Knowledge base documents
├── requirements.txt           # Python dependencies
└── README.md                 # This file
```

## 🔧 Configuration

### Environment Variables
- `OPENAI_API_KEY`: Your OpenAI API key (required)
- `CHAT_MODEL`: OpenAI model for conversations (default: gpt-4o-mini)
- `EMBEDDING_MODEL`: Model for embeddings (default: text-embedding-3-small)
- `DB_URL`: Database URL (default: sqlite:///./app.db)

### Confidence Threshold
Adjust the confidence threshold in `agents/router.py`:
```python
self.confidence_threshold = 0.70  # 70% confidence threshold
```

## 🏗️ Architecture

### Agent Communication Flow
```
User Input → Router Agent → Confidence Analysis → Decision:
├── High Confidence (≥70%) → Direct Agent Routing
├── Low Confidence + Wellness → Clarification Questions
└── Low Confidence + Non-Wellness → Polite Redirection
```

### Key Components

1. **Router Agent**: Uses LLM to analyze queries and assign confidence scores
2. **Orchestrator**: Manages the overall conversation flow and agent coordination
3. **Specialized Agents**: Domain-specific agents for fitness, nutrition, and health
4. **Clarification System**: Handles ambiguous queries with intelligent follow-up questions

## 🛠️ Development

### Adding New Agents
1. Create agent class in `agents/` directory
2. Implement `respond()` method
3. Add agent to orchestrator's agent mapping
4. Update router categories if needed

### Customizing Routing
- Modify confidence threshold in `router.py`
- Adjust LLM prompts for different routing behavior
- Add new categories to the routing system

## 🔒 Error Handling

The system includes robust error handling for:
- Missing database connections
- FAISS index unavailability
- OpenAI API failures
- Network connectivity issues

All agents gracefully degrade functionality when dependencies are unavailable.

## 📊 Features Overview

### Core Capabilities
- ✅ Multi-agent conversation routing
- ✅ Confidence-based decision making
- ✅ Context-aware clarification
- ✅ Graceful error handling
- ✅ Clean conversation interface
- ✅ Extensible architecture

### Optional Features (Full App)
- 📊 User profile management
- 🍽️ Meal logging and tracking
- 🏋️ Workout logging and analytics
- 📈 Progress visualization
- 💾 SQLite database storage

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- OpenAI for providing the language models
- Streamlit for the web interface framework
- FAISS for vector similarity search
- SQLModel for database management

---

**Ready to test?** Run `streamlit run app/main_streamlit_simple.py` and try the test cases above!