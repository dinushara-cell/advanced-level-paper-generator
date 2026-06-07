import streamlit as st
import docx
from google import genai
import io
import time

# පිටු සැකසුම
st.set_page_config(page_title="Universal AI Paper Generator Pro", layout="centered")
st.title("📝 Universal AI Paper Generator Pro")

# --- දත්ත ලැයිස්තු ---
grades = [str(i) for i in range(1, 14)]
paper_types = ["MCQ only", "Structured only", "Essay only", "Mixed (Structured + Essay)"]
languages = ["Sinhala", "English", "Tamil"]

# --- ශ්‍රේණිය අනුව විෂය ධාරා තේරීම ---
col1, col2, col3 = st.columns(3)
selected_grade = col1.selectbox("🎓 ශ්‍රේණිය:", grades)

if int(selected_grade) <= 9:
    available_streams = ["Primary"]
elif int(selected_grade) in [10, 11]:
    available_streams = ["O/L"]
else:
    available_streams = ["A/L Biology", "A/L Maths", "A/L Tech", "A/L Arts", "A/L Commerce"]

selected_stream = col2.selectbox("📂 විෂය ධාරාව:", available_streams)
selected_medium = col3.selectbox("🌐 මාධ්‍යය:", languages)

col4, col5 = st.columns(2)
num_questions = col4.slider("🔢 ප්‍රශ්න ගණන:", 1, 50, 10)
paper_type = col5.selectbox("📄 පත්‍ර වර්ගය:", paper_types)

subject = st.text_input("📚 විෂය නම:", placeholder="උදා: Physics")

default_prompt = f"{selected_grade} ශ්‍රේණියේ {selected_stream} ධාරාවේ {subject} විෂය සඳහා, {paper_type} ආකෘතියෙන් ප්‍රශ්න {num_questions}ක් {selected_medium} මාධ්‍යයෙන් සකසන්න."
prompt_text = st.text_area("✍️ විස්තරය (Prompt):", value=default_prompt, height=150)

# --- නිවැරදි කළ Retry Logic ශ්‍රිතය ---
def generate_doc_with_retry(prompt, gr, stream, sub, med, num, ptype):
    try:
        # API Key එක secrets වලින් ලබා ගැනීම
        api_key = st.secrets["GEMINI_API_KEY"]
        client = genai.Client(api_key=api_key)
        
        final_prompt = f"Create a formal exam paper. Grade: {gr}, Stream: {stream}, Subject: {sub}, Language: {med}, Type: {ptype}, Count: {num}. Prompt: {prompt}. Include marking scheme at the end."
        
        # දෝෂ මඟහරවා ගැනීමට උපරිම වාර 3ක් උත්සාහ කරයි
        for attempt in range(3):
            try:
                # මෙහි Model එක gemini-1.5-flash ලෙස වෙනස් කිරීම වඩාත් ස්ථාවරයි (අවශ්‍ය නම් gemini-2.5-flash ලෙසම තබන්න)
                response = client.models.generate_content(
                    model='gemini-1.5-flash', 
                    contents=final_prompt
                )
                
                doc = docx.Document()
                doc.add_paragraph(response.text)
                bio = io.BytesIO()
                doc.save(bio)
                bio.seek(0)
                return bio.getvalue()
                
            except Exception as e:
                if attempt < 2:
                    time.sleep(5) # තත්පර 5ක ප්‍රමාදයක් ලබා දීම
                    continue
                else:
                    return str(e) # දෝෂය පණිවිඩයක් ලෙස ආපසු යවයි
    except Exception as e:
        return str(e)

# --- Generate බොත්තම ---
if st.button("📄 Generate Paper"):
    if not subject:
        st.warning("කරුණාකර විෂය නම ඇතුළත් කරන්න.")
    else:
        with st.spinner("⏳ පත්‍රය සකසමින් පවතී..."):
            res = generate_doc_with_retry(prompt_text, selected_grade, selected_stream, subject, selected_medium, num_questions, paper_type)
            
            if isinstance(res, bytes):
                st.success("✅ සාර්ථකයි!")
                st.download_button("📥 Download", data=res, file_name=f"{subject}_Paper.docx")
            else:
                st.error(f"❌ දෝෂයකි: {res}")
                st.info("ඉඟිය: පද්ධතියේ තදබදයක් විය හැක. නැවත 'Generate Paper' බොත්තම ඔබන්න.")
