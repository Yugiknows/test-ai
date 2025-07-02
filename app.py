import streamlit as st
import os
import tempfile
import logging
import time
from typing import Optional, List, Dict
from utils import get_answer, text_to_speech, autoplay_audio, speech_to_text
from audio_recorder_streamlit import audio_recorder
from streamlit_float import *

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Float feature initialization
float_init()

# Enhanced styling with modern design
st.markdown("""
<style>
/* Main app styling */
.main .block-container {
    padding-top: 2rem;
    padding-bottom: 8rem;
    max-width: 900px;
    margin: 0 auto;
}

/* Title styling with enhanced gradient */
h1 {
    color: #1B5E20 !important;
    font-family: 'Segoe UI', 'Arial', sans-serif;
    font-weight: 800;
    text-align: center;
    margin-bottom: 2rem;
    padding: 1.5rem;
    background: linear-gradient(135deg, #E8F5E8 0%, #C8E6C9 50%, #A5D6A7 100%);
    border-radius: 20px;
    border-left: 6px solid #2E7D32;
    box-shadow: 0 4px 20px rgba(46, 125, 50, 0.15);
    text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}

/* Enhanced subtitle styling */
.subtitle {
    text-align: center;
    color: #2E7D32;
    font-size: 1.1rem;
    margin-bottom: 2rem;
    padding: 1rem;
    background: rgba(232, 245, 232, 0.5);
    border-radius: 10px;
    font-weight: 500;
}

/* Chat message container styling */
.stChatMessage {
    background: white !important;
    border-radius: 20px !important;
    padding: 1.2rem !important;
    margin: 1rem 0 !important;
    box-shadow: 0 3px 15px rgba(0, 0, 0, 0.08) !important;
    border: 1px solid #E0E0E0 !important;
    transition: transform 0.2s ease !important;
}

.stChatMessage:hover {
    transform: translateY(-2px) !important;
}

/* User message styling */
.stChatMessage[data-testid="chat-message-user"] {
    background: linear-gradient(135deg, #E3F2FD 0%, #BBDEFB 50%, #90CAF9 100%) !important;
    border-left: 5px solid #1976D2 !important;
    margin-left: 3rem !important;
    margin-right: 1rem !important;
}

/* Assistant message styling */
.stChatMessage[data-testid="chat-message-assistant"] {
    background: linear-gradient(135deg, #E8F5E8 0%, #C8E6C9 50%, #A5D6A7 100%) !important;
    border-left: 5px solid #2E7D32 !important;
    margin-right: 3rem !important;
    margin-left: 1rem !important;
}

/* Chat message content */
.stChatMessage > div {
    font-size: 1.1rem !important;
    line-height: 1.7 !important;
    color: #1B5E20 !important;
    font-weight: 500 !important;
}

/* Enhanced spinner styling */
.stSpinner > div {
    border-top-color: #2E7D32 !important;
    border-width: 3px !important;
}

/* Success/Info message styling */
.stSuccess, .stInfo {
    border-radius: 15px !important;
    border-left: 5px solid #2E7D32 !important;
    padding: 1rem !important;
    margin: 1rem 0 !important;
}

/* Footer container styling */
.footer-container {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    background: linear-gradient(180deg, rgba(255,255,255,0) 0%, rgba(255,255,255,0.95) 30%, rgba(255,255,255,1) 100%);
    padding: 2rem 1rem 1rem 1rem;
    z-index: 999;
    backdrop-filter: blur(10px);
    border-top: 1px solid rgba(46, 125, 50, 0.1);
}

/* Audio recorder button enhancement */
.stAudioRecorder button {
    background: linear-gradient(135deg, #2E7D32 0%, #388E3C 100%) !important;
    border: none !important;
    border-radius: 50% !important;
    width: 70px !important;
    height: 70px !important;
    box-shadow: 0 4px 20px rgba(46, 125, 50, 0.3) !important;
    transition: all 0.3s ease !important;
}

.stAudioRecorder button:hover {
    transform: scale(1.1) !important;
    box-shadow: 0 6px 25px rgba(46, 125, 50, 0.4) !important;
}

/* Responsive design */
@media (max-width: 768px) {
    .main .block-container {
        padding-left: 1rem;
        padding-right: 1rem;
        padding-bottom: 10rem;
    }
    
    .stChatMessage[data-testid="chat-message-user"] {
        margin-left: 0.5rem !important;
        margin-right: 0rem !important;
    }
    
    .stChatMessage[data-testid="chat-message-assistant"] {
        margin-right: 0.5rem !important;
        margin-left: 0rem !important;
    }
    
    h1 {
        font-size: 1.8rem !important;
        padding: 1rem !important;
    }
    
    .subtitle {
        font-size: 1rem !important;
        padding: 0.8rem !important;
    }
}

/* Loading animation */
@keyframes pulse {
    0% { opacity: 0.6; }
    50% { opacity: 1; }
    100% { opacity: 0.6; }
}

.loading-text {
    animation: pulse 2s ease-in-out infinite;
}
</style>
""", unsafe_allow_html=True)

class AgriHelperApp:
    """Voice-enabled farming assistant application."""
    def __init__(self):
        self.initialize_session_state()

    def initialize_session_state(self) -> None:
        if "messages" not in st.session_state:
            st.session_state.messages = [
                {"role": "assistant", "content": "Hi! How may I assist you today?"}
            ]

    def run(self) -> None:
        st.title("🌱 AgriHelper")
        # Display conversation history
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.write(message["content"])

        # Respond if needed
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

        # Float the footer container and place mic at bottom
        footer_container = st.container()
        with footer_container:
            audio_bytes = audio_recorder()
            if audio_bytes:
                with st.spinner("Transcribing..."):
                    webm_path = tempfile.NamedTemporaryFile(delete=False, suffix='.webm').name
                    with open(webm_path, "wb") as f:
                        f.write(audio_bytes)
                    transcript = speech_to_text(webm_path)
                    os.remove(webm_path)
                    if transcript:
                        st.session_state.messages.append({"role": "user", "content": transcript})
        footer_container.float("bottom: 0rem;")

        # Sidebar with tips and examples
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
    app = AgriHelperApp()
    app.run()

if __name__ == "__main__":
    main()
