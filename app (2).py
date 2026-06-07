import streamlit as st
import google.generativeai as genai
import io
import time

# පිටු සැකසුම
st.set_page_config(page_title="Universal AI Paper Generator", layout="centered")
st.title("📝 Universal AI Paper Generator Pro")

# API සැකසුම
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
except Exception as e:
    st.error("API Key සොයාගත නොහැක.")
    st.stop()

# තේරීම් මෙනු (සෑම එකකටම unique key එකක් ලබා දී ඇත)
selected_grade = st.selectbox("🎓 ශ්‍රේණිය:", [str(i) for i in range(1, 14)], key="grade_box")
subject = st.text_input("📚 විෂය නම:", placeholder="උදා: Physics", key="sub_box")
num_questions = st.slider("🔢 ප්‍රශ්න ගණන:", 1, 50, 10, key="slider_box")
paper_type = st.selectbox("📄 පත්‍ර වර්ගය:", ["MCQ only", "Structured only", "Essay only"], key="type_box")

# ජනනය කිරීමේ ශ්‍රිතය
def generate_paper(prompt):
    try:
        # Rate limit මඟහැරීමට පවතින stable මාදිලියක් භාවිතා කිරීම
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error: {str(e)}"

# බොත්තම ක්ලික් කළ විට
if st.button("📄 Generate Paper", key="gen_btn"):
    if not subject:
        st.warning("කරුණාකර විෂය නම ඇතුළත් කරන්න.")
    else:
        with st.spinner("⏳ පත්‍රය සකසමින් පවතී..."):
            prompt_text = f"{selected_grade} ශ්‍රේණියේ {subject} විෂය සඳහා {paper_type} ආකෘතියෙන් ප්‍රශ්න {num_questions}ක් සකසන්න."
            result = generate_paper(prompt_text)
            
            if "Error" not in result:
                st.success("✅ සාර්ථකයි!")
                st.text_area("ප්‍රශ්න පත්‍රය:", value=result, height=400)
                st.download_button("📥 Download", data=result, file_name=f"{subject}_Paper.txt")
            else:
                st.error(result)
