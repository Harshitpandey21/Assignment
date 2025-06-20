from flask import Flask, request, jsonify, render_template_string
import os
import chromadb
from chromadb.utils import embedding_functions
from sentence_transformers import SentenceTransformer
from src.scraping_ai import *

chroma_client = chromadb.Client()
embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)
collection = chroma_client.get_or_create_collection(
    name="hitl_editor_collection",
    embedding_function=embedding_fn
)

app = Flask(__name__)

HTML_TEMPLATE="""<!DOCTYPE html>
<html>
<head>
    <title>Human-in-the-Loop Editor</title>
</head>
<body>
    <h2>Step {{ step }}: {{ title }}</h2>
    <form method="POST">
        <textarea name="content" rows="30" cols="100">{{ content }}</textarea><br><br>
        <button type="submit">Submit for Next Step</button>
    </form>
</body>
</html>
"""


@app.route("/", methods=["GET", "POST"])
def hitl_editor():
    if not os.path.exists("chapter_1.txt"):
        fetch_chapter_and_screenshot()

    step = int(request.args.get("step", 1))
    if step == 1:
        with open("chapter_1.txt", "r", encoding="utf-8") as f:
            content = f.read()
        if request.method == "POST":
            with open("edited_step1.txt", "w", encoding="utf-8") as f:
                f.write(request.form["content"])
            return jsonify({"next": "/?step=2"})
        return render_template_string(HTML_TEMPLATE, title="Original Content (Human Edit)", step=step, content=content)

    elif step == 2:
        with open("edited_step1.txt", "r", encoding="utf-8") as f:
            human_edited = f.read()
        ai_reviewed = generate_or_review_content(f"Review the following for grammar and coherence:\n\n{human_edited}")
        with open("ai_reviewed_step2.txt", "w", encoding="utf-8") as f:
            f.write(ai_reviewed)
        return render_template_string(HTML_TEMPLATE, title="AI Suggestions", step=step, content=ai_reviewed)

    elif step == 3:
      with open("ai_reviewed_step2.txt", "r", encoding="utf-8") as f:
        reviewed = f.read()

      if request.method == "POST":
        content = request.form["content"]
        with open("final_approved.txt", "w", encoding="utf-8") as f:
            f.write(content)
        collection.add(
            documents=[content],
            metadatas=[{"source": "human_approved"}],
            ids=["final_doc_1"]
        )

        return jsonify({"message": "Final content saved and stored in ChromaDB."})

      return render_template_string(HTML_TEMPLATE, title="Final Human Approval", step=step, content=reviewed)



    return "Invalid step.", 400

if __name__ == "__main__":
    app.run(host="0.0.0.0",port=8080,debug=True)