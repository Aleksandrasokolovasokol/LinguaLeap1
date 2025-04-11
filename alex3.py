import gradio as gr
from gtts import gTTS
import os
import random
import speech_recognition as sr

# Lesson chapters
chapters = {
    "chapter 1": {  # Greetings and Introductions
        "lessons": [
            {"word": "hello", "meaning": "A way to greet someone.", "example": "Hello! I’m Emma.", "ipa": "/həˈloʊ/"},
            {"word": "name", "meaning": "What someone is called.", "example": "My name is Emma.", "ipa": "/neɪm/"},
            {"word": "nice", "meaning": "Pleasant or good.", "example": "Nice to meet you!", "ipa": "/naɪs/"},
            {"word": "how", "meaning": "Asking about condition.", "example": "How are you?", "ipa": "/haʊ/"}
        ],
        "title": "Greetings and Introductions"
    },
    "chapter 2": {  # Everyday Objects
        "lessons": [
            {"word": "apple", "meaning": "A common fruit.", "example": "She ate an apple.", "ipa": "/ˈæp.əl/"},
            {"word": "shirt", "meaning": "A piece of clothing.", "example": "I wear a shirt.", "ipa": "/ʃɜːrt/"},
            {"word": "chair", "meaning": "Something to sit on.", "example": "The chair is big.", "ipa": "/tʃɛər/"},
            {"word": "book", "meaning": "A written work.", "example": "I read a book.", "ipa": "/bʊk/"}
        ],
        "title": "Everyday Objects"
    },
    "chapter 3": {  # Actions and Verbs
        "lessons": [
            {"word": "eat", "meaning": "To put food in your mouth.", "example": "I eat food.", "ipa": "/iːt/"},
            {"word": "walk", "meaning": "To move on foot.", "example": "I walk to school.", "ipa": "/wɔːk/"},
            {"word": "sit", "meaning": "To rest on a chair.", "example": "I sit on a chair.", "ipa": "/sɪt/"},
            {"word": "read", "meaning": "To look at words.", "example": "I read a book.", "ipa": "/riːd/"}
        ],
        "title": "Actions and Verbs"
    },
    "chapter 4": {  # Simple Questions and Answers
        "lessons": [
            {"word": "what", "meaning": "Asking about something.", "example": "What is this?", "ipa": "/wɒt/"},
            {"word": "where", "meaning": "Asking about place.", "example": "Where are you?", "ipa": "/wɛər/"},
            {"word": "yes", "meaning": "Agreeing.", "example": "Yes, I am.", "ipa": "/jɛs/"},
            {"word": "like", "meaning": "To enjoy something.", "example": "I like apples.", "ipa": "/laɪk/"}
        ],
        "title": "Simple Questions and Answers"
    }
}

# Avatar greetings
avatar_greetings = [
    "Hello! I’m Emma, your English tutor. Which chapter would you like?",
    "Hi there! I’m Emma, ready to teach you. Say 'Start Chapter 1' or another number!",
    "Welcome! I’m Emma, your avatar teacher. Tell me which chapter to begin!"
]

# Path to the avatar image (ensure it's in the same directory as this script)
AVATAR_IMAGE_PATH = "emma_avatar.jpg"

# Generate audio file
def text_to_speech(text, filename="lesson_output.mp3"):
    try:
        tts = gTTS(text=text, lang="en", slow=False)
        tts.save(filename)
        return filename
    except Exception:
        return None

# Recognize speech from audio file
def recognize_speech(audio_path):
    recognizer = sr.Recognizer()
    try:
        with sr.AudioFile(audio_path) as source:
            audio = recognizer.record(source)
        transcript = recognizer.recognize_google(audio)
        return transcript
    except sr.UnknownValueError:
        return "Sorry, I couldn’t understand you. Try again!"
    except sr.RequestError as e:
        return f"Speech recognition error: {str(e)}"
    except Exception as e:
        return f"Error processing audio: {str(e)}"

