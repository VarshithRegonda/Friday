#!/usr/bin/env python3
"""
FRIDAY ASSISTANT - IRON MAN EDITION
Tony Stark's FRIDAY AI - Voice-controlled assistant with Iron Man personality
Speaks like FRIDAY and responds with witty AI personality
Supports: Windows & macOS

Author: FRIDAY Development Team
Version: 3.5 (Iron Man Edition - With Voice & Personality)
"""

import os
import sys
import time
import logging
import sqlite3
import threading
import platform
import subprocess
import random
from datetime import datetime
from tkinter import (
    Tk, Frame, Label, Button, messagebox, simpledialog, ttk, 
    BooleanVar, DoubleVar, IntVar, StringVar, Canvas, Text
)
import tkinter.font as tkFont
import speech_recognition as sr

try:
    import pyttsx3
    HAS_PYTTSX3 = True
except ImportError:
    HAS_PYTTSX3 = False
    logger_temp = logging.getLogger(__name__)
    logger_temp.warning("pyttsx3 not installed. Install with: pip install pyttsx3")


# ==========================================================
# LOGGING CONFIGURATION
# ==========================================================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('friday_assistant.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


# ==========================================================
# FRIDAY PERSONALITY & RESPONSES
# ==========================================================
class FRIDAYPersonality:
    """FRIDAY AI personality and dialogue"""
    
    # FRIDAY's voice responses
    GREETINGS = [
        "Good morning, Sir. I trust you slept well.",
        "Hello, Sir. Ready to work?",
        "Good day, Sir. At your service.",
        "Welcome back, Sir. Systems online and ready.",
        "Hello, Sir. How may I assist you today?",
    ]
    
    STARTUP_MESSAGES = [
        "FRIDAY online. All systems nominal.",
        "Initializing FRIDAY protocols. Standing by.",
        "Good morning, Sir. I am fully operational.",
        "FRIDAY AI initialized. Ready for your commands.",
        "Systems check complete. All green, Sir.",
    ]
    
    APP_LAUNCH_RESPONSES = [
        "Launching {app} for you now, Sir.",
        "Opening {app} immediately, Sir.",
        "Activating {app}, Sir.",
        "One moment, Sir. Bringing up {app}.",
        "Right away, Sir. {app} is being launched.",
    ]
    
    SUCCESS_RESPONSES = [
        "Task complete, Sir.",
        "Done, Sir.",
        "As you wish, Sir.",
        "Affirmative, Sir.",
        "Consider it done, Sir.",
    ]
    
    ERROR_RESPONSES = [
        "I'm afraid I cannot do that, Sir.",
        "My apologies, Sir. That command is not recognized.",
        "I'm unable to comply with that request, Sir.",
        "That appears to be unavailable, Sir.",
        "I'm afraid that's beyond my current capabilities, Sir.",
    ]
    
    NOTE_RESPONSES = [
        "Note saved, Sir.",
        "I have recorded that for you, Sir.",
        "Understood, Sir. Note saved.",
        "Your note has been stored, Sir.",
        "Committing that to memory, Sir.",
    ]
    
    FAREWELL_MESSAGES = [
        "Shutting down, Sir. Until next time.",
        "Goodbye, Sir.",
        "Very good, Sir. Powering down FRIDAY.",
        "See you soon, Sir.",
        "FRIDAY standing by. Awaiting your next command.",
    ]
    
    WITTY_RESPONSES = [
        "As you wish, Sir.",
        "I live to serve, Sir.",
        "Your wish is my command, Sir.",
        "Absolutely, Sir.",
        "Consider it handled, Sir.",
        "Right on it, Sir.",
        "By your command, Sir.",
    ]
    
    @staticmethod
    def get_random(category):
        """Get random response from category"""
        if category == "greeting":
            return random.choice(FRIDAYPersonality.GREETINGS)
        elif category == "startup":
            return random.choice(FRIDAYPersonality.STARTUP_MESSAGES)
        elif category == "success":
            return random.choice(FRIDAYPersonality.SUCCESS_RESPONSES)
        elif category == "error":
            return random.choice(FRIDAYPersonality.ERROR_RESPONSES)
        elif category == "note":
            return random.choice(FRIDAYPersonality.NOTE_RESPONSES)
        elif category == "farewell":
            return random.choice(FRIDAYPersonality.FAREWELL_MESSAGES)
        elif category == "witty":
            return random.choice(FRIDAYPersonality.WITTY_RESPONSES)
        return "Yes, Sir?"
    
    @staticmethod
    def app_launch_message(app_name):
        """Get app launch message"""
        template = random.choice(FRIDAYPersonality.APP_LAUNCH_RESPONSES)
        return template.format(app=app_name)


