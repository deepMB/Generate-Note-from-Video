import streamlit as st
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain.prompts import ChatPromptTemplate
from pytube import YouTube
import os
from pathlib import Path
from dotenv import load_dotenv
import whisper
from zipfile import ZipFile
import shutil

load_dotenv()
prompt_tempt = "Write a news article in 500 words from the below text:\n {text}"

@st.cache_resource
def load_model():
    model = whisper.load_model('base')
    return model

def save_audio(url):
    yt = YouTube(url)
    video = yt.streams.filter(only_audio=True).first()
    out_file = video.download()
    base, ext = os.path.splitext(out_file)
    file_name = base + '.mp3'
    try:
        os.rename(out_file, file_name)
    except WindowsError:
        os.remove(file_name)
        os.rename(out_file, file_name)
    audio_filename = Path(file_name).stem+'.mp3'
    print(yt.title + " Has been successfully downloaded")
    print(file_name)
    return yt.title, audio_filename

def audio_to_transcript(audio_file):
    model = load_model()
    result = model.transcribe(audio_file)
    transcript = result["text"]
    return transcript

def text_to_note(text):
    gpt = ChatOpenAI(model="gpt-4o",temperature=0.2)
    prompt = ChatPromptTemplate.from_template(prompt_tempt)
    chain = prompt|gpt|StrOutputParser()
    response = chain.invoke({'text':text})

def main():
    st.title("Youtube to Note Generator")
    url = st.text_input("Paste Youtube URL here")

    if st.button('Start') and url:
        video_title, audio_filename = save_audio(url)
        print(video_title)
        st.audio(audio_filename)
        transcript = audio_to_transcript(audio_filename)
        st.header("Transcript are getting generated...")
        st.success(transcript)
        st.header("News Article")
        result = text_to_note(transcript)
        st.success(result)
        
        #save the files
        transcript_txt = open('transcript.txt', 'w')
        transcript_txt.write(transcript)
        transcript_txt.close()  
        
        article_txt = open('article.txt', 'w')
        article_txt.write(result) 
        article_txt.close() 
        
        zip_file = ZipFile('output.zip', 'w')
        zip_file.write('transcript.txt')
        zip_file.write('article.txt')
        zip_file.close()
        
        with open("output.zip", "rb") as zip_download:
            btn = st.download_button(
                label="Download ZIP",
                data=zip_download,
                file_name="output.zip",
                mime="application/zip"
            )    


if __name__ =="__main__":
    main()