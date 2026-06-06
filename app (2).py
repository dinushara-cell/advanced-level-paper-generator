import streamlit as st
import docx
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from google import genai
import io
import urllib.parse

# --- වෙබ් පිටුවේ ප්‍රධාන පෙනුම සකස් කිරීම ---
st.set_page_config(page_title="Universal AI Paper Generator Pro", page_icon="📝", layout="centered")

st.title("📝 Universal AI Paper Generator Pro")
st.caption("Create Exam Papers for Any Subject in Any Language | Commercial Version 2.0")
st.write("---")

# --- ඔබේ තොරතුරු (මෙහි ඔබේ විස්තර වෙනස් කරන්න) ---
YOUR_WHATSAPP_NUMBER = "94771234567"  # ඔබේ දුරකථන අංකය (94 රටේ කේතය සමඟ, බිංදුව නැතිව)
VALID_ACCESS_CODE = "EXAMPRO2026"     # පාරිභෝගිකයන් සඳහා වන නව රහස් කේතය

# --- WhatsApp Link එක සෑදීම ---
msg = "Hi Dinusha, මට Universal AI Paper Generator එක පාවිච්චි කරන්න Access Code එකක් ගන්න ඕනේ."
encoded_msg = urllib.parse.quote(msg)
whatsapp_url = f"https://wa.me/{YOUR_WHATSAPP_NUMBER}?text={encoded_msg}"

# --- පරිශීලක අතුරුමුහුණත (Access Code Check) ---
st.sidebar.header("🔑 Access Control")
input_code = st.sidebar.text_input("ඇතුලත් කරන්න ඔබගේ Access Code එක:", type="password", placeholder="Access Code...")

if input_code != VALID_ACCESS_CODE:
    st.warning("⚠️ කරුණාකර මෙම මෙවලම භාවිත කිරීම සඳහා නිවැරදි 'Access Code' එක ඇතුළත් කරන්න.")
    st.info("ඔබ සතුව Access Code එකක් නොමැති නම් හෝ එය මිලදී ගැනීමට අවශ්‍ය නම් පහත බොත්තම හරහා අපව WhatsApp මඟින් සම්බන්ධ කරගන්න.")
    
    st.markdown(f'''
    <a href="{whatsapp_url}" target="_blank">
        <button style="background-color: #25D366; color: white; border: none; padding: 10px 20px; font-size: 16px; border-radius: 5px; cursor: pointer; width: 100%;">
            💬 Get Access Code via WhatsApp
        </button>
    </a>
    ''', unsafe_allowed_html=True)
    
    st.stop()

# --- කේතය නිවැරදි නම් පමණක් පහත ව්‍යාපාරික පැනලය විවෘත වේ ---
st.success("🔒 Access Granted! සාර්ථකව සම්බන්ධ විය.")

# --- විෂය සහ භාෂාව තෝරාගැනීමේ කොටස (Dynamic Dropdowns) ---
col_sub, col_lang = st.columns(2)

with col_sub:
    subject = st.selectbox(
        "📚 විෂය තෝරන්න (Select Subject):",
        ["Physics", "Chemistry", "Combined Mathematics", "Biology", "ICT", "History", "Business Studies", "Accounting", "Economics", "General English", "Other (Mention in prompt)"]
    )

with col_lang:
    language = st.selectbox(
        "🌐 මාධ්‍යය/භාෂාව තෝරන්න (Select Language):",
        ["Sinhala (සිංහල)", "English", "Tamil (தமிழ்)"]
    )

# තෝරාගන්නා විෂය අනුව ස්වයංක්‍රීයව වෙනස් වන Prompt ආදර්ශයක්
placeholder_prompts = {
    "Physics": "ධාරා විද්‍යුතය පාඩමේ කිර්චොෆ් නියම ඇසුරින් විසඳිය යුතු MCQ ප්‍රශ්න 5ක් සහ ව්‍යුහගත රචනා ප්‍රශ්නයක්...",
    "Chemistry": "රදර්ෆර්ඩ්ගේ පරමාණුක ආකෘතිය සහ ක්වොන්ටම් අංක පදනම් කරගත් MCQ ප්‍රශ්න 5ක් සහ රචනා ප්‍රශ්නයක්...",
    "Combined Mathematics": "සන්නිකර්ෂණය සහ සීමාවන් (Limits) පාඩම් ඇසුරින් ව්‍යුහගත රචනා ප්‍රශ්න 3ක්...",
    "Biology": "ශාක පටක සහ ප්‍රභාසංශ්ලේෂණය පාඩම් ඇසුරින් බහුවරණ ප්‍රශ්න 5ක් සහ ව්‍යුහගත ප්‍රශ්නයක්...",
    "ICT": "දත්ත සමුදා කළමනාකරණ පද්ධති (DBMS) සහ SQL Queries ඇසුරින් ව්‍යුහගත ප්‍රශ්න පත්‍රයක්..."
}

