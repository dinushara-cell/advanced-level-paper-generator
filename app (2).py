import streamlit as st
import google.generativeai as genai
import time

st.set_page_config(page_title="Paper Generator")
st.title("📝 Universal AI Paper Generator Pro")

# API Key සකසන්න
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

# තේරීම් මෙනු - Unique Keys භාවිතා කර ඇත
grade = st.selectbox("🎓 ශ්‍රේණිය:", [str(i) for i in range(1, 14)], key="grade_sel")
subject = st.text_input("📚 විෂය:", key="sub_sel")
num = st.slider("🔢 ප්‍රශ්න ගණන:", 1, 20, 5, key="num_sel")

if st.button("Generate Paper", key="gen_btn"):
    if not subject:
        st.warning("විෂය නම ඇතුළත් කරන්න.")
    else:
        with st.spinner("⏳ පත්‍රය සාදමින් පවතී..."):
            try:
                # 404 දෝෂය වළක්වා ගැනීමට නිවැරදි මාදිලිය
                model = genai.GenerativeModel('gemini-1.5-flash')
                prompt = f"Create {num} MCQs for {subject} subject, Grade {grade}."
                response = model.generate_content(prompt)
                st.write(response.text)
            except Exception as e:
                st.error(f"දෝෂයක් සිදුවිය: {e}")
