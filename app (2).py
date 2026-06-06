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
st.caption("Create Exam Papers for A/L & O/L Subjects in Any Language | Commercial Version 3.2")
st.write("---")

# --- ඔබේ තොරතුරු (මෙහි ඔබේ විස්තර වෙනස් කරන්න) ---
YOUR_WHATSAPP_NUMBER = "94771234567"  # ඔබේ දුරකථන අංකය (94 රටේ කේතය සමඟ, බිංදුව නැතිව)
VALID_ACCESS_CODE = "EXAMPRO2026"     # පාරිභෝගිකයන් සඳහා වන රහස් කේතය

# --- Free Counter එක පවත්වාගෙන යාම (Session State) ---
if "free_credits" not in st.session_state:
    st.session_state.free_credits = 2  # නොමිලේ ලැබෙන වාර ගණන 2කි

# --- WhatsApp Link එක සෑදීම ---
msg = "Hi Dinusha, මට Universal AI Paper Generator එක පාවිච්චි කරන්න Access Code එකක් ගන්න ඕනේ."
encoded_msg = urllib.parse.quote(msg)
whatsapp_url = f"https://wa.me/{YOUR_WHATSAPP_NUMBER}?text={encoded_msg}"

# --- පරිශීලක අතුරුමුහුණත (Access Control) ---
st.sidebar.header("🔑 Access Control")
input_code = st.sidebar.text_input("ඇතුලත් කරන්න ඔබගේ Access Code එක (Premium):", type="password", placeholder="Access Code...")

is_premium = (input_code == VALID_ACCESS_CODE)

# --- ආරක්ෂණ පරීක්ෂාව ---
if not is_premium:
    if st.session_state.free_credits > 0:
        st.sidebar.info(f"🎁 ඔබට නොමිලේ ප්‍රශ්න පත්‍ර {st.session_state.free_credits}ක් සැකසීමට අවස්ථාව ඇත.")
    else:
        st.error("⚠️ ඔබගේ නොමිලේ ලැබුණු අවස්ථා (2 Free Credits) අවසන් වී ඇත!")
        st.info("අසීමිතව ප්‍රශ්න පත්‍ර සැකසීම සඳහා අපගේ WhatsApp අංකය හරහා සම්බන්ධ වී Premium Access Code එක ලබාගන්න.")
        
        st.markdown(f'''
        <a href="{whatsapp_url}" target="_blank">
            <button style="background-color: #25D366; color: white; border: none; padding: 10px 20px; font-size: 16px; border-radius: 5px; cursor: pointer; width: 100%;">
                💬 Get Premium Access Code via WhatsApp
            </button>
        </a>
        ''', unsafe_allowed_html=True)
        
        st.stop()
else:
    st.sidebar.success("🔒 Premium Access Active! ඔබට අසීමිතව ප්‍රශ්න පත්‍ර සකස් කළ හැක.")

# --- විෂය සහ භාෂාව තෝරාගැනීමේ කොටස ---
col_sub, col_lang = st.columns(2)

with col_sub:
    subject = st.selectbox(
        "📚 විෂය තෝරන්න (Select Subject):",
        [
            "O/L Science (විද්‍යාව)", "O/L Mathematics (ගණිතය)", "O/L History (ඉතිහාසය)",
            "O/L Sinhala (සිංහල)", "O/L English (ඉංග්‍රීසි)", "O/L ICT (තොරතුරු තාක්ෂණය)",
            "O/L Commerce (වාණිජ්‍යය)", "O/L Geography (භූගෝල විද්‍යාව)", "O/L Health (සෞඛ්‍යය)",
            "A/L Physics (භෞතික විද්‍යාව)", "A/L Chemistry (රසායන විද්‍යාව)", "A/L Combined Mathematics (සංයුක්ත ගණිතය)",
            "A/L Biology (ජීව විද්‍යාව)", "A/L ICT (තොරතුරු තාක්ෂණය)", "A/L History (ඉතිහාසය)",
            "A/L Business Studies (ව්‍යාපාර අධ්‍යයනය)", "A/L Accounting (ගිණුම්කරණය)", "A/L Economics (ආර්ථික විද්‍යාව)",
            "Other (Mention in prompt)"
        ]
    )

with col_lang:
    language = st.selectbox(
        "🌐 මාධ්‍යය/භාෂාව තෝරන්න (Select Language):",
        ["Sinhala (සිංහල)", "English", "Tamil (தமிழ்)"]
    )

