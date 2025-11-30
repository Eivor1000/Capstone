# 🎨 AI Creative Suite - Story Generator, Study Assistant & Kids Challenge

A comprehensive full-stack AI-powered application featuring story generation with cover images, an intelligent study assistant, educational video recommendations, and an AI-graded kids creative challenge. Built with cutting-edge AI technologies and modern web frameworks.

## 🌟 Features Overview

This project includes **4 powerful AI tools** in one platform:

### 1️⃣ **AI Story Generator**
- 📖 Generate creative stories using Groq AI (llama-3.3-70b-versatile)
- 🎨 Create AI-generated cover images using Pollinations.ai
- 📄 Export stories with covers to professional PDFs
- 🔊 **Read Aloud** - Browser-based text-to-speech for stories
- ✨ Beautiful, responsive UI

### 2️⃣ **AI Study Assistant**
- 📝 **Summarize** - Get concise bullet-point summaries of any text
- 🧠 **Understand** - Detailed explanations with examples and analogies
- 📚 **Revise** - Generate practice MCQs (7-10 questions) and Q&A pairs (5 questions)
- ✅ Interactive quiz interface with scoring
- 🎯 Answer reveal functionality
- 📺 **Find Educational Videos** - Get 3 curated YouTube videos for any topic

### 3️⃣ **YouTube Educational Video Finder**
- 🔍 AI-powered topic extraction from any text
- 📹 Search YouTube Data API with strict educational filters
- 🛡️ Safety features: `safeSearch=strict`, content filtering
- 🎓 Only educational content (filters out gaming, pranks, entertainment)
- 📊 Maximum 3 videos per search
- 🌐 Direct links to watch on YouTube

### 4️⃣ **Kids Creative Challenge** 🎨 (Ages 5-8)
- 🖍️ Fun creative assignments (coloring, drawing, crafts)
- 🤖 **AI-powered grading** using local Qwen2-VL-2B-Instruct vision model
- 🏆 Weekly leaderboard with points system
- ⭐ Encouraging feedback and improvement suggestions
- 📸 Upload photos of artwork for instant AI grading
- 🎯 Scores 0-10 with positive reinforcement
- 💻 **Runs 100% locally** on GPU (no API costs, privacy-first)

## 🎯 Use Cases

- **Students:** Summarize textbook chapters, practice with MCQs, find video tutorials
- **Teachers:** Generate story prompts, create study materials, find educational resources
- **Writers:** Get story ideas, create book covers, export to PDF
- **Self-learners:** Understand complex topics, revise with practice questions
- **Parents:** Fun, educational activities for kids with AI grading and encouragement
- **Kids (5-8):** Creative challenges with instant feedback and rewards

## 🚀 Tech Stack

### Backend
- **Python 3.8+**
- **Flask** - REST API framework
- **Groq API** - Story generation & text processing (llama-3.3-70b-versatile)
- **Qwen2-VL-2B-Instruct** - Local vision-language model for kids challenge grading
- **PyTorch 2.5+ (CUDA)** - GPU acceleration for vision model
- **Transformers** - Hugging Face library for model loading
- **Pollinations.ai** - Free image generation (no API key needed!)
- **YouTube Data API v3** - Educational video search
- **ReportLab** - Professional PDF creation
- **Pillow** - Image processing

### Frontend
- **React 18** - UI framework
- **React Router** - Multi-page navigation
- **Vite** - Fast build tool
- **Tailwind CSS** - Modern styling
- **Axios** - HTTP client
- **Web Speech API** - Browser-based text-to-speech

## 📋 Prerequisites

- **Python 3.8+**
- **Node.js 16+**
- **npm** or **yarn**
- Free API keys (see below)

## 🔑 API Keys Setup

You'll need **2 free API keys**:

### 1. Groq API Key (Required)
**For:** Story generation, text summarization, explanations, MCQ generation, topic extraction