# Parse chapter selection
def parse_chapter_command(transcript):
    transcript = transcript.lower().strip()
    for chap in chapters.keys():
        if chap.replace(" ", "") in transcript.replace(" ", "") or chap.split()[1] in transcript:
            return chap
    return None

# State to track progress
class LessonState:
    def __init__(self):
        self.current_chapter = None
        self.lesson_index = 0

state = LessonState()

# Deliver lesson
def deliver_lesson(chapter, index):
    if chapter not in chapters or index >= len(chapters[chapter]["lessons"]):
        return f"Chapter {chapter.split()[1]} is complete! Say 'Start Chapter [number]' to begin another.", None
    
    lesson = chapters[chapter]["lessons"][index]
    lesson_text = (
        f"Lesson {index + 1} of {chapter.title()} - '{lesson['word']}':\n"
        f"Meaning: {lesson['meaning']}\n"
        f"Example: {lesson['example']}\n"
        f"Pronunciation (IPA): {lesson['ipa']}"
    )
    audio_file = text_to_speech(f"The word is {lesson['word']}. {lesson['example']}")
    return lesson_text, audio_file

# Select chapter
def select_chapter(audio_input):
    greeting = random.choice(avatar_greetings)
    if audio_input is None:
        return greeting, "Please record your voice to select a chapter (e.g., 'Start Chapter 1')!", None, "Select Chapter"
    
    transcript = recognize_speech(audio_input)
    chapter = parse_chapter_command(transcript)
    
    if chapter is None:
        return greeting, f"I didn’t catch that. Say 'Start Chapter 1', 'Chapter 2', etc. You said: '{transcript}'", None, "Select Chapter"
    
    state.current_chapter = chapter
    state.lesson_index = 0
    lesson_text, audio = deliver_lesson(chapter, 0)
    return greeting, lesson_text, audio, "Next Lesson"

# Move to next lesson
def next_lesson():
    if state.current_chapter is None:
        greeting = random.choice(avatar_greetings)
        return greeting, "Please select a chapter first by saying 'Start Chapter [number]'!", None, "Select Chapter"
    
    state.lesson_index += 1
    lesson_text, audio = deliver_lesson(state.current_chapter, state.lesson_index)
    return f"Continuing {state.current_chapter.title()}...", lesson_text, audio, "Next Lesson"

# Gradio interface
with gr.Blocks(title="AvatarEnglish - Voice-Based Chapter Lessons") as app:
    gr.Markdown("# AvatarEnglish: Voice-Based English Lessons")
    # Display the avatar image
    gr.Image(AVATAR_IMAGE_PATH, label="Meet Emma, Your English Teacher", width=200, height=200)
    gr.Markdown(
        "Hi! I’m Emma, your avatar teacher. Record your voice to choose a chapter!\n"
        "Say: 'Start Chapter 1', 'Chapter 2', 'Chapter 3', or 'Chapter 4'\n"
        "Then click 'Next Lesson' to move through the lessons."
    )
    
    with gr.Row():
        with gr.Column():
            voice_input = gr.Audio(label="Record Your Chapter Choice", type="filepath")
            select_btn = gr.Button("Select Chapter")
            next_btn = gr.Button("Next Lesson")
        
        with gr.Column():
            greeting_output = gr.Textbox(label="Emma Says")
            lesson_output = gr.Textbox(label="Lesson Content")
            audio_output = gr.Audio(label="Listen Here")
            status_output = gr.Textbox(label="Current Action", value="Select Chapter")
    
    select_btn.click(
        fn=select_chapter,
        inputs=[voice_input],
        outputs=[greeting_output, lesson_output, audio_output, status_output]
    )
    next_btn.click(
        fn=next_lesson,
        inputs=[],
        outputs=[greeting_output, lesson_output, audio_output, status_output]
    )

app.launch()