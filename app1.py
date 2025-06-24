import streamlit as st
import re
import pyperclip
import spacy
from transformers import pipeline
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from googletrans import Translator
from googleapiclient.discovery import build
import os # For reading environment variables
import traceback # For printing full tracebacks

# --- Page Configuration ---
st.set_page_config(
    page_title="Tubescript Analyzer",
    page_icon="📜",
    layout="wide"
)

# --- Initializations ---
# Load NLP model
SPACY_MODEL_NAME = "en_core_web_sm"
try:
    nlp = spacy.load(SPACY_MODEL_NAME)
except OSError:
    st.error(
        f"SpaCy model '{SPACY_MODEL_NAME}' not found. "
        f"Please ensure it's downloaded and compatible with your spaCy version "
        f"(e.g., python -m spacy download {SPACY_MODEL_NAME}==3.6.0 for spaCy v3.6.x)."
    )
    st.stop()

# YouTube API Key 
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY_SCRIPT1")
if not YOUTUBE_API_KEY:
    st.error(
        "ERROR: YouTube API key (YOUTUBE_API_KEY_SCRIPT1) is not set. "
        "Please set the environment variable and restart the app."
    )
    st.stop()

# summarizer
try:
    summarizer = pipeline("summarization")
except Exception as e:
    st.error(f"Failed to load summarization pipeline: {e}")
    st.info("This might be due to model download issues or transformers/torch compatibility.")
    st.stop()

translator = Translator()

# user profile
if "user_profile" not in st.session_state:
    st.session_state.user_profile = {"name": "Guest", "videos": {}}
user = st.session_state.user_profile

# --- App Title ---
st.title("📜 Tubescript :Youtube Video Analyzer")

# --- Input YouTube URL ---
youtube_url = st.text_input("Enter the YouTube video URL:")
video_id = None
if youtube_url:
    match = re.search(r"v=([\w-]+)", youtube_url)
    if match:
        video_id = match.group(1)
    else:
        st.warning("Please enter a valid YouTube video URL.")

# --- Helper Functions ---
def get_related_videos(video_id_to_search):
    if not video_id_to_search:
        return None, []
    try:
        youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)
        video_info_response = youtube.videos().list(part='snippet', id=video_id_to_search).execute()
        
        if 'items' not in video_info_response or not video_info_response['items']:
            st.warning(f"Could not retrieve information for video ID: {video_id_to_search}")
            return None, []

        video_title = video_info_response['items'][0]['snippet']['title']
        search_response = youtube.search().list(
            part='snippet', type='video', q=video_title, maxResults=5
        ).execute()
        return video_info_response, search_response.get('items', [])
    except Exception as e:
        st.error(f"Error fetching video data from YouTube API: {e}")
        return None, []

def save_video_to_profile(v_id, title, summaries):
    user["videos"][v_id] = {"title": title, "summarized_text": summaries}
    st.session_state.user_profile = user