# ==========================================================
# TEXT TO SPEECH ENGINE
# ==========================================================
class VoiceEngine:
    """Text-to-speech engine using pyttsx3"""
    
    def __init__(self):
        self.enabled = HAS_PYTTSX3
        if self.enabled:
            try:
                self.engine = pyttsx3.init()
                # Configure for FRIDAY's voice
                self.engine.setProperty('rate', 150)  # Speed
                self.engine.setProperty('volume', 0.9)  # Volume
                
                # Try to set female voice
                voices = self.engine.getProperty('voices')
                if len(voices) > 0:
                    # Use first female voice if available
                    for voice in voices:
                        if 'female' in voice.name.lower():
                            self.engine.setProperty('voice', voice.id)
                            break
                
                logger.info("VoiceEngine initialized with pyttsx3")
            except Exception as e:
                logger.error(f"VoiceEngine initialization error: {e}")
                self.enabled = False
        else:
            logger.warning("pyttsx3 not available. Voice disabled. Install with: pip install pyttsx3")
    
    def speak(self, text):
        """Speak text using TTS"""
        if not self.enabled:
            logger.warning(f"Voice disabled. Text: {text}")
            return
        
        try:
            logger.info(f"FRIDAY: {text}")
            self.engine.say(text)
            self.engine.runAndWait()
        except Exception as e:
            logger.error(f"Speech error: {e}")
    
    def speak_async(self, text):
        """Speak text asynchronously"""
        thread = threading.Thread(target=self.speak, args=(text,), daemon=True)
        thread.start()


# ==========================================================
# MODERN COLORS & THEME (Iron Man Edition)
# ==========================================================
class Theme:
    """Iron Man cyberpunk theme"""
    PRIMARY = "#FFB81C"           # Iron Man Gold
    SECONDARY = "#DC143C"         # Stark Red
    TERTIARY = "#00BFFF"          # Sky Blue
    BACKGROUND = "#0a0e27"        # Deep Blue-Black
    SURFACE = "#16213e"           # Surface Blue
    SURFACE_LIGHT = "#1f3a52"     # Lighter Surface
    SURFACE_LIGHTER = "#2a5f7f"   # Even Lighter
    TEXT_PRIMARY = "#ffffff"      # White
    TEXT_SECONDARY = "#b0b0b0"    # Gray
    SUCCESS = "#00ff41"           # Green
    ERROR = "#ff006e"             # Pink/Red
    WARNING = "#ffb800"           # Orange
    ACCENT = "#FFB81C"            # Gold


