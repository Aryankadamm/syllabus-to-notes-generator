"""Basic syllabus-to-notes generator for Project No. 27."""

import os
import re
from io import BytesIO

import streamlit as st
from docx import Document
from google import genai
from streamlit.errors import StreamlitSecretNotFoundError


MODEL_NAME = "gemini-3.5-flash-lite"
UNIT_HEADING = re.compile(
    r"^\s*(unit\s+(?:[ivxlcdm]+|\d+)\b[^\r\n]*)\s*$",
    re.IGNORECASE | re.MULTILINE,
)


def split_syllabus_by_unit(syllabus_text):
    """Return (unit heading, syllabus content) pairs from pasted text."""
    matches = list(UNIT_HEADING.finditer(syllabus_text))
    units = []

    for index, match in enumerate(matches):
        content_start = match.end()
        content_end = matches[index + 1].start() if index + 1 < len(matches) else len(syllabus_text)
        content = syllabus_text[content_start:content_end].strip()
        units.append((match.group(1).strip(), content))

    return units


def generate_unit_notes(client, unit_title, unit_syllabus):
    """Make one Gemini API call and return short notes for one unit."""
    prompt = f"""Create short, clear study notes for the syllabus unit below.
Use simple language, organize the notes with brief headings and bullet points,
and cover only the topics supplied. Do not invent syllabus topics.

Unit: {unit_title}
Syllabus topics:
{unit_syllabus or unit_title}
"""
    response = client.models.generate_content(model=MODEL_NAME, contents=prompt)
    notes = (response.text or "").strip()
    if not notes:
        raise ValueError(f"Gemini returned no notes for {unit_title}.")
    return notes


def create_notes_docx(unit_notes):
    """Combine unit notes into an in-memory Word document."""
    document = Document()
    document.add_heading("Syllabus Study Notes", level=0)

    for unit_title, notes in unit_notes:
        document.add_heading(unit_title, level=1)
        for paragraph in notes.splitlines():
            paragraph = paragraph.strip()
            if paragraph:
                if paragraph.startswith("### "):
                    document.add_heading(paragraph[4:], level=3)
                elif paragraph.startswith("## "):
                    document.add_heading(paragraph[3:], level=2)
                elif paragraph.startswith("# "):
                    document.add_heading(paragraph[2:], level=2)
                elif paragraph.startswith(("- ", "* ")):
                    document.add_paragraph(paragraph[2:], style="List Bullet")
                elif re.match(r"\d+[.)]\s+", paragraph):
                    document.add_paragraph(re.sub(r"^\d+[.)]\s+", "", paragraph), style="List Number")
                else:
                    document.add_paragraph(paragraph)

    output = BytesIO()
    document.save(output)
    output.seek(0)
    return output.getvalue()


st.set_page_config(page_title="Syllabus-to-Notes Generator", page_icon="📚")
st.title("Syllabus-to-Notes Generator")
st.caption("Project No. 27 · Paste a syllabus to create short unit-wise study notes.")

syllabus_text = st.text_area(
    "Paste syllabus text",
    height=300,
    placeholder="Example: UNIT I\nIntroduction to the subject...\n\nUNIT II\nNext topics...",
)

try:
    api_key = st.secrets.get("GEMINI_API_KEY", "").strip()
except (KeyError, StreamlitSecretNotFoundError):
    api_key = ""
api_key = api_key or os.getenv("GEMINI_API_KEY", "").strip()
if not api_key:
    st.info("Set the GEMINI_API_KEY environment variable before generating notes.")

if st.button("Generate notes", type="primary", disabled=not syllabus_text.strip()):
    units = split_syllabus_by_unit(syllabus_text)
    if not units:
        st.error("No unit headings found. Add headings such as UNIT I, UNIT 2, or UNIT III.")
    elif not api_key:
        st.error("Gemini API key is missing. Set GEMINI_API_KEY and restart Streamlit.")
    else:
        try:
            client = genai.Client(api_key=api_key)
            generated_notes = []
            progress = st.progress(0, text="Generating notes unit by unit...")

            for index, (unit_title, unit_syllabus) in enumerate(units, start=1):
                notes = generate_unit_notes(client, unit_title, unit_syllabus)
                generated_notes.append((unit_title, notes))
                progress.progress(index / len(units), text=f"Finished {unit_title}")

            docx_bytes = create_notes_docx(generated_notes)
            st.success(f"Notes generated for {len(generated_notes)} units.")
            for unit_title, notes in generated_notes:
                with st.expander(unit_title, expanded=True):
                    st.markdown(notes)

            st.download_button(
                "Download notes as .docx",
                data=docx_bytes,
                file_name="syllabus_notes.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            )
        except Exception as error:
            st.error(f"Could not generate notes: {error}")

