# NeuroTalk - AI-Powered Communication Confidence Platform

![NeuroTalk Banner](https://img.shields.io/badge/NeuroTalk-AI%20Coach-brightgreen)
![Python](https://img.shields.io/badge/Python-3.8+-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.42.0-red)
![License](https://img.shields.io/badge/License-MIT-yellow)

**Tagline:** Talk. Practice. Transform. — Your confidence journey starts now.

---

## 📋 Table of Contents

- [About](#about)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Installation](#installation)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Configuration](#configuration)
- [Screenshots](#screenshots)
- [Contributing](#contributing)
- [Team](#team)
- [License](#license)

---

## 🎯 About

NeuroTalk is an AI-powered communication training platform that helps individuals overcome social anxiety and build conversational confidence through realistic scenario-based practice. Whether preparing for job interviews, networking events, or everyday conversations, NeuroTalk provides a safe, judgment-free environment to develop conversational skills.

Built for **VisionX Hackathon** by **Team HustlerDevs**.

---

## ✨ Features

### 🎭 **Realistic Scenarios**
- Job Interview preparation
- Public Speaking practice
- Casual Conversations
- Networking Events
- Conflict Resolution
- Daily social interactions

### 🤖 **AI-Powered Coach**
- Real-time conversational AI using Google Gemini
- Personalized feedback and scoring (0-10 scale)
- Improved response suggestions
- Adaptive difficulty based on user level

### 📊 **Comprehensive Progress Tracking**
- Session history with detailed analytics
- Average score calculation
- Best score tracking
- Weekly performance charts
- All-time statistics dashboard

### 🔥 **Gamification System**
- **Streak Tracking**: Daily practice streaks with longest streak records
- **XP & Leveling**: Earn experience points with each session
  - Beginner (0-99 XP)
  - Intermediate (100-299 XP)
  - Advanced (300-599 XP)
  - Expert (600+ XP)
- **Achievement System**: Track first and latest responses

### 📈 **Insights & Analytics**
- Focus area recommendations
- Performance trend analysis (improving/steady/dipping)
- Pro tips based on AI feedback
- Weekly score visualization with Plotly charts
- Personalized improvement suggestions

### 📥 **Downloadable Reports**
- Generate comprehensive practice reports
- Export session history
- Track improvement over time
- Share progress with coaches or mentors

---

## 🛠️ Tech Stack

**Frontend:**
- Streamlit 1.42.0
- Custom CSS styling
- Plotly 5.24.1 (for charts)

**Backend:**
- Python 3.8+
- Google Generative AI (Gemini)
- JSON-based data storage

**Authentication:**
- Custom auth system with SHA-256 password hashing
- Session management with Streamlit
- User profile management

**Data Management:**
- JSON file-based database
- Real-time data persistence
- Automated streak tracking

---

## 🚀 Installation

### Prerequisites
- Python 3.8 or higher
- Google API Key (for Gemini AI)
- pip package manager

### Step 1: Clone the Repository
```bash
git clone https://github.com/yourusername/neurotalk.git
cd neurotalk
```

### Step 2: Create Virtual Environment (Recommended)
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Set Up Environment Variables
Create a `.env` file in the root directory:
```env
GOOGLE_API_KEY=your_google_gemini_api_key_here
```

To get your Google API key:
1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Copy and paste it into your `.env` file

### Step 5: Initialize Data Files
The application will automatically create these files on first run:
- `users.json` - User authentication data
- `user_data.json` - Session and practice data

---

## 📖 Usage

### Running the Application
```bash
streamlit run app.py
```

The application will open in your default browser at `http://localhost:8501`

### First-Time User Flow

1. **Sign Up**
   - Enter your name, email, and password
   - Account is created with Beginner level status
   - Redirected to login page

2. **Login**
   - Enter your credentials
   - First-time users see onboarding page
   - Returning users go directly to dashboard

3. **Practice Session**
   - Choose a scenario (Job Interview, Public Speaking, etc.)
   - Interact with AI coach in multiple rounds
   - Receive real-time feedback and scores
   - Get improved response suggestions

4. **Track Progress**
   - View your dashboard with stats
   - Check weekly performance charts
   - Read personalized insights
   - Download comprehensive reports

### User Actions

**Dashboard Features:**
- ✅ Continue Practice - Resume your training
- 🆕 New Scenario - Start fresh with different scenario
- 📊 View All-Time Stats - See complete history
- 📅 Check Weekly Progress - Last 7 days performance
- 💡 Get Insights - Personalized recommendations
- 📥 Download Report - Export your progress

---

## 📁 Project Structure

```
neurotalk/
│
├── app.py                  # Main Streamlit application
├── auth.py                 # User authentication & management
├── data_manager.py         # Session data & analytics
├── prompts.py              # AI prompts & scenario definitions
├── style.css               # Custom CSS styling
│
├── users.json              # User credentials & stats (auto-generated)
├── user_data.json          # Practice sessions data (auto-generated)
│
├── .env                    # Environment variables (create this)
├── .gitignore              # Git ignore file
├── requirements.txt        # Python dependencies
└── README.md               # This file
```

### Key Files Explained

**app.py**
- Main application entry point
- Streamlit UI components
- Session state management
- Page routing logic

**auth.py**
- User registration and login
- Password hashing (SHA-256)
- Streak calculation
- XP and level management
- User stats updates

**data_manager.py**
- Session data storage
- Analytics calculations
- Weekly/all-time stats
- Insights generation
- Report generation

**prompts.py**
- AI system prompts
- Scenario definitions
- Feedback generation logic
- Response improvement prompts

**style.css**
- Custom styling
- Dark theme
- Responsive design
- Card layouts and animations

---

## ⚙️ Configuration

### Scenarios Available

The app comes with pre-configured scenarios:

1. **Job Interview** - Practice interview responses
2. **Public Speaking** - Build presentation confidence
3. **Casual Conversation** - Improve small talk skills
4. **Networking Event** - Master professional introductions
5. **Conflict Resolution** - Handle difficult conversations
6. **Phone Call** - Overcome phone anxiety

### Scoring System

Confidence scores are rated 0-10 based on:
- Clarity and structure
- Confidence level
- Use of filler words
- Eye contact (implied)
- Response relevance
- Professional tone

### XP & Leveling Formula

```python
XP_earned = (rounds * 10) + (avg_score * 5)

Levels:
- Beginner: 0-99 XP
- Intermediate: 100-299 XP
- Advanced: 300-599 XP
- Expert: 600+ XP
```

### Streak Calculation

- Streak increments if practice happens on consecutive days
- Resets to 1 if gap > 1 day
- Longest streak is tracked separately
- Updates on session completion

---

## 📸 Screenshots

*Add screenshots of your application here*

### Login Page
![Login Screenshot](path/to/login.png)

### Dashboard
![Dashboard Screenshot](path/to/dashboard.png)

### Practice Session
![Practice Screenshot](path/to/practice.png)

### Analytics
![Analytics Screenshot](path/to/analytics.png)

---

## 🤝 Contributing

We welcome contributions! Here's how you can help:

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/YourFeature
   ```
3. **Commit your changes**
   ```bash
   git commit -m "Add YourFeature"
   ```
4. **Push to the branch**
   ```bash
   git push origin feature/YourFeature
   ```
5. **Open a Pull Request**

### Contribution Guidelines

- Follow PEP 8 style guide for Python code
- Add comments for complex logic
- Test thoroughly before submitting
- Update documentation as needed

---

## 👥 Team

**Team HustlerDevs**

Built for VisionX Hackathon 2026

- Project Lead: [Your Name]
- AI Integration: [Team Member]
- UI/UX Design: [Team Member]
- Backend Development: [Team Member]

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- Google Gemini AI for powering the conversational intelligence
- Streamlit for the amazing web framework
- VisionX Hackathon for the opportunity
- All beta testers and early users

---

## 🐛 Known Issues

- [ ] Session timeout may require re-login
- [ ] Large report downloads may take time
- [ ] Mobile responsiveness can be improved

---

## 🔮 Future Enhancements

- [ ] Voice input/output integration
- [ ] Video recording for body language analysis
- [ ] Multi-language support
- [ ] Group practice sessions
- [ ] Coach marketplace
- [ ] Mobile app (iOS/Android)
- [ ] Integration with calendar apps
- [ ] Social sharing features
- [ ] Premium subscription tiers

---

## 📞 Support

For questions, issues, or feedback:

- **Email**: support@neurotalk.com
- **GitHub Issues**: [Create an issue](https://github.com/yourusername/neurotalk/issues)
- **Discord**: [Join our community](https://discord.gg/neurotalk)

---

## ⭐ Star Us!

If NeuroTalk helped you build confidence, please star this repository to support the project!

---

**Built with ❤️ by Team HustlerDevs | VisionX Hackathon 2026**

*Transform how you communicate, one conversation at a time.*
