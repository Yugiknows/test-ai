import streamlit as st
import os
from utils import get_answer, text_to_speech, autoplay_audio, speech_to_text
from audio_recorder_streamlit import audio_recorder
from streamlit_float import *

# Float feature initialization
float_init()

# Add beautiful styling
st.markdown("""
<style>
/* Main app styling */
.main .block-container {
    padding-top: 2rem;
    padding-bottom: 6rem;
    max-width: 800px;
}

/* Title styling */
h1 {
    color: #2E7D32 !important;
    font-family: 'Arial', sans-serif;
    font-weight: 700;
    text-align: center;
    margin-bottom: 2rem;
    padding: 1rem;
    background: linear-gradient(135deg, #E8F5E8 0%, #C8E6C9 100%);
    border-radius: 15px;
    border-left: 5px solid #2E7D32;
    box-shadow: 0 2px 10px rgba(46, 125, 50, 0.1);
}

/* Chat message container styling */
.stChatMessage {
    background: white !important;
    border-radius: 15px !important;
    padding: 1rem !important;
    margin: 0.5rem 0 !important;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1) !important;
    border: 1px solid #E0E0E0 !important;
}

/* User message styling */
.stChatMessage[data-testid="chat-message-user"] {
    background: linear-gradient(135deg, #E3F2FD 0%, #BBDEFB 100%) !important;
    border-left: 4px solid #1976D2 !important;
    margin-left: 2rem !important;
}

/* Assistant message styling */
.stChatMessage[data-testid="chat-message-assistant"] {
    background: linear-gradient(135deg, #E8F5E8 0%, #C8E6C9 100%) !important;
    border-left: 4px solid #2E7D32 !important;
    margin-right: 2rem !important;
}

/* Chat message content */
.stChatMessage > div {
    font-size: 1.1rem !important;
    line-height: 1.6 !important;
    color: #1B5E20 !important;
}

/* Spinner styling */
.stSpinner > div {
    border-top-color: #2E7D32 !important;
}

/* Responsive design */
@media (max-width: 768px) {
    .main .block-container {
        padding-left: 1rem;
        padding-right: 1rem;
    }
    
    .stChatMessage[data-testid="chat-message-user"] {
        margin-left: 0.5rem !important;
    }
    
    .stChatMessage[data-testid="chat-message-assistant"] {
        margin-right: 0.5rem !important;
    }
    
    h1 {
        font-size: 1.5rem !important;
    }
}
</style>
""", unsafe_allow_html=True)

def initialize_session_state():
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "system", "content": "You are a helpful assistant providing farming advice in detailed sentences."}
        ]

# Initialize session state
initialize_session_state()

# Display title
st.title("🌱 AgriHelper")
st.markdown("**Speak to get farming advice!**")

# Create footer container for the microphone
footer_container = st.container()
with footer_container:
    audio_bytes = audio_recorder()
    
# Handle audio input
if audio_bytes:
    with st.spinner("🎤 Listening to your question..."):
        webm_file_path = "temp_audio.mp3"
        with open(webm_file_path, "wb") as f:
            f.write(audio_bytes)
        transcript = speech_to_text(webm_file_path)
        if transcript:
            st.success(f"You asked: {transcript}")
            
            # Add user message to conversation history
            st.session_state.messages.append({"role": "user", "content": transcript})
            
            with st.spinner("🤔 Thinking about your farming question..."):
                final_response = get_answer(st.session_state.messages)
            
            with st.spinner("🔊 Speaking my response..."):    
                audio_file = text_to_speech(final_response)
                autoplay_audio(audio_file)
            
            st.info(f"Assistant says: {final_response}")
            
            # Add assistant response to conversation history
            st.session_state.messages.append({"role": "assistant", "content": final_response})
            
            # Clean up files
            os.remove(webm_file_path)
            os.remove(audio_file)
            
# Float the footer container
footer_container.float("bottom: 0rem;")
