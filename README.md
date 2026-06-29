# 🎬 Renderly

### Prompt to Motion: AI-Powered 2D Math & Physics Animations

Renderly is an AI-driven 2D animation generation platform. It translates natural language prompts into production-ready Python Manim code, renders them into video files, saves them locally, and manages complex projects using a multi-shot timeline interface.

---

# 📌 Project Overview

Renderly bridges the gap between text-based generative AI and precise programmatic animation. By leveraging FastAPI on the backend and React on the frontend, users can describe animations such as mathematical proofs, physical simulations, or educational content, save the rendered videos locally, and instantly preview, edit, and stitch generated video shots together.

---

# ✨ Features

- 🎯 **Prompt-to-Animation**  
  Instantly convert complex prompts into structured 2D animations.

- 🤖 **AI Code Generator**  
  Auto-generates clean, syntactically correct Python Manim code via the Gemini API.

- 📂 **Multi-Project Management**  
  Create, save, and organize multiple design projects.

- 🎞️ **Multi-Shot Timeline**  
  Split projects into individual scenes (shots). Create, update, or delete shots.

- 🎬 **Video Compiler**  
  Merge individual rendered shots into a single cohesive final output video.

- 💾 **Local Video Caching**  
  Fast local storage system to save, retrieve, and preview rendered MP4 outputs.

- ✍️ **Interactive Editor**  
  Review and manually edit the AI-generated Manim code directly inside the application.

---

# 🛠️ Tech Stack

## Frontend

- **Framework:** React (Vite)
- **HTTP Client:** Axios
- **Styling:** CSS

## Backend

- **Runtime:** Python 3.10+
- **Framework:** FastAPI
- **Animation Engine:** Manim Community Edition
- **AI Engine:** Gemini API Integration

## Database & Storage

- **Database:** MongoDB
- **Storage:** Local video storage system

---

# 🏗️ Architecture & Workflow

```text
[ Frontend (React) ] ──( Prompt )──> [ Backend (FastAPI) ]
         ▲                                     │
         │                                     ▼
         │                            [ Gemini AI API ]
         │                                     │
         │ (Rendered MP4)                 (Manim Code)
         │                                     ▼
         ├<──( Stream/Display )────── [ Manim Engine ]
         │                                     │
         ▼                                     ▼
[ Local Video Storage ] <──( Save )────────────┼─> [ MongoDB (Metadata) ]
```

---

# ⚡ Execution Flow

## 1. Input
User submits a descriptive animation prompt from the React frontend.

## 2. API Call
Frontend transmits the prompt payload to the FastAPI backend.

## 3. Generation
Backend formats a system prompt and calls the Gemini API to generate clean Manim code.

## 4. Compilation
The backend writes the code to a temporary file and triggers the Manim CLI renderer.

## 5. Storage
The output `.mp4` file is saved to the local storage path and referenced in MongoDB.

## 6. Output
The frontend fetches, displays, and plays the compiled video stream directly from local storage.

---

# ⚙️ Environment Variables

## Frontend Configuration

The frontend configuration has already been configured in your `.env` file:

```env
VITE_API_URL=http://127.0.0.1:8000
```

---

## Backend Configuration

Create a `.env` file inside the backend directory:

```env
MONGODB_URL=your_mongodb_connection_url_here
DATABASE_NAME=renderly

GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-2.5-flash
GEMINI_FALLBACK_MODELS=gemini-1.5-pro,gemini-1.5-flash

STORAGE_PATH=./storage

CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173

MANIM_QUALITY=ql
# ql = low
# qm = medium
# qh = high

RENDER_TIMEOUT_SEC=600
```

---

# 🚀 Installation & Setup

# 📋 Prerequisites

Make sure the following are installed:

- Python 3.10 or higher
- Node.js (v18+) and npm
- MongoDB (local instance or cloud URI)
- FFmpeg
- LaTeX (Required for Manim rendering)

---

## macOS Dependencies

```bash
brew install py3cairo ffmpeg pango scipy
```

---

## Ubuntu Dependencies

```bash
sudo apt install libcairo2-dev libpango1.0-dev ffmpeg
```

---

# 🔧 Backend Setup

## Navigate to backend directory

```bash
cd backend
```

---

## Create virtual environment

```bash
python -m venv venv
```

---

## Activate virtual environment

### macOS/Linux

```bash
source venv/bin/activate
```

### Windows

```bash
venv\Scripts\activate
```

---

## Install backend dependencies

```bash
pip install -r requirements.txt
```

---

## Run FastAPI server (don't use --reload as this cause problem implementing async subprocesses)

```bash
uvicorn app.main:app 
```

---

# 🎨 Frontend Setup

## Navigate to frontend directory

```bash
cd ../frontend
```

---

## Install frontend dependencies

```bash
npm install
```

---

## Start frontend server

```bash
npm run dev
```

---

# 💡 Example Prompt

## Prompt

```text
Draw a grid, then animate a blue circle moving from coordinate (-2, -1) to (3, 2) along a parabolic path y = 0.2x^2. Show a tracker displaying the coordinate value.
```

---

# 🧠 Resulting Manim Concept Class

```python
from manim import *

class ParabolicMovement(Scene):
    def construct(self):
        grid = NumberPlane()
        self.add(grid)

        # Path and moving object
        circle = Dot(color=BLUE).move_to(np.array([-2, -1, 0]))

        self.play(FadeIn(circle))

        # Generated Manim transforms execute here
```


# 🔥 Core Functionalities

## 🎬 AI Animation Pipeline

Renderly automates the complete animation generation workflow:

1. Accepts natural language prompts
2. Converts prompts into structured Manim scripts
3. Executes rendering using Manim CLI
4. Stores generated videos locally
5. Streams videos back to the frontend

---

## 📦 Multi-Shot Rendering System

Projects are divided into independent shots/scenes:

- Each shot contains its own prompt
- Individual shots can be regenerated independently
- Timeline-based organization improves scalability
- Final shots are stitched into one compiled video

---

## 🧠 Gemini AI Integration

The backend uses Gemini models for:

- Code generation
- Prompt enhancement
- Syntax correction
- Scene structuring
- Animation logic generation

Fallback models improve reliability if the primary model fails.

---

## 💾 Local Rendering & Storage

Generated videos are:

- Stored locally for fast access
- Cached for repeated playback
- Linked to MongoDB metadata
- Organized by project and shot IDs

---

# 🛡️ Error Handling

Renderly includes robust backend protections:

- Render timeout protection
- Invalid Manim code validation
- API fallback handling
- Local storage verification
- Safe temporary file cleanup

---

# ⚡ Performance Optimizations

- Multi-shot rendering architecture
- Local MP4 caching
- Lightweight React frontend
- FastAPI asynchronous endpoints
- Efficient MongoDB metadata indexing

