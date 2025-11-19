import os
import asyncio
import edge_tts
from groq import Groq

class MockInterviewer:
    def __init__(self, api_key):
        if not api_key:
            raise ValueError("API Key missing")
        self.client = Groq(api_key=api_key)
        # Use the new supported model
        self.llm_model = "llama-3.3-70b-versatile" 
        self.stt_model = "distil-whisper-large-v3-en"

    def transcribe_audio(self, audio_file):
        """
        Converts user audio (bytes) to text using Groq Whisper.
        """
        try:
            transcription = self.client.audio.transcriptions.create(
                file=("input.wav", audio_file.read()), # standard format for API
                model=self.stt_model,
                response_format="text",
                language="en"
            )
            return transcription
        except Exception as e:
            return f"Error transcribing: {e}"

    def get_ai_response(self, history):
        """
        Generates the next interview question/feedback based on chat history.
        """
        # System prompt to define persona
        system_prompt = {
            "role": "system",
            "content": (
                "You are a senior technical interviewer. "
                "1. Keep your responses concise (under 3 sentences). "
                "2. Evaluate the candidate's previous answer briefly. "
                "3. Ask ONE follow-up technical question based on their resume context. "
                "4. Do not be overly polite; be professional and direct."
            )
        }
        
        messages = [system_prompt] + history
        
        completion = self.client.chat.completions.create(
            model=self.llm_model,
            messages=messages,
            temperature=0.7,
            max_tokens=1024
        )
        return completion.choices[0].message.content

    async def _generate_audio_file(self, text, output_file):
        """Async helper for EdgeTTS"""
        # voices: en-US-AriaNeural, en-US-GuyNeural, etc.
        communicate = edge_tts.Communicate(text, "en-US-AriaNeural")
        await communicate.save(output_file)

    def text_to_speech(self, text):
        """
        Converts AI text to an audio file path.
        """
        output_filename = "temp_response.mp3"
        try:
            asyncio.run(self._generate_audio_file(text, output_filename))
            return output_filename
        except Exception as e:
            print(f"TTS Error: {e}")
            return None