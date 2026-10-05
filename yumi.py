import asyncio
import datetime
import os
import random
import re
import sys
import time
from threading import Thread
import tkinter as tk
from tkinter import DISABLED, END, NORMAL, Scrollbar, Text

import edge_tts
import psutil
import pyautogui
import pygetwindow as gw
import pywhatkit
import speech_recognition as sr
import webbrowser
import wikipedia
from PIL import Image, ImageSequence, ImageTk

# Initialize Pygame Mixer for non-blocking, reliable audio playback
import pygame
pygame.mixer.init()

from responses import responses

# Global Recognizer instance
listener = sr.Recognizer()


def resource_path(relative_path):
    """Get absolute path to resource, works for dev and PyInstaller."""
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


async def speak(text):
    """Converts text to speech using edge_tts and plays it via Pygame."""
    print("AI:", text)
    filename = f"output_{int(time.time() * 1000)}_{random.randint(1000, 9999)}.mp3"
    try:
        communicate = edge_tts.Communicate(
            text,
            voice="ja-JP-NanamiNeural",
            rate="-15%",
            pitch="+40Hz"
        )
        await communicate.save(filename)

        # Play audio using pygame
        pygame.mixer.music.load(filename)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            await asyncio.sleep(0.05)
        pygame.mixer.music.unload()
    except Exception as e:
        print(f"Error in speak: {e}")
    finally:
        if os.path.exists(filename):
            try:
                os.remove(filename)
            except PermissionError:
                pass


def listen_command():
    """Captures voice input from the microphone."""
    with sr.Microphone() as source:
        print("Listening...")
        try:
            listener.adjust_for_ambient_noise(source, duration=0.5)
            audio = listener.listen(source, phrase_time_limit=5)
        except Exception as e:
            print(f"Error listening: {e}")
            return ""

    try:
        command = listener.recognize_google(audio).lower()
        print("You:", command)
        return command
    except sr.UnknownValueError:
        return ""
    except sr.RequestError:
        return "network error"
    except Exception as e:
        print(f"Error recognizing: {e}")
        return ""


# --- Command Handlers ---

async def respond_to_who_made_you(command):
    if "who made you" in command:
        text = "I was made by Amanshu Sharma. He's a computer engineering student who built me as a free project to learn and experiment."
        await speak(text)
        await asyncio.to_thread(webbrowser.open, "https://github.com/amanshu999")
        await asyncio.to_thread(webbrowser.open, "https://www.linkedin.com/in/amanshu404/")
        return True
    return False


async def handle_small_talk(command):
    for key in responses:
        if key in command:
            await speak(random.choice(responses[key]))
            return True
    return False


async def _run_timer_task(value, unit, seconds):
    """Background coroutine for non-blocking timer execution."""
    await speak(f"Timer set for {value} {unit}")
    await asyncio.sleep(seconds)
    await speak(f"Time's up! Your {value} {unit} timer has finished.")


async def set_timer(command):
    if "timer" not in command:
        return False

    pattern = r"timer for (\d+)\s*(seconds|second|minutes|minute)"
    match = re.search(pattern, command)
    if match:
        value = int(match.group(1))
        unit = match.group(2)
        seconds = value if "second" in unit else value * 60
        asyncio.create_task(_run_timer_task(value, unit, seconds))
        return True
    else:
        await speak("Sorry, I couldn't understand the timer duration.")
        return True


async def repeat_after_me(command):
    if "repeat after me" in command:
        to_repeat = command.split("repeat after me")[-1].strip()
        if to_repeat:
            await speak(to_repeat)
            return True
    elif "say " in command:
        to_repeat = command.split("say")[-1].strip()
        if to_repeat:
            await speak(to_repeat)
            return True
    return False


async def play_song_on_youtube(command):
    if "play" in command and "youtube" in command:
        song = command.replace("play", "").replace("on youtube", "").replace("youtube", "").strip()
        if song:
            await speak(f"Playing {song} on YouTube")
            await asyncio.to_thread(pywhatkit.playonyt, song)
            return True
    return False


async def play_song_on_spotify(command):
    if "play" in command and "spotify" in command:
        song = command.replace("play", "").replace("on spotify", "").strip()
        await speak(f"Playing {song} on Spotify")
        await asyncio.to_thread(webbrowser.open, f"https://open.spotify.com/search/{song}")
        await asyncio.sleep(5)
        await asyncio.to_thread(pyautogui.press, 'tab', presses=5, interval=0.3)
        await asyncio.to_thread(pyautogui.press, 'enter')
        await asyncio.sleep(1)
        await asyncio.to_thread(pyautogui.press, 'space')
        return True
    return False


