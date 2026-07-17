from flask import Flask, render_template, request, jsonify
from anthropic import Anthropic
from dotenv import load_dotenv
import os
import pdfplumber
import docx
import io

load_dotenv()

app = Flask(__name__)
client = Anthropic()

def extract_text_from_pdf(file):
    text = ""
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ""
    return text

def extract_text_from_docx(file):
    doc = docx.Document(file)
    text = ""
    for para in doc.paragraphs:
        text += para.text + "\n"
    return text

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/analyze", methods=["POST"])
def analyze():
    resume_text = ""

    if "resume_file" in request.files and request.files["resume_file"].filename:
        file = request.files["resume_file"]
        filename = file.filename.lower()
        file_bytes = io.BytesIO(file.read())

        if filename.endswith(".pdf"):
            resume_text = extract_text_from_pdf(file_bytes)
        elif filename.endswith(".docx"):
            resume_text = extract_text_from_docx(file_bytes)
        else:
            return jsonify({"error": "只支持 PDF 或 Word (.docx) 文件"}), 400
    else:
        resume_text = request.form.get("resume", "")

    job_title = request.form.get("job_title", "")
    language = request.form.get("language", "zh")

    if not resume_text or not job_title:
        return jsonify({"error": "请填写简历内容和目标职位"}), 400

    if language == "en":
        prompt = f"""
You are a professional resume analyst. Analyze the match between the following resume and the target job position.

[Resume Content]
{resume_text}

[Target Job Title]
{job_title}

Based on your knowledge of what this role typically requires, please respond in the following format:
1. Match Score: X/100
2. Missing Keywords: List 3-5 keywords
3. Improvement Suggestions: Provide 2-3 specific suggestions
"""
    else:
        prompt = f"""
你是一个专业的简历分析师。请分析以下简历与目标职位的匹配情况。

【简历内容】
{resume_text}

【目标职位】
{job_title}

根据你对该职位通常要求的了解，请用以下格式回复：
1. 匹配度评分：X/100
2. 缺少的关键词：列出3-5个
3. 修改建议：给出2-3条具体建议
"""

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}]
    )

    return jsonify({"result": message.content[0].text})

if __name__ == "__main__":
    app.run(debug=True)