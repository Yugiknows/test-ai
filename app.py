import streamlit as st
import os
from utils import get_answer, text_to_speech, autoplay_audio, speech_to_text
from audio_recorder_streamlit import audio_recorder
from streamlit_float import *

# Float feature initialization
float_init()

def inject_custom_css():
    """Inject custom CSS for enhanced styling"""
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
    
    /* Audio recorder styling */
    .audio-recorder-container {
        position: fixed !important;
        bottom: 20px !important;
        left: 50% !important;
        transform: translateX(-50%) !important;
        z-index: 999 !important;
        background: white !important;
        border-radius: 50px !important;
        padding: 10px !important;
        box-shadow: 0 4px 20px rgba(46, 125, 50, 0.3) !important;
        border: 3px solid #2E7D32 !important;
    }
    
    /* Custom button styling for audio recorder */
    .stButton > button {
        background: linear-gradient(135deg, #2E7D32 0%, #388E3C 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 25px !important;
        padding: 0.5rem 1.5rem !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 2px 8px rgba(46, 125, 50, 0.3) !important;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #1B5E20 0%, #2E7D32 100%) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 12px rgba(46, 125, 50, 0.4) !important;
    }
    
    /* Loading animation enhancement */
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.5; }
        100% { opacity: 1; }
    }
    
    .stSpinner {
        animation: pulse 1.5s ease-in-out infinite;
    }
    
    /* Sidebar styling if used */
    .css-1d391kg {
        background-color: #E8F5E8 !important;
    }
    
    /* Footer area styling */
    .footer-container {
        position: fixed !important;
        bottom: 0 !important;
        left: 0 !important;
        right: 0 !important;
        background: linear-gradient(180deg, transparent 0%, rgba(241, 248, 233, 0.9) 50%, rgba(241, 248, 233, 1) 100%) !important;
        padding: 20px !important;
        z-index: 998 !important;
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
    
    /* Success message styling */
    .success-message {
        background: linear-gradient(135deg, #E8F5E8 0%, #C8E6C9 100%);
        border: 1px solid #4CAF50;
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
        color: #1B5E20;
        font-weight: 500;
    }
    
    /* Error message styling */
    .error-message {
        background: linear-gradient(135deg, #FFEBEE 0%, #FFCDD2 100%);
        border: 1px solid #F44336;
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
        color: #B71C1C;
        font-weight: 500;
    }
    
    /* Custom scrollbar */
    .main::-webkit-scrollbar {
        width: 8px;
    }
    
    .main::-webkit-scrollbar-track {
        background: #E8F5E8;
        border-radius: 10px;
    }
    
    .main::-webkit-scrollbar-thumb {
        background: #2E7D32;
        border-radius: 10px;
    }
    
    .main::-webkit-scrollbar-thumb:hover {
        background: #1B5E20;
    }
    </style>
    """, unsafe_allow_html=True)

def initialize_session_state():
    """Initialize session state variables"""
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Hi! How may I assist you today?"}
        ]

def display_header():
    """Display the enhanced header"""
    st.markdown("""
    <div style="text-align: center; margin-bottom: 2rem;">
        <h1>🌱 AgriHelper</h1>
        <p style="color: #2E7D32; font-size: 1.1rem; font-weight: 500; margin: 0;">
            Your AI-powered agricultural assistant with voice capabilities
        </p>
    </div>
    """, unsafe_allow_html=True)

def display_chat_messages():
    """Display chat messages with enhanced styling"""
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

def handle_audio_input(audio_bytes):
    """Handle audio input processing"""
    if audio_bytes:
        # Write the audio bytes to a file
        with st.spinner("🎤 Transcribing your voice..."):
            webm_file_path = "temp_audio.mp3"
            with open(webm_file_path, "wb") as f:
                f.write(audio_bytes)

            transcript = speech_to_text(webm_file_path)
            if transcript:
                st.session_state.messages.append({"role": "user", "content": transcript})
                with st.chat_message("user"):
                    st.write(transcript)
                os.remove(webm_file_path)
                return True
    return False

def generate_assistant_response():
    """Generate and display assistant response"""
    if st.session_state.messages[-1]["role"] != "assistant":
        with st.chat_message("assistant"):
            with st.spinner("🤔 Thinking..."):
                final_response = get_answer(st.session_state.messages)
            
            with st.spinner("🔊 Generating audio response..."):    
                audio_file = text_to_speech(final_response)
                autoplay_audio(audio_file)
            
            st.write(final_response)
            st.session_state.messages.append({"role": "assistant", "content": final_response})
            os.remove(audio_file)

def main():
    """Main application function"""
    # Set page config for better mobile experience
    st.set_page_config(
        page_title="AgriHelper - AI Agricultural Assistant",
        page_icon="🌱",
        layout="centered",
        initial_sidebar_state="collapsed"
    )
    
    # Inject custom CSS
    inject_custom_css()
    
    # Initialize session state
    initialize_session_state()
    
    # Display header
    display_header()
    
    # Create footer container for the microphone with enhanced styling
    footer_container = st.container()
    with footer_container:
        st.markdown('<div class="audio-recorder-container">', unsafe_allow_html=True)
        audio_bytes = audio_recorder(
            text="🎤 Click to speak",
            recording_color="#2E7D32",
            neutral_color="#757575",
            icon_size="2x"
        )
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Display chat messages
    display_chat_messages()
    
    # Handle audio input
    audio_processed = handle_audio_input(audio_bytes)
    
    # Generate assistant response if needed
    generate_assistant_response()
    
    # Float the footer container with enhanced positioning
    footer_container.float("bottom: 0rem;")
    
    # Add some spacing at the bottom to prevent overlap with floating elements
    st.markdown('<div style="height: 100px;"></div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
