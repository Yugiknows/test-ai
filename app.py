import streamlit as st
import os
import tempfile
import logging
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
    """Main application class for AgriHelper voice-enabled farming assistant."""
    
    def __init__(self):
        self.initialize_session_state()
        
    def initialize_session_state(self) -> None:
        """Initialize session state with default values."""
        if "messages" not in st.session_state:
            st.session_state.messages = [
                {
                    "role": "system", 
                    "content": "You are AgriHelper, an expert farming assistant. Provide detailed, practical farming advice in clear, conversational sentences. Focus on actionable solutions and consider local farming practices."
                }
            ]
        
        if "conversation_count" not in st.session_state:
            st.session_state.conversation_count = 0
            
        if "audio_processing" not in st.session_state:
            st.session_state.audio_processing = False
    
    def display_header(self) -> None:
        """Display the application header and title."""
        st.title("🌱 AgriHelper")
        st.markdown(
            '<div class="subtitle">🎤 <strong>Speak to get expert farming advice - AI responds with voice!</strong> 🔊</div>', 
            unsafe_allow_html=True
        )
        
        # Display conversation counter
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
            # Create temporary file with proper extension
            with tempfile.NamedTemporaryFile(delete=False, suffix='.webm') as temp_file:
                temp_file.write(audio_bytes)
                temp_file_path = temp_file.name
            
            # Convert audio to text
            transcript = speech_to_text(temp_file_path)
            
            # Clean up temporary file
            self.safe_file_cleanup(temp_file_path)
            
            return transcript
            
        except Exception as e:
            logger.error(f"Error processing audio input: {str(e)}")
            st.error("❌ Sorry, I couldn't process your audio. Please try again.")
            return None
    
    def generate_response(self, transcript: str) -> Optional[str]:
        """Generate response from the AI model."""
        try:
            # Add user message to conversation
            st.session_state.messages.append({"role": "user", "content": transcript})
            
            # Get AI response
            response = get_answer(st.session_state.messages)
            
            # Add assistant response to conversation
            st.session_state.messages.append({"role": "assistant", "content": response})
            
            # Increment conversation counter
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
                autoplay_audio(audio_file)
                # Delay cleanup to allow audio to play longer
                import time
                time.sleep(5)  # Increased from 1 to 5 seconds
                self.safe_file_cleanup(audio_file)
            else:
                logger.error("Audio file not generated")
                
        except Exception as e:
            logger.error(f"Error with text-to-speech: {str(e)}")
            # Silently fail - don't show warnings to user
    
    def run(self) -> None:
        """Main application loop."""
        # Display header
        self.display_header()
        
        # Display conversation history
        self.display_conversation_history()
        
        # Create footer container for audio recorder
        footer_container = st.container()
        
        with footer_container:
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                audio_bytes = audio_recorder(
                    text="Click to record",
                    recording_color="#ff0000",
                    neutral_color="#2E7D32",
                    icon_name="microphone",
                    icon_size="2x"
                )
        
        # Handle audio input
        if audio_bytes:
            # Check if this is a new audio recording by comparing with stored audio
            if "last_audio_bytes" not in st.session_state or st.session_state.last_audio_bytes != audio_bytes:
                st.session_state.last_audio_bytes = audio_bytes
                
                with st.spinner("🎤 Processing your voice..."):
                    transcript = self.process_audio_input(audio_bytes)
                
                if transcript:
                    # Show user's question immediately
                    with st.chat_message("user"):
                        st.write(transcript)
                    
                    with st.spinner("🤔 Thinking..."):
                        response = self.generate_response(transcript)
                    
                    if response:
                        # Show AI response immediately
                        with st.chat_message("assistant"):
                            st.write(response)
                        
                        # Generate voice response in background (no spinner)
                        self.handle_text_to_speech(response)
                
                st.rerun()
        
        # Float the footer container
        footer_container.float("bottom: 0rem;")
        
        # Add helpful tips in sidebar
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

# Initialize and run the application
def main():
    """Main function to run the AgriHelper application."""
    try:
        app = AgriHelperApp()
        app.run()
    except Exception as e:
        logger.error(f"Application error: {str(e)}")
        st.error("❌ Application encountered an error. Please refresh the page.")

if __name__ == "__main__":
    main()
