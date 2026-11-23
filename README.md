# Syllabus-to-Notes Generator

**Project No. 27** — a basic Streamlit app that turns pasted syllabus text into short unit-wise study notes and a downloadable Word document.

## What it does

1. Accepts syllabus text pasted by the user.
2. Uses Python to find headings such as `UNIT I`, `UNIT 2`, or `UNIT III` and split the syllabus into units.
3. Sends one Gemini API request for each unit to generate short notes.
4. Combines the notes and creates a `.docx` file with `python-docx`.

## Requirements

- Python 3.10 or later
- A Gemini API key from [Google AI Studio](https://aistudio.google.com/apikey)

## Setup

Open a terminal in this project folder and create a virtual environment:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Set the API key as an environment variable in PowerShell. Replace the example text with your own key:

```powershell
$env:GEMINI_API_KEY = "paste-your-key-here"
```

On macOS or Linux, use:

```bash
export GEMINI_API_KEY="paste-your-key-here"
```

The key is read from the environment at runtime. Do not paste it into `app.py`, commit it, or share it in screenshots.

## Run

```powershell
streamlit run app.py
```

Paste syllabus text with unit headings, select **Generate notes**, then download `syllabus_notes.docx`.

## Sample input and manual check

Copy the contents of [`sample_syllabus.txt`](sample_syllabus.txt) into the app. It contains three unit headings. With a valid API key, confirm that:

1. Notes appear under three unit headings.
2. The download button creates `syllabus_notes.docx`.
3. The downloaded document opens and contains all three units.

To check unit splitting without an API key, run this in the project folder:

```powershell
python -c "from app import split_syllabus_by_unit; text = open('sample_syllabus.txt', encoding='utf-8').read(); units = split_syllabus_by_unit(text); print([title for title, _ in units]); assert len(units) == 3"
```

## Deploy to Streamlit Community Cloud

1. Create a new app at [share.streamlit.io](https://share.streamlit.io/).
2. Select this GitHub repository, the `main` branch, and `app.py` as the main file.
3. In the app settings, add this under **Secrets**, replacing the example with your own key:

   ```toml
   GEMINI_API_KEY = "paste-your-key-here"
   ```

4. Save the secret and reboot the app if it is already running.

The app reads the key from Streamlit Secrets when deployed, and from the `GEMINI_API_KEY` environment variable when run locally.

## API key safety

`.gitignore` excludes local environment files, Streamlit secrets, and virtual environments. Keep your actual key in the `GEMINI_API_KEY` environment variable and never add it to the project files or GitHub.

