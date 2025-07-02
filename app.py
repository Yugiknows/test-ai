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
dlogging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Float feature initialization
float_init()

class AgriHelperApp:
    """Main application class for AgriHelper voice-enabled farming assistant."""
    
    def __init__(self):
        self.initialize_session_state()
        
    def initialize_session_state(self) -> None:
        if "messages" not in st.session_state:
            st.session_state.messages = [
                {"role": "system", "content": 
                 "You are AgriHelper, an expert farming assistant. Provide detailed, practical farming advice in clear, conversational sentences. Focus on actionable solutions and consider local farming practices."}
            ]
        if "conversation_count" not in st.session_state:
            st.session_state.conversation_count = 0

    def run(self) -> None:
        st.title("🌱 AgriHelper")
        if st.session_state.conversation_count > 0:
            st.markdown(f"*Conversations: {st.session_state.conversation_count}*")

        # Display history
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.write(message["content"])

        # Record audio
        audio_bytes = audio_recorder()
        if audio_bytes:
            # Save and transcribe
            with tempfile.NamedTemporaryFile(delete=False, suffix='.webm') as tmp:
                tmp.write(audio_bytes)
                tmp_path = tmp.name
            transcript = speech_to_text(tmp_path)
            os.remove(tmp_path)
            if transcript:
                st.session_state.messages.append({"role": "user", "content": transcript})

        # If last message isn’t from assistant, respond
        if st.session_state.messages[-1]["role"] != "assistant":
            with st.chat_message("assistant"):
                with st.spinner("Thinking🤔..."):
                    final_response = get_answer(st.session_state.messages)
                with st.spinner("Generating audio response..."):
                    audio_file = text_to_speech(final_response)
                    autoplay_audio(audio_file)
                st.write(final_response)
                st.session_state.messages.append({"role": "assistant", "content": final_response})
                os.remove(audio_file)
                st.session_state.conversation_count += 1

        # Float recorder
        footer = st.container()
        footer.float("bottom: 0rem;")

        # Sidebar tips
        with st.sidebar:
            st.markdown("### 💡 Tips for better results:")
            st.markdown("- Speak clearly and at normal pace\n- Ask specific farming questions\n- Mention your crop type and location if relevant\n- Wait for the complete response before asking again")


def main():
    app = AgriHelperApp()
    app.run()

if __name__ == "__main__":
    main()
