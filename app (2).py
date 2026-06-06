import streamlit as st
import docx
from google import genai
import io
import time
import urllib.parse

st.set_page_config(page_title="Universal AI Paper Generator Pro", layout="centered")
st.title("📝 Universal AI Paper Generator Pro")

# --- දත්ත ලැයිස්තු ---
grades = [str(i) for i in range(1, 14)]
languages = ["Sinhala", "English", "Tamil"]
subjects = [
    "Science", "Mathematics", "History", "ICT", "Geography", "Health", "Sinhala", "English", 
    "Physics", "Chemistry", "Biology", "Combined Mathematics", "Accounting", "Economics", 
    "Business Studies", "Political Science"
]

# --- Access Control (පෙර පරිදිම) ---
if "free_credits" not in st.session_state: st.session_state.free_credits = 2
input_code = st.sidebar.text_input("Access Code:", type="password")
is_premium = (input_code == "EXAMPRO2026")

if not is_premium and st.session_state.free_credits <= 0:
    st.error("⚠️ නොමිලේ අවස්ථා අවසන්!")
    st.stop()

# --- තේරීම් මෙනු ---
col1, col2, col3 = st.columns(3)
selected_grade = col1.selectbox("🎓 ශ්‍රේණිය:", grades)
selected_subject = col2.selectbox("📚 විෂය:", subjects)
selected_medium = col3.selectbox("🌐 මාධ්‍යය:", languages)

# --- ස්වයංක්‍රීය Prompt ජනනය ---
default_prompt = f"{selected_grade} ශ්‍රේණිය සඳහා {selected_subject} විෂයට අදාළව, {selected_medium} මාධ්‍යයෙන් විභාග ප්‍රශ්න පත්‍රයක් සහ පිළිතුරු පත්‍රයක් සකසන්න."
prompt_text = st.text_area("✍️ විස්තරය (Prompt):", value=default_prompt, height=150)

# --- Retry Logic සහිත ශ්‍රිතය ---
def generate_doc_with_retry(prompt, gr, sub, med):
    try:
        api_key = st.secrets["GEMINI_API_KEY"]
        client = genai.Client(api_key=api_key)
        final_prompt = f"Create an official exam paper for Grade {gr}, Subject {sub}, Medium {med}. {prompt}. Include marking scheme at the end."
        
        for attempt in range(3):
            try:
                response = client.models.generate_content(model='gemini-2.5-flash', contents=final_prompt)
                doc = docx.Document()
                doc.add_paragraph(response.text)
                bio = io.BytesIO()
                doc.save(bio)
                bio.seek(0)
                return bio.getvalue()
            except Exception as e:
                if attempt < 2: time.sleep(3); continue
                else: raise e
    except Exception as e:
        return e

# --- Generate බොත්තම ---
if st.button("📄 Generate Paper"):
    with st.spinner("⏳ පත්‍රය සකසමින් පවතී..."):
        res = generate_doc_with_retry(prompt_text, selected_grade, selected_subject, selected_medium)
        if isinstance(res, bytes):
            if not is_premium: st.session_state.free_credits -= 1
            st.success("✅ සාර්ථකයි!")
            st.download_button("📥 Download", data=res, file_name=f"{selected_subject}_Grade{selected_grade}.docx")
        else:
            st.error(f"❌ දෝෂයකි: {res}")
