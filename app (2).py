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
st.set_page_config(page_title="A/L Physics Paper Generator Pro", page_icon="📝", layout="centered")

st.title("📝 A/L Physics Paper Generator Pro")
st.caption("Developed by Dinusha Ratnayake B.Sc | Commercial Version 1.0")
st.write("---")

# --- ඔබේ තොරතුරු (මෙතන ඔබේ විස්තර වෙනස් කරන්න) ---
YOUR_WHATSAPP_NUMBER = "94771234567"  # ඔබේ දුරකථන අංකය (94 රටේ කේතය සමඟ, බිංදුව නැතිව)
VALID_ACCESS_CODE = "PHYSICS2026"     # ඔබ පාරිභෝගිකයන්ට දෙන රහස් කේතය (Password)

# --- WhatsApp Link එක සෑදීම ---
msg = "Hi Dinusha, මට Paper Generator එක පාවිච්චි කරන්න Access Code එකක් ගන්න ඕනේ."
encoded_msg = urllib.parse.quote(msg)
whatsapp_url = f"https://wa.me/{YOUR_WHATSAPP_NUMBER}?text={encoded_msg}"

# --- පරිශීលක අතුරුමුහුණත (Access Code Check) ---
st.sidebar.header("🔑🔑 Access Control")
input_code = st.sidebar.text_input("ඇතුලත් කරන්න ඔබගේ Access Code එක:", type="password", placeholder="කේතය මෙතන ලියන්න...")

if input_code != VALID_ACCESS_CODE:
    st.warning("⚠️ කරුණාකර මෙම මෙවලම භාවිත කිරීම සඳහා නිවැරදි 'Access Code' එක ඇතුළත් කරන්න.")
    st.info("ඔබ සතුව Access Code එකක් නොමැති නම් හෝ එය ලබා ගැනීමට අවශ්‍ය නම් පහත බොත්තම හරහා අපව WhatsApp මඟින් සම්බන්ධ කරගන්න.")
    
    st.markdown(f'''
    <a href="{whatsapp_url}" target="_blank">
        <button style="background-color: #25D366; color: white; border: none; padding: 10px 20px; font-size: 16px; border-radius: 5px; cursor: pointer; width: 100%;">
            💬 Get Access Code via WhatsApp
        </button>
    </a>
    ''', unsafe_allowed_html=True)
    
    st.stop() # කේතය නිවැරදි නැත්නම් වෙබ් ඇප් එකේ ඉතිරි කොටස පෙන්වීම නතර කරයි.

# --- කේතය නිවැරදි නම් පමණක් පහත කොටස ක්‍රියාත්මක වේ ---
st.success("🔒 Access Granted! ඔබට දැන් ප්‍රශ්න පත්‍ර සකස් කළ හැක.")

default_prompt = """උසස් පෙළ භෞතික විද්‍යාව (A/L Physics) විෂය නිර්දේශයට අනුව "ධාරා විද්‍යුතය" පාඩමේ කිර්චොෆ් නියම (Kirchhoff Laws) පදනම් කරගෙන රූප සටහන් ඇසුරින් විසඳිය යුතු බහුවරණ ප්‍රශ්න (MCQ) 5ක් සහ පරිපථ සටහනක් සහිත ව්‍යුහගත රචනා ප්‍රශ්නයක් (Structured Essay) සිංහල මාධ්‍යයෙන් සකස් කරන්න. පිළිතුරු පත්‍රය අවසානයට ඇතුලත් කරන්න. කිසිදු අමතර හැඳින්වීමක් නැතිව ප්‍රශ්න පත්‍රය පමණක් ලබාදෙන්න."""

base_prompt = st.text_area("ඔබට අවශ්‍ය ප්‍රශ්න පත්‍රයේ විස්තරය (Prompt):", value=default_prompt, height=200)

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

def generate_word_document(prompt_text, with_diagrams):
    # Streamlit Secrets එකෙන් ආරක්ෂිතව API Key එක ලබාගැනීම
    try:
        api_key = st.secrets["GEMINI_API_KEY"]
    except Exception:
        st.error("❌ System Error: Gemini API Key එක සකසා නැත. කරුණාකර Streamlit Cloud Dashboard එක පරීක්ෂා කරන්න.")
        return None

    final_prompt = prompt_text
    if with_diagrams:
        final_prompt += " (IMPORTANT: For questions that need circuits, graphs, or diagrams, explicitly add a line '[DIAGRAM: Describe what should be drawn here]' right after the question text, so I can format it properly.)"

    try:
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=final_prompt,
        )
        exam_text = response.text
        
        doc = docx.Document()
        
        for section in doc.sections:
            section.top_margin = Inches(1)
            section.bottom_margin = Inches(1)
            section.left_margin = Inches(1)
            section.right_margin = Inches(1)
            
            footer = section.footer
            f_p = footer.paragraphs[0]
            f_p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
            f_run = f_p.add_run("Developed by: Dinusha Ratnayake B.Sc")
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
                run_box = p_box.add_run(f"🖼️ [රූප සටහන සඳහා වෙන් කළ ස්ථානය]\n({cleaned_line})")
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
        st.error(f"❌ දෝෂයක් mthe විය: {e}")
        return None

# --- Plain Paper බොත්තම ක්‍රියාකාරීත්වය ---
with col1:
    if st.button("📄 Generate Plain Paper", use_container_width=True):
        with st.spinner("⏳ ප්‍රශ්න පත්‍රය සකසමින් පවතී..."):
            doc_bytes = generate_word_document(base_prompt, with_diagrams=False)
            if doc_bytes:
                st.success("✅ ප්‍රශ්න පත්‍රය සාර්ථකව නිමවා ඇත!")
                st.download_button(label="📥 Download Plain Word File", data=doc_bytes, file_name="Physics_Plain_Paper.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document", use_container_width=True)

# --- Diagram Paper බොත්තම ක්‍රියාකාරීත්වය ---
with col2:
    if st.button("🖼️ Generate with Diagrams", use_container_width=True):
        with st.spinner("⏳ රූප රාමු සහිත ප්‍රශ්න පත්‍රය සකසමින් පවතී..."):
            doc_bytes = generate_word_document(base_prompt, with_diagrams=True)
            if doc_bytes:
                st.success("✅ ප්‍රශ්න පත්‍රය සාර්ථකව නිමවා ඇත!")
                st.download_button(label="📥 Download Diagram Word File", data=doc_bytes, file_name="Physics_Diagram_Paper.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document", use_container_width=True)
