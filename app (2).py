import streamlit as st
import docx
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from google import genai
import io
import urllib.parse

# --- පද්ධති සැකසුම් ---
st.set_page_config(page_title="Universal AI Paper Generator Pro", page_icon="📝", layout="centered")

# --- Session State ආරම්භ කිරීම ---
if "free_credits" not in st.session_state:
    st.session_state.free_credits = 2

st.title("📝 Universal AI Paper Generator Pro")
st.caption("Commercial Version 3.3 | Stable Release")
st.write("---")

# --- සැකසුම් ---
YOUR_WHATSAPP_NUMBER = "94771234567"
VALID_ACCESS_CODE = "EXAMPRO2026"
msg = "Hi Dinusha, මට Universal AI Paper Generator එක පාවිච්චි කරන්න Access Code එකක් ගන්න ඕනේ."
whatsapp_url = f"https://wa.me/{YOUR_WHATSAPP_NUMBER}?text={urllib.parse.quote(msg)}"

# --- Sidebar Access Control ---
st.sidebar.header("🔑 Access Control")
input_code = st.sidebar.text_input("Access Code:", type="password")
is_premium = (input_code == VALID_ACCESS_CODE)

if not is_premium:
    if st.session_state.free_credits > 0:
        st.sidebar.info(f"🎁 ඉතිරි නොමිලේ අවස්ථා: {st.session_state.free_credits}")
    else:
        st.error("⚠️ නොමිලේ අවස්ථා අවසන්!")
        st.markdown(f'[💬 Get Premium Access via WhatsApp]({whatsapp_url})')
        st.stop()
else:
    st.sidebar.success("🔒 Premium Access Active!")

# --- UI කොටස ---
col_sub, col_lang = st.columns(2)
subject = col_sub.selectbox("📚 විෂය:", ["O/L Science (විද්‍යාව)", "O/L Mathematics (ගණිතය)", "A/L Physics (භෞතික විද්‍යාව)", "A/L Chemistry (රසායන විද්‍යාව)", "Other"])
language = col_lang.selectbox("🌐 මාධ්‍යය:", ["Sinhala (සිංහල)", "English", "Tamil (தமிழ்)"])
base_prompt = st.text_area("✍️ විස්තරය:", height=150)

# --- ප්‍රධාන ශ්‍රිතය ---
def generate_doc(prompt_text, with_diagrams, sub, lang):
    try:
        api_key = st.secrets["GEMINI_API_KEY"]
        client = genai.Client(api_key=api_key)
        final_prompt = f"Create an exam paper for {sub} in {lang}. {prompt_text}. Provide marking scheme at the end."
        
        response = client.models.generate_content(model='gemini-2.5-flash', contents=final_prompt)
        
        doc = docx.Document()
        doc.add_paragraph(response.text)
        bio = io.BytesIO()
        doc.save(bio)
        bio.seek(0)
        return bio.getvalue()
    except Exception as e:
        return e

# --- බොත්තම් සැකසුම (Spinners දෝෂ රහිතව) ---
if st.button("📄 Generate Plain Paper"):
    with st.spinner("⏳ පත්‍රය සකසමින් පවතී..."):
        res = generate_doc(base_prompt, False, subject, language)
        if isinstance(res, bytes):
            if not is_premium: st.session_state.free_credits -= 1
            st.download_button("📥 Download File", data=res, file_name="paper.docx")
        else:
            st.error(f"Error: {res}")

if st.button("🖼️ Generate with Diagrams"):
    with st.spinner("⏳ පත්‍රය සහ රූප සටහන් සකසමින් පවතී..."):
        res = generate_doc(base_prompt, True, subject, language)
        if isinstance(res, bytes):
            if not is_premium: st.session_state.free_credits -= 1
            st.download_button("📥 Download File", data=res, file_name="paper_diagrams.docx")
        else:
            st.error(f"Error: {res}")
