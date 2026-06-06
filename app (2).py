import streamlit as st
import docx
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from google import genai
import io

# --- වෙබ් පිටුවේ ප්‍රධාන පෙනුම සකස් කිරීම ---
st.set_page_config(page_title="Gemini Physics Paper Generator", page_icon="⚙️", layout="centered")

st.title("⚙️ Gemini Advanced Physics Paper Generator")
st.subheader("👨‍💻 Developed by: Dinusha Ratnayake B.Sc (දිනූෂ රත්නායක මයා)")
st.write("---")

# --- පරිශීලක අතුරුමුහුණත (GUI Elements) ---
user_api_key = st.text_input("ඇතුලත් කරන්න ඔබගේ Gemini API Key එක (API Key):", type="password", placeholder="AIzaSy...")

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
    if not user_api_key.strip():
        st.error("❌ කරුණාකර ප්‍රථමයෙන් ඔබගේ Gemini API Key එක ඇතුලත් කරන්න!")
        return None
        
    if not prompt_text.strip():
        st.error("❌ කරුණාකර ප්‍රශ්න පත්‍රයට අදාළ Prompt එක ඇතුලත් කරන්න!")
        return None

    final_prompt = prompt_text
    if with_diagrams:
        final_prompt += " (IMPORTANT: For questions that need circuits, graphs, or diagrams, explicitly add a line '[DIAGRAM: Describe what should be drawn here]' right after the question text, so I can format it properly.)"

    try:
        # Gemini API ඇමතීම
        client = genai.Client(api_key=user_api_key.strip())
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=final_prompt,
        )
        exam_text = response.text
        
        # Word Document එක නිර්මාණය කිරීම
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
                    
        # බ්‍රවුසරය හරහා ඩවුන්ලෝඩ් කිරීමට මතකය (Buffer) වෙත සේව් කිරීම
        bio = io.BytesIO()
        doc.save(bio)
        bio.seek(0)
        return bio.getvalue()

    except Exception as e:
        st.error(f"❌ දෝෂයක් මතු විය: {e}")
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
        with str.spinner("⏳ රූප රාමු සහිත ප්‍රශ්න පත්‍රය සකසමින් පවතී..."):
            doc_bytes = generate_word_document(base_prompt, with_diagrams=True)
            if doc_bytes:
                st.success("✅ ප්‍රශ්න පත්‍රය සාර්ථකව නිමවා ඇත!")
                st.download_button(label="📥 Download Diagram Word File", data=doc_bytes, file_name="Physics_Diagram_Paper.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document", use_container_width=True)
