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
    """Initialize session state variables"""
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Hi! How may I assist you today?"}
        ]

# Initialize session state
initialize_session_state()

# Display title
st.title("🌱 AgriHelper")

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Handle text input
if prompt := st.chat_input("Ask me anything about agriculture..."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Get and display assistant response
    with st.chat_message("assistant"):
        with st.spinner("🤔 Thinking..."):
            response = get_answer(prompt)
            st.markdown(response)
            
            # Convert response to speech
            try:
                audio_file = text_to_speech(response)
                autoplay_audio(audio_file)
            except Exception as e:
                st.error(f"Error generating audio: {str(e)}")
    
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})

# Create footer container for the microphone
footer_container = st.container()

with footer_container:
    # Audio recorder
    audio_bytes = audio_recorder(
        text="🎤 Click to record your question",
        recording_color="#2E7D32",
        neutral_color="#757575",
        icon_name="microphone",
        icon_size="2x",
        key="audio_recorder"
    )

# Handle audio input
if audio_bytes:
    with st.spinner("🎤 Transcribing..."):
        # Save audio bytes to temporary file
        webm_file_path = "temp_audio.mp3"
        with open(webm_file_path, "wb") as f:
            f.write(audio_bytes)
        
        try:
            # Transcribe audio to text
            question = speech_to_text(webm_file_path)
            
            if question:
                # Add user message to chat
                st.session_state.messages.append({"role": "user", "content": question})
                
                # Get assistant response
                with st.spinner("🤔 Processing your question..."):
                    final_response = get_answer(question)
                    
                # Add assistant response to chat
                st.session_state.messages.append({"role": "assistant", "content": final_response})
                
                # Convert response to speech
                try:
                    audio_file = text_to_speech(final_response)
                    autoplay_audio(audio_file)
                except Exception as e:
                    st.error(f"Error generating audio response: {str(e)}")
                
                # Rerun to update the chat display
                st.rerun()
            else:
                st.error("Could not transcribe audio. Please try again.")
                
        except Exception as e:
            st.error(f"Error processing audio: {str(e)}")
        
        finally:
            # Clean up temporary file
            if os.path.exists(webm_file_path):
                os.remove(webm_file_path)

# Float the footer container to bottom
footer_container.float("bottom: 0rem;")
