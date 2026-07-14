from flask import Flask, render_template, request, jsonify
from anthropic import Anthropic
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
client = Anthropic()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.json
    resume = data.get("resume", "")
    job_description = data.get("job_description", "")

    if not resume or not job_description:
        return jsonify({"error": "请填写简历和职位描述"}), 400

    prompt = f"""
    你是一个专业的简历分析师。请分析以下简历和职位描述的匹配情况。

    【简历内容】
    {resume}

    【职位描述】
    {job_description}

    请用以下格式回复：
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