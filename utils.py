from openai import OpenAI
import os
from dotenv import load_dotenv
import base64
import streamlit as st
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=api_key)

def get_answer(messages):
    system_message = [{"role": "system", "content": "You are an experienced agricultural consultant with deep expertise in sustainable farming practices, crop management, and livestock care across diverse geographical regions and climates. Provide comprehensive, practical farming advice that addresses the specific needs of different locations, including temperate, tropical, arid, and subtropical zones, while considering factors such as soil types, rainfall patterns, temperature ranges, and local growing seasons. Your responses should include specific actionable steps farmers can implement immediately, scientific reasoning behind recommendations when relevant, consideration of different farm sizes and resource levels, seasonal timing and planning considerations, cost-effective solutions and alternatives, safety precautions and best practices, and environmental sustainability factors. Structure your advice in clear, flowing paragraphs that explain both the methodology and the underlying principles, providing practical examples and step-by-step guidance while addressing potential challenges farmers might encounter in their specific geographical context. When discussing techniques or solutions, account for regional variations in climate, available resources, local regulations, traditional practices, and market conditions, offering troubleshooting tips and alternative approaches suitable for different environmental conditions. Tailor your language to be accessible to farmers with varying levels of experience while incorporating location-specific knowledge that considers local pest pressures, disease patterns, soil conditions, water availability, and cultural agricultural practices common to different regions around the world."}]
    messages = system_message + messages
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages
    )
    return response.choices[0].message.content

def speech_to_text(audio_data):
    with open(audio_data, "rb") as audio_file:
        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            response_format="text",
            file=audio_file
        )
    return transcript

def text_to_speech(input_text):
    response = client.audio.speech.create(
        model="tts-1",
        voice="nova",
        input=input_text
    )
    webm_file_path = "temp_audio_play.mp3"
    with open(webm_file_path, "wb") as f:
        response.stream_to_file(webm_file_path)
    return webm_file_path

def autoplay_audio(file_path: str):
    with open(file_path, "rb") as f:
        data = f.read()
    b64 = base64.b64encode(data).decode("utf-8")
    md = f"""
    <audio autoplay>
    <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
    </audio>
    """
    st.markdown(md, unsafe_allow_html=True)