placeholder_prompts = {
    "O/L Science (විද්‍යාව)": "10 ශ්‍රේණිය 'ආලෝකය' පාඩමේ වර්තනය සහ දර්පණ ඇසුරින් MCQ 10ක් සහ ව්‍යුහගත ප්‍රශ්නයක් සකසන්න...",
    "O/L Mathematics (ගණිතය)": "11 ශ්‍රේණිය 'වර්ගජ සමීකරණ' පාඩම ඇසුරින් පියවර සහිතව විසඳිය යුතු ව්‍යුහගත ප්‍රශ්න 3ක් සකසන්න...",
    "A/L Physics (භෞතික විද්‍යාව)": "ධාරා විද්‍යුතය පාඩමේ කිර්චොෆ් නියම ඇසුරින් විසඳිය යුතු MCQ ප්‍රශ්න 5ක් සහ ව්‍යුහගත රචනා ප්‍රශ්නයක්..."
}

default_hint = placeholder_prompts.get(subject, "ඔබට අවශ්‍ය ප්‍රශ්න පත්‍රයේ මාතෘකාව, ප්‍රශ්න වර්ග (MCQ/Essay) සහ ප්‍රමාණය මෙතැන පැහැදිලිව ලියන්න...")

base_prompt = st.text_area("✍️ ඔබට අවශ්‍ය ප්‍රශ්න පත්‍රයේ විස්තරය (Prompt):", value=default_hint, height=180)

st.write("---")
st.subheader("📥 ප්‍රශ්න පත්‍රය බාගත කරගැනීමට අවශ්‍ය ක්‍රමය තෝරන්න:")

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
        return "api_error"

    final_prompt = f"You are an expert school exam paper setter in Sri Lanka. Create an official exam paper for the subject '{sub}' in '{lang}' language. "
    final_prompt += f"Based on the user's specific request: {prompt_text}. "
    final_prompt += "Provide ONLY the exam paper text and the marking scheme/answers at the very end. No conversational intro or outro text. "
    
    if with_diagrams:
        final_prompt += " (IMPORTANT: For any questions that strictly require circuits, graphs, geometry, or biological/chemical structures, explicitly add a line '[DIAGRAM: Describe what should be drawn here]' right after the question text, so I can format it properly.)"

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
        return str(e)

# --- ප්‍රශ්න පත්‍ර ජනනය කිරීමේ ස්ථාවර පද්ධතිය ---
col1, col2 = st.columns(2)

with col1:
    if st.button("📄 Generate Plain Paper", use_container_width=True):
        with st.spinner("⏳ ප්‍රශ්න පත්‍රය සකසමින් පවතී... කරුණාකර රැඳී සිටින්න."):
            res = generate_word_document(base_prompt, False, subject, language)
            
            if res == "api_error":
                st.error("❌ System Error: Gemini API Key එක සකසා නැත. Streamlit Cloud Dashboard එක පරීක්ෂා කරන්න.")
            elif isinstance(res, str):
                st.error(f"❌ AI සේවාදායකයේ තාවකාලික දෝෂයකි. කරුණාකර සුළු මොහොතකින් නැවත උත්සාහ කරන්න: {res}")
            else:
                if not is_premium:
                    st.session_state.free_credits -= 1
                st.success("✅ සාර්ථකයි! පහත බොත්තමෙන් බාගත කරගන්න.")
                st.download_button(label="📥 Download Word File", data=res, file_name=f"{subject}_Paper.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document", use_container_width=True)

with col2:
    if st.button("🖼️ Generate with Diagrams", use_container_width=True):
        with st.spinner("⏳ ප්‍රශ්න පත්‍රය සකසමින් පවතී... කරුණාකර රැඳී සිටින්න."):
            res = generate_word_document(base_prompt, True, subject, language)
            
            if res == "api_error":
                st.error("❌ System Error: Gemini API Key එක සකසා නැත. Streamlit Cloud Dashboard එක පරීක්ෂා කරන්න.")
            elif isinstance(res, str):
                st.error(f"❌ AI සේවාදායකයේ තාවකාලික දෝෂයකි. කරුණාකර සුළු මොහොතකින් නැවත උත්සාහ කරන්න: {res}")
            else:
                if not is_premium:
                    st.session_state.free_credits -= 1
                st.success("✅ සාර්ථකයි! පහත බොත්තමෙන් බාගත කරගන්න.")
                st.download_button(label="📥 Download Diagram Word File", data=res, file_name=f"{subject}_With_Diagrams_Paper.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document", use_container_width=True)
