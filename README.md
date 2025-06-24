# -Tubescript-Youtube-Video-Analyzer
A versatile web app built with Streamlit and Python to automatically summarize, translate, and analyze YouTube video transcripts using NLP.
📝

An AI-powered Streamlit web app that:

- Extracts video transcripts using `youtube-transcript-api`
- Summarizes transcripts using Hugging Face Transformers
- Extracts keywords with spaCy NLP
- Generates a word cloud
- Translates transcripts into Hindi
- Shows related videos using YouTube Data API
- Allows saving summaries in the session profile

## 🚀 Features

- 🎯 Paste any YouTube URL
- 🧠 AI-based summarization
- ☁️ WordCloud of key terms
- 🌐 Translation to Hindi
- 📂 Save and view previous summaries
- 🔍 Related video discovery

## 🛠️ Tech Stack

- Python 3.11
- [Streamlit](https://streamlit.io/)
- [HuggingFace Transformers](https://huggingface.co/)
- [spaCy NLP](https://spacy.io/)
- YouTube APIs (Transcript + Data API)
- Google Translate API (via `googletrans`)

## 🧪 Setup Instructions

```bash
# 1. Clone the repo
git clone https://github.com/YOUR-USERNAME/youtube-transcript-summarizer
cd youtube-transcript-summarizer

# 2. Set up a virtual environment
python3 -m venv venv
source venv/bin/activate   # or venv\Scripts\activate on Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set your YouTube API key
export YOUTUBE_API_KEY_SCRIPT1="YOUR_YOUTUBE_API_KEY"

# 5. Run the app
streamlit run app1.py