1. Go to [https://console.groq.com](https://console.groq.com)
2. Sign up for a free account (Google/GitHub login available)
3. Navigate to **API Keys** section
4. Click **"Create API Key"**
5. Copy the key (format: `gsk_xxxxxxxxxxxxxxxxxxxxx`)

**Free Tier:** Very generous limits for personal/educational use

### 2. YouTube Data API v3 Key (Optional - for video search)
**For:** Finding educational YouTube videos

1. Go to [https://console.cloud.google.com](https://console.cloud.google.com)
2. Create a new project or select existing
3. Click **"Enable APIs & Services"**
4. Search for **"YouTube Data API v3"** and enable it
5. Go to **"Credentials"** → **"Create Credentials"** → **"API Key"**
6. Copy the key (format: `AIzaSyXXXXXXXXXXXXXXXXXXXXXXXXX`)

**Free Tier:** 10,000 quota units/day = ~100 video searches/day

### 3. Image Generation (No API Key Needed!)
Uses **Pollinations.ai** - completely free, no registration required.

## 📦 Installation

### Backend Setup

1. **Navigate to backend directory:**
```bash
cd story-generator/backend
```

2. **Create virtual environment:**
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Configure environment variables:**
```bash
# Windows
copy .env.example .env

# macOS/Linux
cp .env.example .env
```

5. **Edit `.env` file and add your API keys:**
```env
GROQ_API_KEY=your_groq_api_key_here
YOUTUBE_API_KEY=your_youtube_api_key_here  # Optional
```

### Frontend Setup

1. **Navigate to frontend directory:**
```bash
cd story-generator/frontend
```

2. **Install dependencies:**
```bash
npm install
```

## ▶️ Running the Application

You need **two terminal windows** - one for backend, one for frontend.

### Terminal 1: Start Backend

```bash
cd story-generator/backend
venv\Scripts\activate  # Windows
# source venv/bin/activate  # macOS/Linux
python app.py
```

Backend runs on: **http://localhost:5000**

### Terminal 2: Start Frontend

```bash
cd story-generator/frontend
npm run dev
```

Frontend runs on: **http://localhost:3000**

Your browser should automatically open to the application!

## 🎮 How to Use

### Feature 1: Story Generator

1. Click **"Story Generator"** from home page
2. Enter a story prompt (e.g., "A sci-fi story about AI becoming sentient")
3. Click **"Generate Story & Cover"**
4. Wait for AI to generate story and cover image
5. Preview your story and cover
6. Click **"Read Aloud"** to hear the story
7. Click **"Download PDF"** to save

### Feature 2: AI Study Assistant

1. Click **"AI Study Assistant"** from home page
2. Paste text or enter a topic to study
3. Choose a mode:
   - **📝 Summarize** - Get bullet-point summary
   - **🧠 Understand** - Get detailed explanation
   - **📚 Revise** - Get MCQs and Q&A for practice
4. Review results
5. **(Optional)** Click **"Find Educational Videos"** for YouTube tutorials

### Feature 3: Video Search (within Study Assistant)

1. After getting Summarize/Explain/Revise results
2. Click **"Find Educational Videos"**
3. AI extracts the topic and searches YouTube
4. View 3 curated educational videos
5. Click any video to watch on YouTube

## 📁 Project Structure

```
story-generator/
├── README.md                           # This file
├── .gitignore                          # Git ignore rules
│
├── backend/
│   ├── app.py                          # Flask API (all endpoints)
│   ├── requirements.txt                # Python dependencies
│   ├── .env.example                    # Environment template
│   └── .env                            # Your API keys (create this)
│
└── frontend/
    ├── src/
    │   ├── components/
    │   │   ├── HomePage.jsx            # Landing page with 3 features
    │   │   ├── StoryGenerator.jsx      # Story generator UI
    │   │   └── StudyAssistant.jsx      # Study assistant UI
    │   ├── App.jsx                     # Main app with routing
    │   ├── main.jsx                    # React entry point
    │   └── index.css                   # Tailwind imports
    │
    ├── index.html                      # HTML template
    ├── package.json                    # Node dependencies
    ├── vite.config.js                  # Vite config
    ├── tailwind.config.js              # Tailwind config
    └── postcss.config.js               # PostCSS config
```

## 🔌 API Endpoints

### Story Generator
- `POST /api/generate-story` - Generate creative story
- `POST /api/generate-image` - Create cover image
- `POST /api/create-pdf` - Export story + image to PDF

### Study Assistant
- `POST /api/summarize` - Summarize text
- `POST /api/explain` - Detailed explanation
- `POST /api/generate-revision` - Generate MCQs and Q&A

### Video Search
- `POST /api/find-videos` - Find educational YouTube videos

### Health
- `GET /health` - Check API status

## 🛡️ Safety & Privacy

### Educational Video Search Safety:
- ✅ `safeSearch=strict` enabled
- ✅ Filters out gaming, pranks, entertainment content
- ✅ Only embeddable, educational videos
- ✅ English language content only
- ✅ Medium-length videos (4-20 minutes)
- ✅ Maximum 3 videos per search
- ✅ "Educational purposes only" notice displayed

### API Key Security:
- 🔒 `.env` file excluded from Git (see `.gitignore`)
- 🔒 Never commit real API keys
- 🔒 `.env.example` provided with placeholders only

## 💰 Cost Breakdown

| Service | Free Tier | Cost After Free |
|---------|-----------|-----------------|
| **Groq API** | Very generous | Contact for pricing |
| **Pollinations.ai** | Unlimited FREE | Always free |
| **YouTube Data API** | 10,000 units/day (~100 searches) | Paid tiers available |

**Total for personal use: $0** ✅

## 🐛 Troubleshooting

### Backend Issues

**"API key not found":**
- Ensure `.env` file exists in `backend/` folder
- Check API keys are pasted correctly (no extra spaces)
- Restart backend server

**"Module not found":**
- Activate virtual environment
- Run `pip install -r requirements.txt` again

### Frontend Issues

**"Cannot connect to backend":**
- Check backend is running on `http://localhost:5000`
- Look for errors in backend terminal

**Styling issues:**
- Clear browser cache
- Run `npm install` again

### Image Generation Issues

**Timeout errors:**
- Pollinations.ai may be slow sometimes
- Wait and try again
- Check internet connection

### Video Search Issues

**"YouTube API not configured":**
- Add `YOUTUBE_API_KEY` to `.env` file
- Restart backend

**"Quota exceeded":**
- Daily limit reached (100 searches/day)
- Try again tomorrow
- Or use fallback YouTube search link

## 🚀 Deployment

### Backend (Heroku, Railway, Render)
1. Add environment variables in platform dashboard
2. Use `requirements.txt` for dependencies
3. Set start command: `python app.py`

### Frontend (Vercel, Netlify)
1. Build command: `npm run build`
2. Publish directory: `dist`
3. Update API URL in code to your backend URL

## 🤝 Contributing

Contributions welcome! Feel free to:
- Report bugs
- Suggest features
- Submit pull requests

## 📜 License

This project is open source and available under the MIT License.

## 🙏 Credits

- **Groq AI** - Fast LLM inference (llama-3.3-70b-versatile)
- **Pollinations.ai** - Free image generation
- **YouTube Data API** - Educational video search
- **ReportLab** - PDF generation
- **React** - UI framework
- **Tailwind CSS** - Styling

## 📧 Support

For issues or questions:
- Open an issue on GitHub
- Check the troubleshooting section above

---

**Built with ❤️ using AI technologies**

Enjoy creating stories, learning with AI, and exploring educational content! 🎉
