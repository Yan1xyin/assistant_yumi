import asyncio
import edge_tts
import playsound
import speech_recognition as sr
import webbrowser
import wikipedia
import pywhatkit
import pygetwindow as gw
import pyautogui
import psutil
import os
import time
import random
import tkinter as tk
from threading import Thread
from tkinter import PhotoImage, Scrollbar, Text, END, DISABLED, NORMAL
from PIL import Image, ImageTk, ImageSequence
import sys
import os
import re
import datetime
from responses import responses

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and PyInstaller """
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

listener = sr.Recognizer()

async def speak(text):
    print("AI:", text)
    filename = f"output_{int(time.time() * 1000)}_{random.randint(1000, 9999)}.mp3"
    try:
        communicate = edge_tts.Communicate(
            text,
            voice="ja-JP-NanamiNeural",  # Or try JennyNeural (ja-JP-NanamiNeural is Japanese, might sound weird for English but user had it)
            rate="-15%",                 # Slightly faster
            pitch="+40Hz"                # Higher pitch = more anime-like
        )
        await communicate.save(filename)
        # playsound 1.2.2 blocks by default. 
        # If using a newer version or fork, it might be different, but usually blocks.
        # We run this in a thread to ensure it doesn't block the event loop entirely if we wanted concurrency,
        # but for this app, blocking the loop is fine as discussed.
        # However, purely for safety against event loop warnings, we can run it in executor.
        await asyncio.to_thread(playsound.playsound, filename)
    except Exception as e:
        print(f"Error in speak: {e}")
    finally:
        try:
            if os.path.exists(filename):
                os.remove(filename)
        except PermissionError:
            print(f"Could not delete {filename} because it is still in use.")
        except Exception as e:
            print(f"Error deleting file: {e}")

def listen_command():
    with sr.Microphone() as source:
        print("Listening...")
        try:
            listener.adjust_for_ambient_noise(source, duration=0.5)
            # phrase_time_limit=5 prevents getting stuck listening forever
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

async def open_any_website(command):
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
    if "open" in command:
        site = command.split("open")[-1].strip().replace(" ", "")
        if site:
            url = f"https://www.{site}.com"
            await speak(f"Trying to open {site}")
            await asyncio.to_thread(webbrowser.open, url)
            return True
    return False

async def close_application(command):
    keyword = command.replace("close", "").replace("app", "").strip().lower()
    found = False

    # Get windows in a thread if it takes time, but usually fast enough
    start_time = time.time()
    # gw.getWindowsWithTitle might be blocking? It's usually fast.
    windows = await asyncio.to_thread(gw.getWindowsWithTitle, '')
    
    for window in windows:
        title = window.title.lower()
        if keyword in title:
            try:
                window.close()
                await speak(f"Closed window with {keyword}")
                found = True
                break
            except:
                continue

    if not found:
        await speak(f"No window found containing '{keyword}'")

async def search_anything(command):
    # Only check "search" once
    if "search" not in command:
        return False
        
    command = command.lower()
    query = command.replace("search", "").replace("for", "").strip()

    if "youtube" in command:
        query = query.replace("on youtube", "").strip()
        await speak(f"Searching YouTube for {query}")
        await asyncio.to_thread(webbrowser.open, f"https://www.youtube.com/results?search_query={query}")

    elif "chat gpt" in command:
        query = query.replace("on chat gpt", "").strip()
        await speak(f"Searching ChatGPT for {query}")
        await asyncio.to_thread(webbrowser.open, f"https://chat.openai.com/?q={query}")

    else:
        query = query.replace("on google", "").strip()
        await speak(f"Searching Google for {query}")
        await asyncio.to_thread(webbrowser.open, f"https://www.google.com/search?q={query}")
    return True 

async def play_song_on_youtube(command):
    if "play" in command and ("youtube" in command or "on youtube" in command):
        song = command.replace("play", "").replace("on youtube", "").replace("youtube", "").strip()
        if song:
            await speak(f"Playing {song} on YouTube")
            await asyncio.to_thread(pywhatkit.playonyt, song)
            return True
    return False


async def repeat_after_me(command):
    if "repeat after me" in command:
        to_repeat = command.split("repeat after me ",)[-1].strip()
        if to_repeat:
            await speak(to_repeat)
            return True
    elif "say" in command:
        to_repeat = command.split("say",)[-1].strip()
        if to_repeat:
            await speak(to_repeat)
            return True
    return False

async def tell_about_topic(command):
    trigger_phrases = ["do you know about", "tell me about", "who is", "what do you know about"]
    for phrase in trigger_phrases:
        if phrase in command.lower():
            try:
                topic = command.lower()
                for p in trigger_phrases:
                    topic = topic.replace(p, "")
                topic = topic.strip()
                if not topic: continue
                
                summary = await asyncio.to_thread(wikipedia.summary, topic, sentences=2)
                await speak(summary)
            except wikipedia.exceptions.DisambiguationError:
                await speak(f"There are multiple entries for {topic}. Please be more specific.")
            except wikipedia.exceptions.PageError:
                await speak(f"I couldn't find any information about {topic}.")
            except Exception as e:
                 await speak(f"I encountered an error looking that up.")
            return True
    return False

async def explain_meaning(command):
    trigger_phrases = ["what do you mean by", "define", "explain","what is"]
    for phrase in trigger_phrases:
        if phrase in command.lower():
            try:
                topic = command.lower()
                for p in trigger_phrases:
                    topic = topic.replace(p, "")
                topic = topic.strip()
                if not topic: continue

                summary = await asyncio.to_thread(wikipedia.summary, topic, sentences=2)
                await speak(summary)
            except wikipedia.exceptions.DisambiguationError:
                await speak(f"There are multiple meanings of {topic}. Can you be more specific?")
            except wikipedia.exceptions.PageError:
                await speak(f"I couldn't find the meaning of {topic}.")
            except Exception as e:
                 await speak(f"I encountered an error looking that up.")
            return True
    return False

async def set_timer(command):
    if "timer" not in command: return False
    
    pattern = r"timer for (\d+)\s*(seconds|second|minutes|minute)"
    match = re.search(pattern, command.lower())
    if match:
        value = int(match.group(1))
        unit = match.group(2)
        seconds = value if "second" in unit else value * 60
        await speak(f"Timer set for {value} {unit}")
        await asyncio.sleep(seconds)
        await speak(f"Time's up! Your {value} {unit} timer has finished.")
        return True
    else:
        # Only say we couldn't understand if it explicitly looked like a timer request
        if "timer" in command:
            await speak("Sorry, I couldn't understand the timer duration.")
            return True
    return False

async def time_based_greeting():
    hour = datetime.datetime.now().hour
    if 5 <= hour < 12:
        await speak("Good morning! ☀️ How can I help you today?")
    elif 12 <= hour < 17:
        await speak("Good afternoon senpai need help?")
    elif 17 <= hour < 22:
        await speak("Good evening! 🌆 Need any assistance?")
    else:
        await speak("Hello! It's quite late. Do you need help with something?")

async def tell_about_person(command):
    # This overlaps with tell_about_topic, might not be reached if tell_about_topic catches "who is" first
    # But let's keep it if logic flows to it.
    if "tell me about" in command or "who is" in command:
        return await tell_about_topic(command)
    return False

async def play_song_on_spotify(command):
    if "play" in command and "spotify" in command:
        song = command.replace("play", "").replace("on spotify", "").strip()
        await speak(f"Playing {song} on Spotify")
        await asyncio.to_thread(webbrowser.open, f"https://open.spotify.com/search/{song}")
        await asyncio.sleep(5)
        # Type filtering is brittle but kept as per original logic
        # Run in executor because these are blocking calls
        await asyncio.to_thread(pyautogui.press, 'tab', presses=5, interval=0.3)
        await asyncio.to_thread(pyautogui.press, 'enter')
        await asyncio.sleep(1)
        await asyncio.to_thread(pyautogui.press, 'space')
        return True
    return False

async def respond_to_who_made_you(command):
    if "who made you" in command.lower():
        text = "I was made by Amanshu Sharma. He's a computer engineering student who built me as a free project to learn and experiment."
        await speak(text)
        await asyncio.to_thread(webbrowser.open, "https://github.com/amanshu999")
        await asyncio.to_thread(webbrowser.open, "https://www.linkedin.com/in/amanshu404/")
        return True
    return False


async def handle_small_talk(command):
    command = command.lower()
    for key in responses:
        if key in command:
            await speak(random.choice(responses[key]))
            return True
    return False

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
            self.frames = [ImageTk.PhotoImage(img.resize(frame_size, Image.LANCZOS).convert('RGBA'))
                           for img in ImageSequence.Iterator(gif)]
            self.gif_index = 0
            self.bg_image = self.canvas.create_image(0, 0, anchor='nw', image=self.frames[0])
            self.animate()
        except Exception as e:
            print(f"Error loading GIF: {e}")
            self.frames = []

        self.root.configure(bg="#000000")

        self.chat_log = Text(
            self.root,
            bg="#000000",
            fg="sky blue",
            font=("Consolas", 10),
            wrap='word',
            bd=0
        )
        self.chat_log.place(x=0, y=600, width=800, height=100)
        self.chat_log.insert(END, "[System] Type your command below or press F2 to speak.\n")
        self.chat_log.config(state=tk.DISABLED)

        scrollbar = Scrollbar(self.chat_log)
        scrollbar.pack(side="right", fill="y")

        self.entry = tk.Entry(self.root, font=("Segoe UI", 13), bg="#1a1a1a", fg="white", bd=3, insertbackground='white')
        self.entry.place(x=20, y=670, width=700, height=30)
        self.entry.bind("<Return>", self.send_text)

        send_button = tk.Button(self.root, text="Send", command=self.send_text, bg="#222222", fg="white", relief='flat')
        send_button.place(x=730, y=670, width=50, height=30)

        # Bind F2 key
        self.root.bind("<F2>", lambda e: self.listen_voice_thread())
        
        # Start asyncio event loop in a background thread
        self.loop = asyncio.new_event_loop()
        self.loop_thread = Thread(target=self.start_async_loop, daemon=True)
        self.loop_thread.start()

        # Schedule greeting
        self.run_async(time_based_greeting())

    def start_async_loop(self):
        asyncio.set_event_loop(self.loop)
        try:
            self.loop.run_forever()
        except Exception as e:
            print(f"Event loop stopped: {e}")

    def run_async(self, coro):
        """Helper to run a coroutine in the background loop safely."""
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
            self.run_async(self.handle_command(user_input))

    def add_text(self, text):
        # Schedule GUI update on the main thread
        self.root.after(0, lambda: self._add_text_safe(text))

    def _add_text_safe(self, text):
        try:
            self.chat_log.config(state=tk.NORMAL)
            self.chat_log.insert(END, text + "\n")
            self.chat_log.config(state=tk.DISABLED)
            self.chat_log.see(END)
        except Exception as e:
            print(f"Error updating GUI: {e}")

    def listen_voice_thread(self):
        # Check if already listening to prevent overlap? 
        # For simplicity, allow it but ideally should be guarded.
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

            if await respond_to_who_made_you(command):
                return

            if await handle_small_talk(command):
                return

            if "open" in command:
                if await open_any_website(command):
                    return

            if "close" in command:
                await close_application(command)
                return
            
            if await set_timer(command):
                return

            if await repeat_after_me(command):
                return

            if await search_anything(command):
                return
            
            if await explain_meaning(command):
                return
            
            # play_song_on_youtube is covered below if not caught by "search"
            # logic flow: "play ... on youtube" 
            if "play" in command and ("youtube" in command or "on youtube" in command):
                 if await play_song_on_youtube(command):
                     return

            if await tell_about_topic(command):
                return

            if await play_song_on_spotify(command):
                return
                
            if "exit" in command:
                self.add_text("[System] Exiting...")
                await speak("Goodbye!")
                self.root.quit()
                return

            await speak("i dont understand what youre saying")
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
    finally:
        pass

if __name__ == "__main__":
    main()