import streamlit as st
import os
import tempfile
import logging
import time
from typing import Optional
from utils import get_answer, text_to_speech, autoplay_audio, speech_to_text
from audio_recorder_streamlit import audio_recorder
from streamlit_float import *

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Float feature initialization
float_init()

class AgriHelperApp:
    """Main application class for AgriHelper voice-enabled farming assistant."""
    
    def __init__(self):
        self.initialize_session_state()
        
    def initialize_session_state(self) -> None:
        """Initialize session state with default values."""
        if "messages" not in st.session_state:
            st.session_state.messages = [
                {
                    "role": "system", 
                    "content": (
                        "You are AgriHelper, an expert farming assistant. "
                        "Provide detailed, practical farming advice in clear, conversational sentences. "
                        "Focus on actionable solutions and consider local farming practices."
                    )
                }
            ]
        if "conversation_count" not in st.session_state:
            st.session_state.conversation_count = 0
        
    def display_header(self) -> None:
        """Display the application header and title."""
        st.markdown("""
        <style>
        .main .block-container { padding-top: 2rem; padding-bottom: 8rem; max-width: 900px; margin: 0 auto; }
        h1 { color: #1B5E20 !important; font-family: 'Segoe UI', Arial, sans-serif; font-weight: 800;
             text-align: center; margin-bottom: 2rem; padding: 1.5rem;
             background: linear-gradient(135deg, #E8F5E8 0%, #C8E6C9 50%, #A5D6A7 100%);
             border-radius: 20px; border-left: 6px solid #2E7D32;
             box-shadow: 0 4px 20px rgba(46, 125, 50, 0.15);
             text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1); }
        .subtitle { text-align: center; color: #2E7D32; font-size: 1.1rem;
                     margin-bottom: 2rem; padding: 1rem; background: rgba(232, 245, 232, 0.5);
                     border-radius: 10px; font-weight: 500; }
        </style>
        """, unsafe_allow_html=True)
        st.title("🌱 AgriHelper")
        st.markdown(
            '<div class="subtitle">🎤 <strong>Speak to get expert farming advice - AI responds with voice!</strong> 🔊</div>',
            unsafe_allow_html=True
        )
        if st.session_state.conversation_count > 0:
            st.markdown(f"*Conversations: {st.session_state.conversation_count}*")

    def display_conversation_history(self) -> None:
        """Display the conversation history in a chat-like format."""
        for message in st.session_state.messages[1:]:  # Skip system message
            with st.chat_message(message["role"]):
                st.write(message["content"])

    def safe_file_cleanup(self, file_path: str) -> None:
        """Safely remove temporary files with error handling."""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"Successfully cleaned up file: {file_path}")
        except Exception as e:
            logger.error(f"Error cleaning up file {file_path}: {str(e)}")

    def process_audio_input(self, audio_bytes: bytes) -> Optional[str]:
        """Process audio input and return transcript."""
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix='.webm') as tmp:
                tmp.write(audio_bytes)
                tmp_path = tmp.name
            transcript = speech_to_text(tmp_path)
            self.safe_file_cleanup(tmp_path)
            return transcript
        except Exception as e:
            logger.error(f"Error processing audio input: {str(e)}")
            st.error("❌ Sorry, I couldn't process your audio. Please try again.")
            return None

    def generate_response(self, transcript: str) -> Optional[str]:
        """Generate response from the AI model."""
        try:
            st.session_state.messages.append({"role": "user", "content": transcript})
            response = get_answer(st.session_state.messages)
            st.session_state.messages.append({"role": "assistant", "content": response})
            st.session_state.conversation_count += 1
            return response
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            st.error("❌ Sorry, I couldn't generate a response. Please try again.")
            return None

    def handle_text_to_speech(self, text: str) -> None:
        """Convert text to speech and play audio."""
        try:
            audio_file = text_to_speech(text)
            if audio_file and os.path.exists(audio_file):
                logger.info(f"Playing audio file: {audio_file}")
                autoplay_audio(audio_file)
                time.sleep(1.0)
                self.safe_file_cleanup(audio_file)
            else:
                logger.error("Audio file not generated or missing")
                st.warning("⚠️ Audio response could not be generated.")
        except Exception as e:
            logger.error(f"Error with text-to-speech: {str(e)}")
            st.warning("⚠️ Could not play audio response. Please try again.")

    def run(self) -> None:
        """Main application loop."""
        self.display_header()
        self.display_conversation_history()
        footer = st.container()
        with footer:
            cols = st.columns([1, 2, 1])
            with cols[1]:
                audio_bytes = audio_recorder(
                    text="Click to record",
                    recording_color="#ff0000",
                    neutral_color="#2E7D32",
                    icon_name="microphone",
                    icon_size="2x"
                )
        if audio_bytes:
            if ("last_audio" not in st.session_state or
                st.session_state.last_audio != audio_bytes):
                st.session_state.last_audio = audio_bytes
                with st.spinner("🎤 Processing your voice..."):
                    transcript = self.process_audio_input(audio_bytes)
                if transcript:
                    with st.chat_message("user"):
                        st.write(transcript)
                    with st.spinner("🤔 Thinking..."):
                        response = self.generate_response(transcript)
                    if response:
                        with st.chat_message("assistant"):
                            st.write(response)
                        self.handle_text_to_speech(response)
                st.rerun()
        footer.float("bottom: 0rem;")
        with st.sidebar:
            st.markdown("### 💡 Tips for better results:")
            st.markdown("""
            - Speak clearly and at normal pace
            - Ask specific farming questions
            - Mention your crop type and location if relevant
            - Wait for the complete response before asking again
            """)
            st.markdown("### 🌾 Example questions:")
            st.markdown("""
            - "How do I treat tomato blight?"
            - "What's the best fertilizer for corn?"
            - "When should I plant wheat in winter?"
            - "How to prevent pest damage in vegetables?"
            """)


def main():
    try:
        app = AgriHelperApp()
        app.run()
    except Exception as e:
        logger.error(f"Application error: {str(e)}")
        st.error("❌ Application encountered an error. Please refresh the page.")

if __name__ == "__main__":
    main()
