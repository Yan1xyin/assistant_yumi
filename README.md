# 🌸 Yumi - Your Personalized Desktop Assistant 🌸

**Yumi** is a Python-based desktop assistant designed with a friendly personality. Unlike robotic AI, she can perform tasks like opening websites, searching the web, playing music, and chatting with you—all while maintaining a fun and engaging character using a custom anime-style voice. ✨

## 🚀 Features

- 🗣️ **Voice Interaction**: Talks back to you using a high-quality, anime-style TTS voice (`edge-tts`).
- 🌐 **Web Automation**: Opens websites like YouTube, Google, Instagram, and more hands-free.
- 🔍 **Search**: Searches Google, YouTube, and ChatGPT directly from your voice commands.
- 🎵 **Media Control**: Plays your favorite music on YouTube and Spotify.
- 📚 **Information**: Fetches summaries from Wikipedia for topics and people.
- ⏱️ **Utilities**: Sets timers and provides time-based greetings.
- 💬 **Custom Personality**: Engaging, friend-like responses for small talk.
- 🎨 **GUI**: A dark-themed, animated interface featuring a GIF avatar.

## 🛠️ Requirements

- Python 3.8+ 🐍
- Internet connection (for TTS and web features) 🌍
- A microphone 🎤

## 📥 Installation

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/amanshu999/assistant_yumi.git
    cd assistant_yumi
    ```

2.  **Install the required dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

    *Note: You may also need to install `pyaudio` separately if the installation fails, or use pre-compiled binaries for your OS.*

## 🎮 Usage

1.  **Run the application**:
    ```bash
    python yumi.py
    ```

2.  The GUI will open! Type commands in the text box or press **F2** to start voice recognition. 🎙️

## 🗣️ Common Commands

- **"Open YouTube"** 📺
- **"Search for [topic] on Google"** 🔎
- **"Play [song name] on YouTube"** 🎶
- **"Tell me about [person/topic]"** 📖
- **"Set a timer for 5 minutes"** ⏲️
- **"Who are you?"** (and other friendly chat! 👋)

## 🔧 Troubleshooting

- **Microphone issues**: Ensure your default microphone is set correctly in your system settings.
- **Voice not playing**: Detailed error logs will be printed to the console. Check if `edge-tts` or `playsound` is encountering issues with file permissions.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
