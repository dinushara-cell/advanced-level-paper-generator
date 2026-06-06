import streamlit as st
import docx
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from google import genai
import io

st.set_page_config(page_title="Paper Generator", layout="centered")
st.title("📝 Universal AI Paper Generator")

# API Key පරීක්ෂාව
try:
    api_key = st.secrets["GEMINI_API_KEY"]
except:
    st.error("❌ System Error: Gemini API Key එක සකසා නැත. Streamlit Secrets පරීක්ෂා කරන්න.")
    st.stop()

# විෂය තෝරා ගැනීම
subject = st.selectbox("📚 විෂය තෝරන්න:", ["Physics", "Chemistry", "Mathematics", "Biology", "Other"])
prompt_text = st.text_area("✍️ විස්තරය ලියන්න:")

# පත්‍රය ජනනය කිරීම
def generate_paper(prompt, sub):
    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model='gemini-2.0-flash',
        contents=f"Create a test paper for {sub}. {prompt}"
    )
    return response.text

if st.button("📄 Generate Paper"):
    with st.spinner("⏳ ප්‍රශ්න පත්‍රය සකසමින් පවතී..."):
        try:
            content = generate_paper(prompt_text, subject)
            doc = docx.Document()
            doc.add_paragraph(content)
            
            bio = io.BytesIO()
            doc.save(bio)
            bio.seek(0)
            
            st.success("✅ සූදානම්!")
            st.download_button("📥 Download", data=bio, file_name="paper.docx")
        except Exception as e:
            st.error(f"❌ දෝෂයකි: {e}")
