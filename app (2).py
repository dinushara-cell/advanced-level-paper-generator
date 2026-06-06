import streamlit as st
import docx
from google import genai
import io

st.set_page_config(page_title="Universal AI Paper Generator", layout="centered")
st.title("📝 Universal AI Paper Generator Pro")

# --- ශ්‍රේණිය, විෂය හා මාධ්‍ය ඇතුළත් කිරීමේ Text Box තුන ---
col1, col2, col3 = st.columns(3)

with col1:
    grade = st.text_input("🎓 ශ්‍රේණිය (Grade):", placeholder="උදා: 11")
with col2:
    subject = st.text_input("📚 විෂය (Subject):", placeholder="උදා: විද්‍යාව")
with col3:
    medium = st.text_input("🌐 මාධ්‍යය (Medium):", placeholder="උදා: සිංහල")

# ස්වයංක්‍රීයව prompt එක ජනනය කිරීම
default_prompt = f"{grade} ශ්‍රේණිය සඳහා {subject} විෂයට අදාළව, {medium} මාධ්‍යයෙන් ප්‍රශ්න පත්‍රයක් සහ පිළිතුරු පත්‍රයක් සකසන්න."
prompt_text = st.text_area("✍️ ප්‍රශ්න පත්‍රයේ විස්තරය (Prompt):", value=default_prompt, height=150)

# ප්‍රශ්න පත්‍රය ජනනය කිරීමේ ශ්‍රිතය
import time

def generate_paper(prompt, grade, sub, med):
    api_key = st.secrets["GEMINI_API_KEY"]
    client = genai.Client(api_key=api_key)
    
    # Retry logic එක
    for attempt in range(3): 
        try:
            response = client.models.generate_content(
                model='gemini-2.0-flash', # අවශ්‍ය නම් මෙතැන මාදිලිය වෙනස් කරන්න
                contents=f"You are a professional teacher in Sri Lanka. Create a formal exam paper for Grade {grade}, Subject {sub}, Medium {med}. {prompt}. Include marking scheme at the end."
            )
            return response.text
        except Exception as e:
            if "503" in str(e) and attempt < 2:
                time.sleep(5) # තත්පර 5ක් ඉඳලා නැවත උත්සාහ කරන්න
                continue
            else:
                raise e # තෙවන වරත් බැරි නම් දෝෂය පෙන්වන්න
                st.error(f"❌ දෝෂයකි: {e}")
