# 🤖 JARVIS: Just A Rather Very Intelligent System

### The Ultimate Personal AI Assistant for Windows
JARVIS is a real-time, voice-driven AI ecosystem that can **hear, see, and control** your digital world with autonomy. Unlike static chatbots, JARVIS lives on your desktop, interacts with your files, manages your apps, and completes complex tasks through an agentic multi-tool architecture.

---

## 🔥 Key Technical Features

*   **🎙️ Real-time Multimodal Conversation**: Powered by **Gemini Live API**, allowing for natural, fluid dialogue with zero-latency interruption.
*   **👁️ Visual Understanding**: JARVIS can see your computer screen or your webcam, analyze the content, and explain it to you in real-time.
*   **🧠 Agentic Workflow Engine**: JARVIS doesn't just answer questions—it builds a plan. When you give a complex goal (e.g., *"Research AI news, summarize it in a text file, and WhatsApp it to Smith"*), JARVIS plans the steps and executes them one by one.
*   **💻 Deep System Control**: Control system volume, brightness, window management, app launching, and even shell commands with natural speech.
*   **📂 Multi-Service Integration**: Out-of-the-box support for:
    *   **Messaging**: WhatsApp, Telegram, Instagram
    *   **Media**: YouTube (Play, Summarize, Trending)
    *   **Travel**: Real-time Google Flights search and tracking
    *   **Productivity**: Reminder system, File Controller, Dev Agent (Full project builder)
    *   **Search**: Intelligent web search with result synthesis
*   **📈 Intelligence & Learning (Extension)**: A modular layer that logs sessions, analyzes user patterns/sentiment, and uses Machine Learning to predict and prevent system failures.

---

## 🏗️ The Architecture (How it Works)

JARVIS is built on a modular "Brain & Core" architecture:

1.  **The Interface (ui.py)**: A high-performance, 60fps animated Tkinter HUD that provides visual feedback for listening, thinking, and speaking.
2.  **The Live Session (main.py)**: Manages the bidirectional stream between your microphone/speaker and the Gemini Live API.
3.  **The Planner (agent/planner.py)**: Translates human language into a sequence of executable tool calls using advanced reasoning.
4.  **The Executor (agent/executor.py)**: Safely runs each tool step, handles errors, and performs automatic recovery if a step fails.
5.  **The Tool Registry (actions/)**: A library of 16+ modules that allow the AI to interact with Windows, the web, and external APIs.
6.  **The Intelligence Layer (jarvis_extension/)**: Asynchronous logging and analysis system with MongoDB integration and ML success prediction.

---

## ⚡ Quick Start

### 🚀 Recommended Installation (Fast)
Requires [uv](https://github.com/astral-sh/uv):
```powershell
pip install uv
python setup.py   # Installs dependencies 10x faster
python main.py
```

### 🐍 Standard Installation
Using standard pip:
```powershell
python setup.py
python main.py
```

*On first launch, enter your **Gemini API Key** in the setup prompt. JARVIS uses a secure `.env` system for all credentials.*

---

## 🛠️ Built With

*   **Core**: Python 3.10+
*   **Intelligence**: Google Gemini 3.1 (Live Vision/Audio)
*   **Automation**: Playwright, PyAutoGUI, Windows Shell
*   **Interface**: Custom Tkinter (HUD Architecture)
*   **Async**: Threading & Priority Task Queuing

---

## 📁 Project Map

*   `main.py`: Entry point for Live AI session.
*   `ui.py`: The visual JARVIS persona.
*   `agent/`: The "Intelligence Center" (Planning and Execution).
*   `actions/`: The "Hands" (Tool modules).
*   `core/`: Core behavior prompts and persona definitions.
*   `memory/`: Long-term user preference management.

---

*JARVIS — Built for intelligent automation. Always evolving.* 🚀
