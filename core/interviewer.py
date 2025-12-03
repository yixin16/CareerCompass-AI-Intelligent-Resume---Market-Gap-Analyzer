import os
import asyncio
import edge_tts

try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False

class MockInterviewer:
    def __init__(self, api_key):
        if not api_key:
            raise ValueError("API Key missing. Please configure it in the sidebar.")
        self.client = Groq(api_key=api_key)
        self.llm_model = "llama-3.3-70b-versatile" 
        self.stt_model = "whisper-large-v3-turbo"

    def transcribe_audio(self, audio_bytes):
        """
        Converts user audio (bytes) to text using Groq Whisper.
        """
        try:
            # Create a virtual file-like object or reset the pointer if it's a file
            if hasattr(audio_bytes, 'seek'):
                audio_bytes.seek(0) 
                audio_data = audio_bytes.read()
                # IMPORTANT: Reset pointer so if we compare it later or read again, it works
                audio_bytes.seek(0) 
            else:
                audio_data = audio_bytes

            transcription = self.client.audio.transcriptions.create(
                file=("input.wav", audio_data), 
                model=self.stt_model,
                response_format="text",
                language="en" 
            )
            return transcription
        except Exception as e:
            return f"Error transcribing audio: {e}"

    def get_ai_response(self, history, target_role="Software Engineer", resume_context=""):
        """
        Generates the next interview question AND a sample answer in JSON format.
        """
        import json # Ensure this is imported
        
        # 🧠 DYNAMIC SYSTEM PROMPT
        system_content = (
            f"You are an expert technical interviewer for a {target_role} role. "
            f"Candidate Context: {resume_context}. "
            "Your task: Analyze the chat history and generate the NEXT response.\n\n"
            "OUTPUT FORMAT: Return a valid JSON object with two keys:\n"
            "1. 'question': Your response to the candidate (feedback + next question). Keep it conversational and under 3 sentences.\n"
            "2. 'sample_answer': A concise, 'Senior-Level' example answer to the question you just asked. Use the STAR method if applicable.\n\n"
            "RULES:\n"
            "- If the candidate's previous answer was wrong, correct them gently in the 'question' field.\n"
            "- Do not output markdown code blocks, just the raw JSON."
        )

        messages = [{"role": "system", "content": system_content}]
        
        # Clean history to ensure we send valid string content to the LLM
        for msg in history:
            # We only send the 'content' text to the LLM, not the hidden sample answers
            messages.append({"role": msg["role"], "content": msg["content"]})
        
        try:
            completion = self.client.chat.completions.create(
                model=self.llm_model,
                messages=messages,
                temperature=0.6, 
                max_tokens=600,
                response_format={"type": "json_object"} # Force JSON mode
            )
            
            response_text = completion.choices[0].message.content
            return json.loads(response_text)
            
        except Exception as e:
            # Fallback if JSON fails
            return {
                "question": "Could you elaborate on your experience with that technology?",
                "sample_answer": "I have used X to build Y, resulting in Z improvement."
            }

    async def _generate_audio_file(self, text, output_file):
        """Async helper for EdgeTTS"""
        # "en-US-AriaNeural" is a professional, clear female voice
        # "en-US-ChristopherNeural" is a professional male voice
        communicate = edge_tts.Communicate(text, "en-US-AriaNeural")
        await communicate.save(output_file)

    def text_to_speech(self, text):
        """
        Converts AI text to an audio file path safely handling Streamlit's event loop.
        """
        output_filename = "temp_response.mp3"
        try:
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():

                    import nest_asyncio
                    nest_asyncio.apply()
                    asyncio.run(self._generate_audio_file(text, output_filename))
                else:
                    asyncio.run(self._generate_audio_file(text, output_filename))
            except RuntimeError:
                asyncio.run(self._generate_audio_file(text, output_filename))
                
            return output_filename
        except Exception as e:
            print(f"TTS Error: {e}")
            return None