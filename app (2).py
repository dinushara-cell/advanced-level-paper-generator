import streamlit as st
import docx
from docx.shared import Pt, Inches
from google import genai
import io
import urllib.parse

# --- පිටු සැකසුම ---
st.set_page_config(page_title="Universal AI Paper Generator Pro", layout="centered")
st.title("📝 Universal AI Paper Generator Pro")
st.caption("Commercial Version 3.4 | Stable Edition")
st.write("---")

# --- සැකසුම් ---
VALID_ACCESS_CODE = "EXAMPRO2026"
YOUR_WHATSAPP_NUMBER = "94771234567"

if "free_credits" not in st.session_state:
    st.session_state.free_credits = 2

# --- Access Control ---
st.sidebar.header("🔑 Access Control")
input_code = st.sidebar.text_input("Access Code:", type="password")
is_premium = (input_code == VALID_ACCESS_CODE)

if not is_premium:
    if st.session_state.free_credits > 0:
        st.sidebar.info(f"🎁 නොමිලේ ඉතිරි අවස්ථා: {st.session_state.free_credits}")
    else:
        st.error("⚠️ නොමිලේ අවස්ථා අවසන්!")
        msg = "Hi, මට Premium Access Code එකක් අවශ්‍යයි."
        whatsapp_url = f"https://wa.me/{YOUR_WHATSAPP_NUMBER}?text={urllib.parse.quote(msg)}"
        st.markdown(f'[💬 Get Premium Access via WhatsApp]({whatsapp_url})')
        st.stop()
else:
    st.sidebar.success("🔒 Premium Access Active!")

# --- ශ්‍රේණිය, විෂය, මාධ්‍ය ඇතුළත් කිරීම ---
col1, col2, col3 = st.columns(3)
grade = col1.text_input("🎓 ශ්‍රේණිය:", placeholder="උදා: 11")
subject = col2.text_input("📚 විෂය:", placeholder="උදා: විද්‍යාව")
medium = col3.text_input("🌐 මාධ්‍යය:", placeholder="උදා: සිංහල")

default_prompt = f"{grade} ශ්‍රේණිය සඳහා {subject} විෂයට අදාළව, {medium} මාධ්‍යයෙන් විභාග ප්‍රශ්න පත්‍රයක් සහ පිළිතුරු පත්‍රයක් සකසන්න."
prompt_text = st.text_area("✍️ විස්තරය (Prompt):", value=default_prompt, height=150)

# --- පත්‍රය ජනනය කිරීමේ ශ්‍රිතය ---
def generate_doc(prompt, gr, sub, med):
    try:
        api_key = st.secrets["GEMINI_API_KEY"]
        client = genai.Client(api_key=api_key)
        final_prompt = f"Create an official exam paper for Grade {gr}, Subject {sub}, Medium {med}. {prompt}. Include marking scheme at the end."
        
        response = client.models.generate_content(model='gemini-2.5-flash', contents=final_prompt)
        
        doc = docx.Document()
        doc.add_paragraph(response.text)
        bio = io.BytesIO()
        doc.save(bio)
        bio.seek(0)
        return bio.getvalue()
    except Exception as e:
        return e

# --- Generate බොත්තම ---
if st.button("📄 Generate Paper"):
    if not grade or not subject or not medium:
        st.warning("⚠️ කරුණාකර සියලු විස්තර පුරවන්න.")
    else:
        with st.spinner("⏳ පත්‍රය සකසමින් පවතී..."):
            res = generate_doc(prompt_text, grade, subject, medium)
            if isinstance(res, bytes):
                if not is_premium: st.session_state.free_credits -= 1
                st.success("✅ සූදානම්!")
                st.download_button("📥 Download Word File", data=res, file_name=f"{sub}_Grade{gr}_Paper.docx")
            else:
                st.error(f"❌ දෝෂයකි: {res}")
