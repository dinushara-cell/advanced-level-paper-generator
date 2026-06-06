import streamlit as st
import docx
from google import genai
import io
import time

st.set_page_config(page_title="Universal AI Paper Generator Pro", layout="centered")
st.title("📝 Universal AI Paper Generator Pro")

# --- දත්ත ලැයිස්තු ---
grades = [str(i) for i in range(1, 14)]
streams = ["Science", "Mathematics", "Technology", "Arts", "Commerce"]
paper_types = ["MCQ only", "Structured only", "Essay only", "Mixed (MCQ + Structured + Essay)"]
languages = ["Sinhala", "English", "Tamil"]

# --- තේරීම් මෙනු ---
col1, col2, col3 = st.columns(3)
selected_grade = col1.selectbox("🎓 ශ්‍රේණිය:", grades)
selected_stream = col2.selectbox("📂 විෂය ධාරාව:", streams)
selected_medium = col3.selectbox("🌐 මාධ්‍යය:", languages)

col4, col5 = st.columns(2)
num_questions = col4.slider("🔢 ප්‍රශ්න ගණන:", 1, 50, 10)
paper_type = col5.selectbox("📄 පත්‍ර වර්ගය:", paper_types)

# විෂයය ඇතුලත් කිරීම
subject = st.text_input("📚 විෂය නම:", placeholder="උදා: Physics")

# --- ස්වයංක්‍රීය Prompt ජනනය ---
default_prompt = f"{selected_grade} ශ්‍රේණියේ {selected_stream} ධාරාවේ {subject} විෂය සඳහා, {paper_type} ආකෘතියෙන් ප්‍රශ්න {num_questions}ක් {selected_medium} මාධ්‍යයෙන් සකසන්න."
prompt_text = st.text_area("✍️ විස්තරය (Prompt):", value=default_prompt, height=150)

# --- Retry Logic සහිත ජනනය ---
def generate_doc_with_retry(prompt, gr, stream, sub, med, num, ptype):
    try:
        api_key = st.secrets["GEMINI_API_KEY"]
        client = genai.Client(api_key=api_key)
        final_prompt = f"Create an official exam paper. Grade: {gr}, Stream: {stream}, Subject: {sub}, Language: {med}, Type: {ptype}, Count: {num}. Prompt: {prompt}. Include marking scheme at the end."
        
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
        res = generate_doc_with_retry(prompt_text, selected_grade, selected_stream, subject, selected_medium, num_questions, paper_type)
        if isinstance(res, bytes):
            st.success("✅ සාර්ථකයි!")
            st.download_button("📥 Download", data=res, file_name=f"{subject}_Paper.docx")
        else:
            st.error(f"❌ දෝෂයකි: {res}")
