from flask import Flask, request, render_template, redirect, url_for
import google.generativeai as genai
import os

app = Flask(__name__)


genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Prompt template for website generation
prompt_template = """
You are a web developer assistant. Given a one-line business idea: "{idea}", generate a basic HTML+CSS homepage with a header, a short about section, and a footer.
Only return raw HTML and CSS inside <style> tags. Do NOT include markdown, explanations, or code fences.
"""

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    try:
        idea = request.form.get("idea")
        if not idea:
            return "No business idea provided", 400

        model = genai.GenerativeModel("gemini-pro")
        response = model.generate_content(prompt_template.format(idea=idea))

        # Handle empty or invalid response
        generated_html = response.text.strip()
        if not generated_html:
            return "Model returned empty response", 500

        # Save to file (optional)
        with open("static/generated_site.html", "w", encoding="utf-8") as f:
            f.write(generated_html)

        # Redirect to preview
        return redirect(url_for('preview'))

    except Exception as e:
        return f"Error during generation: {str(e)}", 500

@app.route('/preview')
def preview():
    return render_template("preview.html")

if __name__ == '__main__':
    app.run(debug=True)