default_hint = placeholder_prompts.get(subject, "ඔබට අවශ්‍ය ප්‍රශ්න පත්‍රයේ මාතෘකාව, ප්‍රශ්න වර්ග (MCQ/Essay) සහ ප්‍රමාණය මෙතැන පැහැදිලිව ලියන්න...")

base_prompt = st.text_area("✍️ ඔබට අවශ්‍ය ප්‍රශ්න පත්‍රයේ විස්තරය (Prompt):", value=default_hint, height=180)

st.write("---")
st.write("📥 ප්‍රශ්න පත්‍රය බාගත කරගැනීමට අවශ්‍ය ක්‍රමය තෝරන්න:")

col1, col2 = st.columns(2)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('w:top', top), ('w:bottom', bottom), ('w:left', left), ('w:right', right)]:
        node = OxmlElement(m)
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def generate_word_document(prompt_text, with_diagrams, sub, lang):
    try:
        api_key = st.secrets["GEMINI_API_KEY"]
    except Exception:
        st.error("❌ System Error: Gemini API Key එක සකසා නැත.")
        return None

    # AI එකට දෙන විධානය තෝරාගත් විෂය සහ භාෂාව අනුව ස්වයංක්‍රීයව හැඩගැස්වීම
    final_prompt = f"You are an expert exam paper setter. Create an official exam paper for the subject '{sub}' in '{lang}' language. "
    final_prompt += f"Based on the user's specific request: {prompt_text}. "
    final_prompt += "Provide ONLY the exam paper text and the marking scheme/answers at the very end. No conversational intro or outro text. "
    
    if with_diagrams:
        final_prompt += " (IMPORTANT: For any questions that strictly require circuits, graphs, or biological/chemical structures, explicitly add a line '[DIAGRAM: Describe what should be drawn here]' right after the question text, so I can format it properly.)"

    try:
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=final_prompt,
        )
        exam_text = response.text
        
        doc = docx.Document()
        
        # පිටුවේ මායිම් සැකසීම
        for section in doc.sections:
            section.top_margin = Inches(1)
            section.bottom_margin = Inches(1)
            section.left_margin = Inches(1)
            section.right_margin = Inches(1)
            
            footer = section.footer
            f_p = footer.paragraphs[0]
            f_p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
            f_run = f_p.add_run("AI Generated | Powered by Dinusha Ratnayake B.Sc")
            f_run.font.name = 'Arial'
            f_run.font.size = Pt(9)
            f_run.italic = True
        
        style = doc.styles['Normal']
        font = style.font
        font.name = 'Arial'
        font.size = Pt(12)
        
        lines = exam_text.split('\n')
        for index, line in enumerate(lines):
            cleaned_line = line.strip().replace("**", "").replace("###", "")
            
            if cleaned_line == "":
                doc.add_paragraph()
                continue
            
            if with_diagrams and ("[DIAGRAM:" in cleaned_line or "රූප සටහන" in cleaned_line or "[DIAGRAM]" in cleaned_line):
                table = doc.add_table(rows=1, cols=1)
                table.alignment = docx.enum.table.WD_TABLE_ALIGNMENT.CENTER
                cell = table.cell(0, 0)
                cell.width = Inches(5.5)
                set_cell_margins(cell, top=400, bottom=400, left=400, right=400)
                
                p_box = cell.paragraphs[0]
                p_box.alignment = WD_ALIGN_PARAGRAPH.CENTER
                run_box = p_box.add_run(f"🖼️ [රූප සටහන / Diagram Space]\n({cleaned_line})")
                run_box.font.name = 'Arial'
                run_box.font.size = Pt(10)
                run_box.italic = True
                doc.add_paragraph()
            else:
                p = doc.add_paragraph()
                run = p.add_run(cleaned_line)
                
                if index == 0:
                    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    run.bold = True
                    run.font.size = Pt(14)
                    
        bio = io.BytesIO()
        doc.save(bio)
        bio.seek(0)
        return bio.getvalue()

    except Exception as e:
        st.error(f"❌ දෝෂයක් මතු විය: {e}")
        return None

# --- Plain Paper බොත්තම ---
with col1:
    if st.button("📄 Generate Plain Paper", use_container_width=True):
        with st.spinner("⏳ ප්‍රශ්න පත්‍රය සකසමින් පවතී..."):
            doc_bytes = generate_word_document(base_prompt, with_diagrams=False, sub=subject, lang=language)
            if doc_bytes:
                st.success("✅ සූදානම්!")
                st.download_button(label="📥 Download Word File", data=doc_bytes, file_name=f"{subject}_Paper.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document", use_container_width=True)

# --- Diagram Paper බොත්තම ---
with col2:
    if st.button("🖼️ Generate with Diagrams", use_container_width=True):
        with st.spinner("⏳ ප්‍රශ්න පත්‍රය සකසමින් පවතී..."):
            doc_bytes = generate_word_document(base_prompt, with_diagrams=True, sub=subject, lang=language)
            if doc_bytes:
                st.success("✅ සූදානම්!")
                st.download_button(label="📥 Download Diagram Word File", data=doc_bytes, file_name=f"{subject}_With_Diagrams_Paper.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document", use_container_width=True)