# ==========================================================
# DATABASE CLASS
# ==========================================================
class Database:
    """SQLite database handler"""
    
    def __init__(self, db_path="friday.db"):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self._create_tables()

    def _create_tables(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS preferences (
            key TEXT PRIMARY KEY, value TEXT
        )''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL, content TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        )''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS command_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            command TEXT, timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
            success BOOLEAN DEFAULT 1
        )''')
        self.conn.commit()

    def get_preference(self, key, default=None):
        self.cursor.execute("SELECT value FROM preferences WHERE key = ?", (key,))
        row = self.cursor.fetchone()
        return row[0] if row else default

    def set_preference(self, key, value):
        self.cursor.execute("REPLACE INTO preferences (key, value) VALUES (?, ?)", (key, str(value)))
        self.conn.commit()

    def search_notes(self, query=""):
        self.cursor.execute('''
            SELECT id, title, content, created_at
            FROM notes
            WHERE title LIKE ? OR content LIKE ?
            ORDER BY updated_at DESC
        ''', (f'%{query}%', f'%{query}%'))
        return self.cursor.fetchall()

    def get_note(self, note_id):
        self.cursor.execute("SELECT id, title, content, created_at, updated_at FROM notes WHERE id = ?", (note_id,))
        return self.cursor.fetchone()

    def add_note(self, title, content):
        self.cursor.execute("INSERT INTO notes (title, content) VALUES (?, ?)", (title, content))
        self.conn.commit()
        return self.cursor.lastrowid

    def update_note(self, note_id, title, content):
        self.cursor.execute('''
            UPDATE notes
            SET title=?, content=?, updated_at=CURRENT_TIMESTAMP
            WHERE id=?
        ''', (title, content, note_id))
        self.conn.commit()

    def delete_note(self, note_id):
        self.cursor.execute("DELETE FROM notes WHERE id=?", (note_id,))
        self.conn.commit()

    def add_command_history(self, command, success=True):
        self.cursor.execute(
            "INSERT INTO command_history (command, success) VALUES (?, ?)",
            (command, success)
        )
        self.conn.commit()

    def close(self):
        try:
            if self.cursor:
                self.cursor.close()
            if self.conn:
                self.conn.close()
        except Exception as e:
            logger.error(f"Database close error: {e}")


# ==========================================================
# VOICE ASSISTANT CLASS
# ==========================================================
class VoiceAssistant:
    """Speech recognition handler"""
    
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.microphone = self._get_microphone()
        self.is_listening = False
        self.language = "en-US"

    def _get_microphone(self):
        try:
            mics = sr.Microphone.list_microphone_names()
            if not mics:
                return None
            return sr.Microphone(device_index=0)
        except Exception:
            return None

    def listen(self):
        if not self.microphone:
            return False, "Microphone not found"
        try:
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
            text = self.recognizer.recognize_google(audio)
            return True, text
        except sr.WaitTimeoutError:
            return False, "Timeout"
        except sr.UnknownValueError:
            return False, "Could not understand"
        except Exception as e:
            return False, str(e)

    def start_listening(self, callback):
        if self.is_listening:
            return
        self.is_listening = True
        thread = threading.Thread(target=self._voice_listener_loop, args=(callback,), daemon=True)
        thread.start()

    def stop_listening(self):
        self.is_listening = False

    def _voice_listener_loop(self, callback):
        error_count = 0
        while self.is_listening:
            try:
                if not self.microphone:
                    error_count += 1
                    if error_count >= 5:
                        self.is_listening = False
                        break
                    time.sleep(2 ** error_count)
                    continue
                
                success, result = self.listen()
                if success:
                    error_count = 0
                    callback(result)
                else:
                    error_count += 1
                
                time.sleep(0.5)
            except Exception as e:
                logger.error(f"Voice error: {e}")
                error_count += 1
                if error_count >= 5:
                    self.is_listening = False


# ==========================================================
# APPLICATION LAUNCHER
# ==========================================================
class ApplicationLauncher:
    """Cross-platform app launcher"""
    
    APPS = {
        "excel": {"Windows": "start excel", "Darwin": "/Applications/Microsoft Excel.app"},
        "word": {"Windows": "start winword", "Darwin": "/Applications/Microsoft Word.app"},
        "powerpoint": {"Windows": "start powerpnt", "Darwin": "/Applications/Microsoft PowerPoint.app"},
        "outlook": {"Windows": "start outlook", "Darwin": "/Applications/Microsoft Outlook.app"},
        "notepad": {"Windows": "notepad", "Darwin": "/Applications/TextEdit.app"},
        "chrome": {"Windows": "start chrome", "Darwin": "/Applications/Google Chrome.app"},
        "firefox": {"Windows": "start firefox", "Darwin": "/Applications/Firefox.app"},
        "calculator": {"Windows": "calc", "Darwin": "/Applications/Calculator.app"},
        "terminal": {"Windows": "start cmd", "Darwin": "/Applications/Utilities/Terminal.app"},
    }

    @staticmethod
    def launch(app_name):
        sys_os = platform.system()
        app_name = app_name.lower().strip()
        try:
            if sys_os == "Windows":
                cmd = ApplicationLauncher.APPS.get(app_name, {}).get("Windows")
                if cmd:
                    subprocess.Popen(cmd, shell=True)
                    return True
            elif sys_os == "Darwin":
                app_path = ApplicationLauncher.APPS.get(app_name, {}).get("Darwin")
                if app_path:
                    if os.path.exists(app_path):
                        subprocess.Popen(["open", app_path])
                    else:
                        subprocess.Popen(["open", "-a", app_path])
                    return True
            return False
        except Exception:
            return False

    @staticmethod
    def get_available_apps():
        sys_os = platform.system()
        return [app for app, paths in ApplicationLauncher.APPS.items() if paths.get(sys_os)]


# ==========================================================
# FRIDAY APP - IRON MAN EDITION
# ==========================================================
class FRIDAYApp:
    """Main application with Iron Man FRIDAY AI"""
    
    def __init__(self):
        self.db = Database()
        self.voice = VoiceAssistant()
        self.app_launcher = ApplicationLauncher()
        self.voice_engine = VoiceEngine()
        self.listening = False

        self.root = Tk()
        self.root.title("FRIDAY - Iron Man AI Assistant")
        self.root.geometry("1300x850")
        self.root.minsize(1100, 750)
        self.root.config(bg=Theme.BACKGROUND)
        self.root.resizable(True, True)

        # Fonts
        self.title_font = tkFont.Font(family="Segoe UI", size=28, weight="bold")
        self.subtitle_font = tkFont.Font(family="Segoe UI", size=14, weight="bold")
        self.body_font = tkFont.Font(family="Segoe UI", size=10)
        self.code_font = tkFont.Font(family="Courier New", size=9)

        # Variables
        self.rate_var = IntVar(self.root, value=150)
        self.volume_var = DoubleVar(self.root, value=1.0)
        self.startup_var = BooleanVar(self.root, value=False)

        self.setup_ui()
        self.load_preferences()
        self.load_notes()
        
        # Welcome message
        greeting = FRIDAYPersonality.get_random("startup")
        self.log_friday(greeting)
        self.voice_engine.speak_async(greeting)

    def setup_ui(self):
        """Setup stunning Iron Man UI"""
        main = Frame(self.root, bg=Theme.BACKGROUND)
        main.pack(fill="both", expand=True, padx=20, pady=20)

        # ===== HEADER =====
        header = Frame(main, bg=Theme.BACKGROUND)
        header.pack(fill="x", pady=(0, 20))

        title = Label(
            header,
            text="⚡ F.R.I.D.A.Y ⚡",
            font=self.title_font,
            bg=Theme.BACKGROUND,
            fg=Theme.PRIMARY
        )
        title.pack(anchor="w")

        subtitle = Label(
            header,
            text="Tony Stark's AI Assistant | Female Replacement for J.A.R.V.I.S",
            font=self.subtitle_font,
            bg=Theme.BACKGROUND,
            fg=Theme.ACCENT
        )
        subtitle.pack(anchor="w", pady=(5, 0))

        divider = Canvas(main, height=3, bg=Theme.PRIMARY, highlightthickness=0)
        divider.pack(fill="x", pady=(0, 20))

        # ===== VOICE CONTROL =====
        voice_section = Frame(main, bg=Theme.SURFACE, relief="raised", bd=2)
        voice_section.pack(fill="x", pady=(0, 20))

        voice_inner = Frame(voice_section, bg=Theme.SURFACE)
        voice_inner.pack(fill="both", expand=True, padx=20, pady=20)

        voice_title = Label(
            voice_inner,
            text="🎤 VOICE CONTROL",
            font=self.subtitle_font,
            bg=Theme.SURFACE,
            fg=Theme.ACCENT
        )
        voice_title.pack(anchor="w", pady=(0, 15))

        voice_btn = Frame(voice_inner, bg=Theme.SURFACE)
        voice_btn.pack(fill="x")

        self.listen_btn = Button(
            voice_btn, text="🎙️ START LISTENING",
            command=self.start_listening,
            bg=Theme.SURFACE, fg=Theme.SUCCESS,
            width=20, bd=0, padx=10, pady=8,
            font=("Segoe UI", 10, "bold"), cursor="hand2"
        )
        self.listen_btn.pack(side="left", padx=5)

        stop_btn = Button(
            voice_btn, text="⏹️  STOP",
            command=self.stop_listening,
            bg=Theme.SURFACE, fg=Theme.ERROR,
            width=20, bd=0, padx=10, pady=8,
            font=("Segoe UI", 10, "bold"), cursor="hand2"
        )
        stop_btn.pack(side="left", padx=5)

        apps_btn = Button(
            voice_btn, text="📋 SHOW APPS",
            command=self.show_available_apps,
            bg=Theme.SURFACE, fg=Theme.ACCENT,
            width=20, bd=0, padx=10, pady=8,
            font=("Segoe UI", 10, "bold"), cursor="hand2"
        )
        apps_btn.pack(side="left", padx=5)

        self.status_var = StringVar(value="🔵 Standby | Ready for voice commands")
        status = Label(
            voice_inner,
            textvariable=self.status_var,
            font=self.body_font,
            bg=Theme.SURFACE,
            fg=Theme.PRIMARY,
            pady=15
        )
        status.pack(anchor="w", pady=(15, 0))

        # ===== QUICK LAUNCH =====
        app_section = Frame(main, bg=Theme.SURFACE_LIGHT, relief="raised", bd=2)
        app_section.pack(fill="x", pady=(0, 20))

        app_inner = Frame(app_section, bg=Theme.SURFACE_LIGHT)
        app_inner.pack(fill="both", expand=True, padx=20, pady=20)

        app_title = Label(
            app_inner,
            text="⚡ QUICK LAUNCH",
            font=self.subtitle_font,
            bg=Theme.SURFACE_LIGHT,
            fg=Theme.ACCENT
        )
        app_title.pack(anchor="w", pady=(0, 15))

        app_btn_frame = Frame(app_inner, bg=Theme.SURFACE_LIGHT)
        app_btn_frame.pack(fill="x")

        apps = [
            ("Excel", "📊", "excel"),
            ("Word", "📄", "word"),
            ("PowerPoint", "🎨", "powerpoint"),
            ("Chrome", "🌐", "chrome"),
            ("Notepad", "📝", "notepad"),
            ("Calculator", "🧮", "calculator"),
            ("Terminal", "💻", "terminal"),
            ("Outlook", "📧", "outlook"),
        ]

        for i, (name, icon, app) in enumerate(apps):
            btn = Button(
                app_btn_frame, text=f"{icon} {name}",
                command=lambda a=app: self.launch_app(a),
                width=14, bg=Theme.SURFACE_LIGHT, fg=Theme.ACCENT,
                bd=0, padx=10, pady=8,
                font=("Segoe UI", 9, "bold"), cursor="hand2"
            )
            btn.grid(row=i//4, column=i%4, padx=5, pady=5)

        # ===== NOTES SECTION =====
        notes_section = Frame(main, bg=Theme.SURFACE_LIGHTER, relief="raised", bd=2)
        notes_section.pack(fill="both", expand=True, pady=(0, 20))

        notes_inner = Frame(notes_section, bg=Theme.SURFACE_LIGHTER)
        notes_inner.pack(fill="both", expand=True, padx=20, pady=20)

        notes_title = Label(
            notes_inner,
            text="📝 NOTES",
            font=self.subtitle_font,
            bg=Theme.SURFACE_LIGHTER,
            fg=Theme.PRIMARY
        )
        notes_title.pack(anchor="w", pady=(0, 15))

        notes_btn_frame = Frame(notes_inner, bg=Theme.SURFACE_LIGHTER)
        notes_btn_frame.pack(fill="x", pady=(0, 15))

        Button(
            notes_btn_frame, text="➕ ADD",
            command=self.add_note,
            bg=Theme.SURFACE_LIGHTER, fg=Theme.PRIMARY,
            width=12, bd=0, padx=10, pady=8,
            font=("Segoe UI", 9, "bold"), cursor="hand2"
        ).pack(side="left", padx=5)

        Button(
            notes_btn_frame, text="✏️  EDIT",
            command=self.edit_note,
            bg=Theme.SURFACE_LIGHTER, fg=Theme.ACCENT,
            width=12, bd=0, padx=10, pady=8,
            font=("Segoe UI", 9, "bold"), cursor="hand2"
        ).pack(side="left", padx=5)

        Button(
            notes_btn_frame, text="🗑️  DELETE",
            command=self.delete_note,
            bg=Theme.SURFACE_LIGHTER, fg=Theme.ERROR,
            width=12, bd=0, padx=10, pady=8,
            font=("Segoe UI", 9, "bold"), cursor="hand2"
        ).pack(side="left", padx=5)

        self.notes_list = ttk.Treeview(
            notes_inner, columns=("Title", "Created"), show="headings", height=5
        )
        self.notes_list.heading("Title", text="Title")
        self.notes_list.heading("Created", text="Created")
        self.notes_list.column("Title", width=800)
        self.notes_list.column("Created", width=300)

        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Treeview', background=Theme.BACKGROUND, foreground=Theme.TEXT_PRIMARY,
                       fieldbackground=Theme.BACKGROUND, borderwidth=0)
        style.map('Treeview', background=[('selected', Theme.SURFACE)],
                 foreground=[('selected', Theme.PRIMARY)])

        self.notes_list.pack(fill="both", expand=True)

        # ===== FOOTER =====
        footer_divider = Canvas(main, height=2, bg=Theme.SURFACE_LIGHT, highlightthickness=0)
        footer_divider.pack(fill="x", pady=(20, 10))

        footer = Label(
            main,
            text=f"F.R.I.D.A.Y v3.5 | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Platform: {platform.system()}",
            font=self.body_font,
            bg=Theme.BACKGROUND,
            fg=Theme.TEXT_SECONDARY
        )
        footer.pack(anchor="e")

    def log_friday(self, message):
        """Log FRIDAY message"""
        logger.info(f"FRIDAY: {message}")
        self.status_var.set(f"FRIDAY: {message}")

    def load_preferences(self):
        try:
            self.rate_var.set(int(self.db.get_preference('voice_rate', 150)))
            self.volume_var.set(float(self.db.get_preference('voice_volume', 1.0)))
        except Exception as e:
            logger.error(f"Preferences error: {e}")

    def load_notes(self):
        self.notes_list.delete(*self.notes_list.get_children())
        notes = self.db.search_notes("")
        for note in notes:
            try:
                note_id, title, _, created = note
                self.notes_list.insert("", "end", iid=str(note_id), values=(title, created))
            except Exception as e:
                logger.error(f"Load note error: {e}")

    def add_note(self):
        title = simpledialog.askstring("New Note", "Enter title:")
        if not title:
            return
        content = simpledialog.askstring("New Note", "Enter content:")
        if content is None:
            return
        self.db.add_note(title, content)
        self.load_notes()
        msg = FRIDAYPersonality.get_random("note")
        self.log_friday(msg)
        self.voice_engine.speak_async(msg)

    def edit_note(self):
        selected = self.notes_list.selection()
        if not selected:
            messagebox.showwarning("⚠", "Please select a note")
            return
        try:
            note_id = int(selected[0])
            note = self.db.get_note(note_id)
            if not note:
                return
            title = simpledialog.askstring("Edit Note", "Title:", initialvalue=note[1])
            if title is None:
                return
            content = simpledialog.askstring("Edit Note", "Content:", initialvalue=note[2])
            if content is None:
                return
            self.db.update_note(note_id, title, content)
            self.load_notes()
            msg = FRIDAYPersonality.get_random("success")
            self.log_friday(msg)
            self.voice_engine.speak_async(msg)
        except Exception as e:
            messagebox.showerror("✗", str(e))

    def delete_note(self):
        selected = self.notes_list.selection()
        if not selected:
            messagebox.showwarning("⚠", "Please select a note")
            return
        try:
            note_id = int(selected[0])
            note = self.db.get_note(note_id)
            if not note:
                return
            if messagebox.askyesno("Delete", f"Delete '{note[1]}'?"):
                self.db.delete_note(note_id)
                self.load_notes()
                msg = FRIDAYPersonality.get_random("success")
                self.log_friday(msg)
                self.voice_engine.speak_async(msg)
        except Exception as e:
            messagebox.showerror("✗", str(e))

    def launch_app(self, app_name):
        success = self.app_launcher.launch(app_name)
        if success:
            msg = FRIDAYPersonality.app_launch_message(app_name)
            self.log_friday(msg)
            self.voice_engine.speak_async(msg)
            self.db.add_command_history(f"open {app_name}", True)
        else:
            msg = FRIDAYPersonality.get_random("error")
            self.log_friday(msg)
            self.voice_engine.speak_async(msg)

    def show_available_apps(self):
        available = self.app_launcher.get_available_apps()
        apps_list = "\n".join([f"• {app.upper()}" for app in available])
        msg = f"Available applications: {', '.join([a.upper() for a in available[:5]])}..."
        self.voice_engine.speak_async(msg)
        messagebox.showinfo("📋 Applications", f"Apps on {platform.system()}:\n\n{apps_list}")

    def start_listening(self):
        if not self.voice.microphone:
            msg = "I'm afraid the microphone is not responding, Sir."
            self.log_friday(msg)
            self.voice_engine.speak_async(msg)
            return
        self.listening = True
        msg = "Listening for commands, Sir."
        self.log_friday(msg)
        self.voice_engine.speak_async(msg)
        self.voice.start_listening(self.on_voice_command)
        self.status_var.set("🔴 LISTENING...")

    def stop_listening(self):
        self.listening = False
        self.voice.stop_listening()
        msg = "Listening stopped, Sir."
        self.log_friday(msg)
        self.voice_engine.speak_async(msg)
        self.status_var.set("🔵 Standby")

    def on_voice_command(self, text):
        logger.info(f"Voice command: {text}")
        text_lower = text.lower().strip()

        try:
            if "open" in text_lower:
                parts = text_lower.split("open", 1)
                if len(parts) > 1:
                    app_name = parts[1].strip().replace(" please", "").replace(" now", "").strip()
                    if app_name in self.app_launcher.get_available_apps():
                        self.root.after(0, lambda: self.launch_app(app_name))
                    else:
                        msg = f"I'm unable to locate {app_name}, Sir."
                        self.root.after(0, lambda: (self.log_friday(msg), self.voice_engine.speak_async(msg)))

            elif "add note" in text_lower or "new note" in text_lower:
                self.root.after(0, lambda: self.add_note())

            elif "stop" in text_lower or "exit" in text_lower or "quit" in text_lower:
                self.root.after(0, lambda: self.quit())

            else:
                msg = FRIDAYPersonality.get_random("witty")
                self.root.after(0, lambda: (self.log_friday(msg), self.voice_engine.speak_async(msg)))

            self.db.add_command_history(text, True)

        except Exception as e:
            logger.error(f"Command error: {e}")

    def quit(self):
        msg = FRIDAYPersonality.get_random("farewell")
        self.voice_engine.speak(msg)
        try:
            self.voice.stop_listening()
            self.db.close()
        except Exception:
            pass
        logger.info("FRIDAY shutting down")
        self.root.quit()
        self.root.destroy()

    def run(self):
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            self.quit()


# ==========================================================
# MAIN
# ==========================================================
if __name__ == "__main__":
    logger.info("=" * 70)
    logger.info("F.R.I.D.A.Y 0.1 EDITION")
    logger.info(f"Platform: {platform.system()} | Python: {platform.python_version()}")
    logger.info(f"Voice Enabled: {HAS_PYTTSX3}")
    logger.info("=" * 70)
    
    try:
        app = FRIDAYApp()
        app.run()
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)
