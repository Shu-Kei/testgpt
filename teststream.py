import streamlit as st
import random
import speech_recognition as sr
import numpy as np
from gtts import gTTS
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferWindowMemory
from langchain.chains import ConversationChain
from audio_recorder_streamlit import audio_recorder
from streamlit_chat import message 
import os
import base64
from langdetect import detect
def texttospeech(text,language):
    output = gTTS(text,lang=language, slow=False)
    output.save("output.mp3")

def autoplay_audio(file_path: str):
    with open(file_path, "rb") as f:
        data = f.read()
        b64 = base64.b64encode(data).decode()
        md = f"""
            <audio controls autoplay="true">
            <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
            </audio>
            """
        st.markdown(
            md,
            unsafe_allow_html=True,
        )    
 
llm = ChatOpenAI(openai_api_key="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",temperature=0.0)
r = sr.Recognizer()

if "memory" not in st.session_state:
    st.session_state["memory"]=ConversationBufferWindowMemory(k=5)

st.title("Chat with AI")
if "input" not in st.session_state:
    st.session_state["input"]=np.empty((0, 2), str)
col1, col2 = st.columns([11, 1])
with col1:
    input=st.text_input("say something",label_visibility="collapsed")
with col2:
    audio_bytes = audio_recorder(text="",icon_size="2x")
if "ab" not in st.session_state:
    st.session_state.ab=None   
col=st.columns([1,1])

chat_placeholder = st.empty()

if input != "" and input!=None or audio_bytes:
    try:
        if audio_bytes!=st.session_state.ab:
            if os.path.exists('myfile.wav'):
                os.remove('myfile.wav')
            with open('myfile.wav', mode='bx') as f:
                f.write(audio_bytes)
            audio_ex = sr.AudioFile('myfile.wav')
            with audio_ex as source:
                audiodata = r.record(audio_ex)
            input=r.recognize_google(audiodata,language="vi-VN")
            st.session_state.ab=audio_bytes
        message(input,is_user=True,key=random.random())
        history=np.flip(st.session_state["input"])
        for a,i in history:
            message(a,key=random.random())
            message(i,is_user=True,key=random.random())
        conversation = ConversationChain(
        llm=llm, 
        memory = st.session_state["memory"],
        verbose=False) 
        anwser=conversation.predict(input=input)
        st.session_state["input"]=np.append(st.session_state["input"],np.array([[input, anwser]]),axis=0)
        with open("chat_history.txt", "a", encoding='utf-8') as file:
            for i,a in st.session_state["input"]:
                file.write('User: '+ i + '\n'+ 'Bot: ' +a+ '\n')
        with chat_placeholder.container():  
            message(anwser,key=random.random())
            texttospeech(anwser,detect(anwser))
            autoplay_audio("output.mp3")
    except Exception as e:
        message("Tôi không hiểu bạn nói gì, hãy thử lại!")
