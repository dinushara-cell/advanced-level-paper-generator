import streamlit as st
import docx
import google.generativeai as genai
import io
import time

# පිටු සැකසුම
st.set_page_config(page_title="Universal AI Paper Generator Pro", layout="centered")
st.title("📝 Universal AI Paper Generator Pro")

# API සැකසුම
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
except Exception as e:
    st.error("API Key සොයාගත නොහැක.")
    st.stop()

# දත්ත ලැයිස්තු
grades = [str(i) for i in range(1, 14)]
paper_types = ["MCQ only", "Structured only", "Essay only", "Mixed (Structured + Essay)"]
languages = ["Sinhala", "English", "Tamil"]

# තේරීම් මෙනු
col1, col2, col3 = st.columns(3)
selected_grade = col1.selectbox("🎓 ශ්‍රේණිය:", grades, key="grade_sel") # Key එකක් එකතු කළා

if int(selected_grade) <= 9:
    available_streams = ["Primary"]
elif int(selected_grade) in [10, 11]:
    available_streams = ["O/L"]
else:
    available_streams = ["A/L Science", "A/L Tech", "A/L Arts", "A/L Commerce"]

selected_stream = col2.selectbox("📂 විෂය ධාරාව:", available_streams, key="stream_sel")
selected_medium = col3.selectbox("🌐 මාධ්‍යය:", languages, key="med_sel")

col4, col5 = st.columns(2)
num_questions = col4.slider("🔢 ප්‍රශ්න ගණන:", 1, 50, 10)
paper_type = col5.selectbox("📄 පත්‍ර වර්ගය:", paper_types, key="type_sel")

subject = st.text_input("📚 විෂය නම:", placeholder="උදා: Physics")
import streamlit as st
import docx
import google.generativeai as genai
import io
import time

# පිටු සැකසුම
st.set_page_config(page_title="Universal AI Paper Generator Pro", layout="centered")
st.title("📝 Universal AI Paper Generator Pro")

# API සැකසුම
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
except Exception as e:
    st.error("API Key සොයාගත නොහැක.")
    st.stop()

# දත්ත ලැයිස්තු
grades = [str(i) for i in range(1, 14)]
paper_types = ["MCQ only", "Structured only", "Essay only", "Mixed (Structured + Essay)"]
languages = ["Sinhala", "English", "Tamil"]

# තේරීම් මෙනු (Unique keys භාවිතා කර ඇත)
col1, col2, col3 = st.columns(3)
selected_grade = col1.selectbox("🎓 ශ්‍රේණිය:", grades, key="g1")

if int(selected_grade) <= 9:
    available_streams = ["Primary"]
elif int(selected_grade) in [10, 11]:
    available_streams = ["O/L"]
else:
    available_streams = ["A/L Science", "A/L Tech", "A/L Arts", "A/L Commerce"]

selected_stream = col2.selectbox("📂 විෂය ධාරාව:", available_streams, key="s1")
selected_medium = col3.selectbox("🌐 මාධ්‍යය:", languages, key="m1")

col4, col5 = st.columns(2)
num_questions = col4.slider("🔢 ප්‍රශ්න ගණන:", 1, 50, 10, key="n1")
paper_type = col5.selectbox("📄 පත්‍ර වර්ගය:", paper_types, key="p1")

subject = st.text_input("📚 විෂය නම:", placeholder="උදා: Physics")

# ජනනය කිරීමේ ශ්‍රිතය
def generate_paper(prompt, gr, stream, sub, med, num, ptype):
    try:
        # වඩාත්ම ස්ථාවර මාදිලිය භාවිතා කිරීම
        model = genai.GenerativeModel('gemini-1.5-flash-001')
        final_prompt = f"Create a formal exam paper. Grade: {gr}, Stream: {stream}, Subject: {sub}, Language: {med}, Type: {ptype}, Count: {num}. Prompt: {prompt}."
        
        response = model.generate_content(final_prompt)
        return response.text
    except Exception as e:
        return f"Error: {str(e)}"

# ජනනය බොත්තම
if st.button("📄 Generate Paper"):
    if not subject:
        st.warning("කරුණාකර විෂය නම ඇතුළත් කරන්න.")
    else:
        with st.spinner("⏳ පත්‍රය සකසමින් පවතී..."):
            result = generate_paper(subject, selected_grade, selected_stream, subject, selected_medium, num_questions, paper_type)
            if "Error" not in result:
                st.success("✅ සාර්ථකයි!")
                st.download_button("📥 Download Result", data=result, file_name=f"{subject}_Paper.txt")
            else:
                st.error(result)
# ජනනය කිරීමේ ශ්‍රිතය
def generate_paper(prompt, gr, stream, sub, med, num, ptype):
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        final_prompt = f"Create a formal exam paper. Grade: {gr}, Stream: {stream}, Subject: {sub}, Language: {med}, Type: {ptype}, Count: {num}. Prompt: {prompt}. Include marking scheme."
        
        response = model.generate_content(final_prompt)
        return response.text
    except Exception as e:
        return f"Error: {str(e)}"

if st.button("📄 Generate Paper"):
    if not subject:
        st.warning("කරුණාකර විෂය නම ඇතුළත් කරන්න.")
    else:
        with st.spinner("⏳ පත්‍රය සකසමින් පවතී..."):
            result = generate_paper(subject, selected_grade, selected_stream, subject, selected_medium, num_questions, paper_type)
            if "Error" not in result:
                st.success("✅ සාර්ථකයි!")
                st.download_button("📥 Download", data=result, file_name=f"{subject}_Paper.txt")
            else:
                st.error(result)
