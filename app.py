import streamlit as st
import os
from src.video_info import GetVideo
from src.model import Model
from src.prompt import Prompt
from src.misc import Misc
from src.timestamp_formatter import TimestampFormatter
from src.db_handler import DatabaseHandler
from st_copy_to_clipboard import st_copy_to_clipboard

st.set_page_config(
    page_title= "Video Summarizer by HAZL",
    layout = "wide",
)
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            .stDeployButton {
                    visibility: hidden;
                }
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)


class AIVideoSummarizer:
    def __init__(self):
        self.youtube_url = None
        self.video_id = None
        self.video_title = None
        self.video_transcript = None
        self.video_transcript_time = None
        self.summary = None
        self.time_stamps = None
        self.transcript = None
        self.col1 = None
        self.col2 = None
        self.db = DatabaseHandler()
        
        if 'openai_api_key' not in st.session_state:
            api_key = self.db.get_api_key()
            if api_key:
                st.session_state['openai_api_key'] = api_key

    def setup_sidebar(self):
        with st.sidebar:
            st.title("Settings")
            api_key = st.text_input("Enter OpenAI API Key", 
                                  value=st.session_state.get('openai_api_key', ''),
                                  type="password")
            
            if st.button("Save API Key"):
                self.db.save_api_key(api_key)
                st.session_state['openai_api_key'] = api_key
                st.success("API key saved successfully!")

    def check_api_key(self):
        if 'openai_api_key' not in st.session_state or not st.session_state['openai_api_key']:
            st.warning("Please enter your OpenAI API key in the sidebar.", icon="⚠️")
            return False
        return True

    def get_youtube_info(self):
        self.youtube_url = st.text_input("Enter YouTube Video Link")
        
        if self.youtube_url:
            self.video_id = GetVideo.Id(self.youtube_url)
            if self.video_id is None:
                st.write("**Error**")
                st.image("https://i.imgur.com/KWFtgxB.png", use_column_width=True)
                st.stop()
            self.video_title = GetVideo.title(self.youtube_url)
            st.write(f"**{self.video_title}**")
            st.image(f"http://img.youtube.com/vi/{self.video_id}/0.jpg", use_column_width=True)

    def generate_summary(self):
        if not self.check_api_key():
            return
        
        if st.button(":rainbow[**Get Summary**]"):
            self.video_transcript = GetVideo.transcript(self.youtube_url)
            self.summary = Model.openai_chatgpt(transcript=self.video_transcript, prompt=Prompt.prompt1())
            st.markdown("## Summary:")
            st.write(self.summary)
            st_copy_to_clipboard(self.summary)

    def generate_time_stamps(self):
        if not self.check_api_key():
            return
        
        if st.button(":rainbow[**Get Timestamps**]"):
            self.video_transcript_time = GetVideo.transcript_time(self.youtube_url)
            youtube_url_full = f"https://youtube.com/watch?v={self.video_id}"
            self.time_stamps = Model.openai_chatgpt(self.video_transcript_time, Prompt.prompt1(ID='timestamp'), extra=youtube_url_full)
            st.markdown("## Timestamps:")
            st.markdown(self.time_stamps)
            cp_text=TimestampFormatter.format(self.time_stamps)
            st_copy_to_clipboard(cp_text)

    def generate_transcript(self):
        if st.button("Get Transcript"):
            self.video_transcript = GetVideo.transcript(self.youtube_url)
            self.transcript = self.video_transcript
            st.markdown("## Transcript:") 
            st.download_button(label="Download as text file", data=self.transcript, file_name=f"Transcript - {self.video_title}")
            st.write(self.transcript)
            st_copy_to_clipboard(self.transcript)

    def run(self):
        
        st.title("Video Summarizer")
        
        self.setup_sidebar()
        self.col1, padding_col, self.col2 = st.columns([1, 0.1, 1])
        
        with self.col1:
            self.get_youtube_info()

        ran_loader=Misc.loaderx() 
        n, loader = ran_loader[0],ran_loader[1]

        with self.col2:
            mode = st.radio(
                "What do you want to generate for this video?",
                [":rainbow[**AI Summary**]", ":rainbow[**AI Timestamps**]", "**Transcript**"],
                index=0)
            if mode == ":rainbow[**AI Summary**]":
                with st.spinner(loader[n]):
                    self.generate_summary()

            elif mode == ":rainbow[**AI Timestamps**]":
                with st.spinner(loader[n]):
                    self.generate_time_stamps()
            else:
                with st.spinner(loader[0]):
                    self.generate_transcript()

        
        st.write(Misc.footer(), unsafe_allow_html=True)


if __name__ == "__main__":
    app = AIVideoSummarizer()
    app.run()