# --- Processing ---
if video_id:
    st.video(youtube_url)
    st.write(f"Video ID: {video_id}")

    # Use a spinner to show the app is working
    with st.spinner('Analyzing video... This may take a moment.'):
        full_text = None
        summarized_text_parts = []
        try:
            st.info(f"Fetching transcript...")
            transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
            full_text = " ".join([entry['text'] for entry in transcript_list])
            
            # If transcript is fetched, proceed with analysis
            if full_text:
                st.info("Summarizing transcript...")
                max_chunk_size = 1000
                for i in range(0, len(full_text), max_chunk_size):
                    chunk = full_text[i:i + max_chunk_size]
                    summary_output = summarizer(chunk, max_length=150, min_length=30, do_sample=False)
                    if summary_output:
                        summarized_text_parts.append(summary_output[0]['summary_text'])
                
                st.info("Extracting keywords...")
                doc = nlp(full_text)
                keywords = list(set([token.text for token in doc if token.is_alpha and not token.is_stop]))

                st.info("Fetching video details and related videos...")
                video_info_data, related_videos_data = get_related_videos(video_id)
                if video_info_data and 'items' in video_info_data:
                    current_video_title = video_info_data['items'][0]['snippet']['title']
                    save_video_to_profile(video_id, current_video_title, summarized_text_parts)
                    st.success(f"Video '{current_video_title}' saved to your profile!")

        except TranscriptsDisabled:
            st.error(f"Transcripts are disabled for video ID: {video_id}")
        except NoTranscriptFound:
            st.error(f"No transcript could be found for video ID: {video_id}.")
        except Exception as e:
            st.error(f"An error occurred processing the video: {e}")
            print("--------------------------------------------------------------")
            print(f"An error occurred while processing video_id: {video_id}. Full Python traceback:")
            traceback.print_exc()
            print("--------------------------------------------------------------")
    
    #  success message  
    if full_text:
        st.success('Analysis Complete!')
    
    # --- Display Results 
    if full_text:
        st.subheader("📊 Analysis Results")
        tab1, tab2, tab3, tab4, tab5 = st.tabs(["📝 Summary", "🔑 Keywords", "☁️ Word Cloud", "🌐 Translate", "📥 Download"])

        with tab1:
            st.header("Summarized Transcript")
            if summarized_text_parts:
                for i, summary_part in enumerate(summarized_text_parts):
                    st.write(f"**Part {i + 1}:** {summary_part}")
                if st.button("Copy Summarized Text to Clipboard"):
                    pyperclip.copy("\n".join(summarized_text_parts))
                    st.info("Summarized text copied to clipboard.")
            else:
                st.write("No summary could be generated.")

        with tab2:
            st.header("Keywords in the Video Transcript")
            if keywords:
                st.write(", ".join(keywords))
            else:
                st.write("No keywords found.")
        
        with tab3:
            st.header("Word Cloud for Keywords")
            if keywords:
                try:
                    wordcloud_obj = WordCloud(width=800, height=400, background_color="white").generate(" ".join(keywords))
                    fig, ax = plt.subplots(figsize=(10, 5))
                    ax.imshow(wordcloud_obj, interpolation="bilinear")
                    ax.axis("off")
                    st.pyplot(fig)
                except Exception as e_wc:
                    st.error(f"Could not generate word cloud: {e_wc}")
            else:
                st.write("No keywords found to generate a word cloud.")

        with tab4:
            st.header("Translate Full Transcript")
            if st.button("Translate to Hindi"):
                st.info("Translating...")
                try:
                    translated_text = translator.translate(full_text, src='en', dest='hi').text
                    st.write(translated_text)
                    st.success("Translation complete.")
                except Exception as e_translate:
                    st.error(f"Translation failed: {e_translate}")
        
        with tab5:
            st.header("Download Full Transcript")
            st.download_button(
                label="Download Full Transcript as .txt",
                data=full_text,
                file_name=f"{video_id}_transcript.txt",
                mime="text/plain"
            )

        # related videos 
        if 'related_videos_data' in locals() and related_videos_data:
            st.subheader("🤝 Related Videos")
            for video_item in related_videos_data:
                title = video_item['snippet']['title']
                related_video_id_val = video_item['id']['videoId']
                url = f"https://www.youtube.com/watch?v={related_video_id_val}"
                st.markdown(f"- [{title}]({url})")

# Sidebar
st.sidebar.title("👤 User Profile")
st.sidebar.subheader(f"Welcome, {user['name']}!")
new_name = st.sidebar.text_input("Update Name:", user["name"], key="user_name_input")
if st.sidebar.button("Update Profile Name"):
    user["name"] = new_name
    st.session_state.user_profile = user
    st.sidebar.success("Profile name updated!")
    st.rerun()

st.sidebar.subheader("🗂️ Your Saved Videos")
if user["videos"]:
    for vid_id_key, data_val in user["videos"].items():
        with st.sidebar.expander(f"{data_val['title']}"):
            st.markdown(f"**Summarized Parts:**")
            if data_val["summarized_text"]:
                for s_idx, s_text in enumerate(data_val["summarized_text"]):
                    st.write(f"Part {s_idx + 1}: {s_text}")
            else:
                st.write("No summary available for this video.")
else:
    st.sidebar.info("You have not saved any videos yet.")