import streamlit as st
import docx
from docx.shared import Pt, Inches
from google import genai
import io

# --- විෂයයන් සහ ඒවාට අදාළ Sample Prompts ---
subject_prompts = {
    "O/L Science (විද්‍යාව)": "10 ශ්‍රේණිය 'ආලෝකය' පාඩමේ වර්තනය සහ දර්පණ ඇසුරින් MCQ 10ක් සහ ව්‍යුහගත ප්‍රශ්නයක් සකසන්න.",
    "O/L Mathematics (ගණිතය)": "11 ශ්‍රේණිය 'වර්ගජ සමීකරණ' පාඩම ඇසුරින් පියවර සහිතව විසඳිය යුතු ව්‍යුහගත ප්‍රශ්න 3ක් සකසන්න.",
    "A/L Physics (භෞතික විද්‍යාව)": "ධාරා විද්‍යුතය පාඩමේ කිර්චොෆ් නියම ඇසුරින් විසඳිය යුතු MCQ 5ක් සහ ව්‍යුහගත ප්‍රශ්නයක් සකසන්න.",
    "A/L Chemistry (රසායන විද්‍යාව)": "s, p, d ගොනුවේ මූලද්‍රව්‍ය ඇසුරින් රසායනික ගුණ විමසන MCQ 5ක් සහ ව්‍යුහගත ප්‍රශ්නයක් සකසන්න.",
    "A/L Biology (ජීව විද්‍යාව)": "සෛල විද්‍යාව පාඩම ඇසුරින් අණුක ව්‍යුහය පිළිබඳ ප්‍රශ්න 5ක් සකසන්න.",
    "Other": "මෙම විෂයට අදාළව වැදගත් පාඩම් මාතෘකා කිහිපයක් ඇතුළත් කර ප්‍රශ්න පත්‍රයක් සකසන්න."
}

st.set_page_config(page_title="Universal AI Paper Generator", layout="centered")
st.title("📝 Universal AI Paper Generator")

# විෂය තෝරා ගැනීම
selected_subject = st.selectbox("📚 විෂය තෝරන්න:", list(subject_prompts.keys()))

# තෝරාගත් විෂයට අදාළ default prompt එක ලබා ගැනීම
default_prompt = subject_prompts.get(selected_subject, "ඔබේ ප්‍රශ්න පත්‍රය සඳහා විස්තරය මෙතැන ලියන්න...")

# Prompt එක Edit කිරීමට ඉඩ දීම
prompt_text = st.text_area("✍️ ප්‍රශ්න පත්‍රයේ විස්තරය (Prompt):", value=default_prompt, height=150)

# ප්‍රශ්න පත්‍රය ජනනය කිරීමේ ශ්‍රිතය
def generate_paper(prompt, sub):
    api_key = st.secrets["GEMINI_API_KEY"]
    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=f"You are a professional teacher. Create an exam paper for {sub}. {prompt}. Include marking scheme."
    )
    return response.text

if st.button("📄 Generate Paper"):
    with st.spinner("⏳ ප්‍රශ්න පත්‍රය සකසමින් පවතී..."):
        try:
            content = generate_paper(prompt_text, selected_subject)
            doc = docx.Document()
            doc.add_paragraph(content)
            
            bio = io.BytesIO()
            doc.save(bio)
            bio.seek(0)
            
            st.success("✅ සාර්ථකයි!")
            st.download_button("📥 Download Word File", data=bio, file_name=f"{selected_subject}_Paper.docx")
        except Exception as e:
            st.error(f"❌ දෝෂයකි: {e}")
