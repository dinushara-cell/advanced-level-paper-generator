import streamlit as st
import google.generativeai as genai
import time

# API සැකසුම
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

# දෝෂ මඟහරවා ගැනීමට නිවැරදි Model නාමය භාවිතා කරන්න
def get_model():
    return genai.GenerativeModel('gemini-1.5-flash')

# බොත්තම එබූ විට ක්‍රියාත්මක වන කොටස
if st.button("Generate Paper"):
    try:
        model = get_model()
        # Rate limit එක නිසා කෙටි ප්‍රමාදයක් ලබා දීම
        time.sleep(2) 
        response = model.generate_content("ඔබේ Prompt එක මෙතැනට")
        st.write(response.text)
    except Exception as e:
        st.error(f"දෝෂයකි: {e}")