async def search_anything(command):
    if "search" not in command:
        return False

    query = command.replace("search", "").replace("for", "").strip()

    if "youtube" in command:
        query = query.replace("on youtube", "").strip()
        await speak(f"Searching YouTube for {query}")
        await asyncio.to_thread(webbrowser.open, f"https://www.youtube.com/results?search_query={query}")
    elif "chat gpt" in command or "chatgpt" in command:
        query = query.replace("on chat gpt", "").replace("on chatgpt", "").strip()
        await speak(f"Searching ChatGPT for {query}")
        await asyncio.to_thread(webbrowser.open, f"https://chat.openai.com/?q={query}")
    else:
        query = query.replace("on google", "").strip()
        await speak(f"Searching Google for {query}")
        await asyncio.to_thread(webbrowser.open, f"https://www.google.com/search?q={query}")
    return True


async def open_any_website(command):
    if "open" not in command:
        return False

    known_sites = {
        "youtube": "https://www.youtube.com",
        "google": "https://www.google.com",
        "instagram": "https://www.instagram.com",
        "chatgpt": "https://chat.openai.com",
        "github": "https://github.com",
        "spotify": "https://open.spotify.com"
    }
    for name, url in known_sites.items():
        if name in command:
            await speak(f"Opening {name}")
            await asyncio.to_thread(webbrowser.open, url)
            return True

    site = command.split("open")[-1].strip().replace(" ", "")
    if site:
        url = f"https://www.{site}.com"
        await speak(f"Trying to open {site}")
        await asyncio.to_thread(webbrowser.open, url)
        return True
    return False


async def tell_about_topic(command):
    trigger_phrases = ["do you know about", "tell me about", "who is", "what do you know about"]
    for phrase in trigger_phrases:
        if phrase in command:
            topic = command
            for p in trigger_phrases:
                topic = topic.replace(p, "")
            topic = topic.strip()
            if not topic:
                continue

            try:
                summary = await asyncio.to_thread(wikipedia.summary, topic, sentences=2)
                await speak(summary)
            except wikipedia.exceptions.DisambiguationError:
                await speak(f"There are multiple entries for {topic}. Please be more specific.")
            except wikipedia.exceptions.PageError:
                await speak(f"I couldn't find any information about {topic}.")
            except Exception:
                await speak("I encountered an error looking that up.")
            return True
    return False


async def explain_meaning(command):
    trigger_phrases = ["what do you mean by", "define", "explain", "what is"]
    for phrase in trigger_phrases:
        if phrase in command:
            topic = command
            for p in trigger_phrases:
                topic = topic.replace(p, "")
            topic = topic.strip()
            if not topic:
                continue

            try:
                summary = await asyncio.to_thread(wikipedia.summary, topic, sentences=2)
                await speak(summary)
            except wikipedia.exceptions.DisambiguationError:
                await speak(f"There are multiple meanings of {topic}. Can you be more specific?")
            except wikipedia.exceptions.PageError:
                await speak(f"I couldn't find the meaning of {topic}.")
            except Exception:
                await speak("I encountered an error looking that up.")
            return True
    return False


async def close_application(command):
    if "close" not in command:
        return False

    keyword = command.replace("close", "").replace("app", "").strip().lower()
    if not keyword:
        return False

    windows = await asyncio.to_thread(gw.getWindowsWithTitle, '')
    found = False

    for window in windows:
        title = window.title.lower()
        if keyword in title:
            try:
                window.close()
                await speak(f"Closed window containing {keyword}")
                found = True
                break
            except Exception:
                continue

    if not found:
        await speak(f"No window found containing '{keyword}'")
    return True


async def time_based_greeting():
    hour = datetime.datetime.now().hour
    if 5 <= hour < 12:
        await speak("Good morning! How can I help you today?")
    elif 12 <= hour < 17:
        await speak("Good afternoon senpai, need help?")
    elif 17 <= hour < 22:
        await speak("Good evening! Need any assistance?")
    else:
        await speak("Hello! It's quite late. Do you need help with something?")


# --- Assistant GUI ---

class AssistantGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Yumi AI")
        self.root.geometry("800x700")
        self.root.configure(bg="black")
        self.root.resizable(False, False)
        self.root.wm_attributes("-topmost", True)

        self.canvas = tk.Canvas(self.root, width=800, height=700, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        try:
            gif_path = resource_path("elf2.gif")
            gif = Image.open(gif_path)
            frame_size = (800, 600)
            self.frames = [
                ImageTk.PhotoImage(img.resize(frame_size, Image.LANCZOS).convert('RGBA'))
                for img in ImageSequence.Iterator(gif)
            ]
            self.gif_index = 0
            self.bg_image = self.canvas.create_image(0, 0, anchor='nw', image=self.frames[0])
            self.animate()
        except Exception as e:
            print(f"Error loading GIF: {e}")
            self.frames = []

        self.chat_log = Text(
            self.root,
            bg="#000000",
            fg="sky blue",
            font=("Consolas", 10),
            wrap='word',
            bd=0
        )
        self.chat_log.place(x=0, y=600, width=780, height=65)
        self.chat_log.insert(END, "[System] Type your command below or press F2 to speak.\n")
        self.chat_log.config(state=DISABLED)

        # Connected scrollbar widget
        scrollbar = Scrollbar(self.root, command=self.chat_log.yview)
        scrollbar.place(x=780, y=600, width=20, height=65)
        self.chat_log.config(yscrollcommand=scrollbar.set)

        self.entry = tk.Entry(self.root, font=("Segoe UI", 13), bg="#1a1a1a", fg="white", bd=3, insertbackground='white')
        self.entry.place(x=20, y=670, width=700, height=25)
        self.entry.bind("<Return>", self.send_text)

        send_button = tk.Button(self.root, text="Send", command=self.send_text, bg="#222222", fg="white", relief='flat')
        send_button.place(x=730, y=670, width=50, height=25)

        self.root.bind("<F2>", lambda e: self.listen_voice_thread())

        # Async Loop
        self.loop = asyncio.new_event_loop()
        self.loop_thread = Thread(target=self.start_async_loop, daemon=True)
        self.loop_thread.start()

        self.run_async(time_based_greeting())

    def start_async_loop(self):
        asyncio.set_event_loop(self.loop)
        try:
            self.loop.run_forever()
        except Exception as e:
            print(f"Event loop stopped: {e}")

    def run_async(self, coro):
        if not self.loop.is_closed():
            asyncio.run_coroutine_threadsafe(coro, self.loop)

    def animate(self):
        if self.frames:
            try:
                self.canvas.itemconfig(self.bg_image, image=self.frames[self.gif_index])
                self.gif_index = (self.gif_index + 1) % len(self.frames)
                self.root.after(100, self.animate)
            except Exception:
                pass

    def send_text(self, event=None):
        user_input = self.entry.get()
        self.entry.delete(0, END)
        if user_input:
            self.add_text("You: " + user_input)
            self.run_async(self.handle_command(user_input.lower()))

    def add_text(self, text):
        self.root.after(0, lambda: self._add_text_safe(text))

    def _add_text_safe(self, text):
        try:
            self.chat_log.config(state=NORMAL)
            self.chat_log.insert(END, text + "\n")
            self.chat_log.config(state=DISABLED)
            self.chat_log.see(END)
        except Exception as e:
            print(f"Error updating GUI: {e}")

    def listen_voice_thread(self):
        Thread(target=self._listen_and_process, daemon=True).start()

    def _listen_and_process(self):
        self.add_text("[System] Listening...")
        command = listen_command()
        if command:
            self.add_text("You: " + command)
            self.run_async(self.handle_command(command))
        else:
            self.add_text("[System] No command detected.")

    async def handle_command(self, command):
        try:
            if command == "network error":
                self.add_text("[System] Network error")
                await speak("Network error.")
                return

            if "exit" in command or "quit" in command:
                self.add_text("[System] Exiting...")
                await speak("Goodbye!")
                self.root.quit()
                return

            # Ordered Command Dispatch Pipeline
            command_dispatchers = [
                respond_to_who_made_you,
                handle_small_talk,
                set_timer,
                repeat_after_me,
                play_song_on_youtube,
                play_song_on_spotify,
                search_anything,
                open_any_website,
                tell_about_topic,
                explain_meaning,
                close_application
            ]

            for dispatcher in command_dispatchers:
                if await dispatcher(command):
                    return

            await speak("I don't understand what you're saying.")
            self.add_text("AI: Can you repeat that?")
        except Exception as e:
            print(f"Error handling command: {e}")
            self.add_text(f"[System] Error: {e}")


def main():
    root = tk.Tk()
    app = AssistantGUI(root)
    try:
        root.mainloop()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
