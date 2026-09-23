from flask import Flask, render_template, request, session
from groq import Groq
from tavily import TavilyClient
from dotenv import load_dotenv
import os

app = Flask(__name__)
app.secret_key = "insightsearch-secret-key"
# Load API Keys
load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

# Clients
client = Groq(api_key=GROQ_API_KEY)
tavily = TavilyClient(api_key=TAVILY_API_KEY)


@app.route("/")
def home():
    return render_template("index.html")

@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/search", methods=["POST"])
def search():

    query = request.form["query"]

    # Live Web Search
    web = tavily.search(
        query=query,
        search_depth="advanced",
        max_results=5
    )

    web_info = ""

    for result in web["results"]:
        web_info += result["content"] + "\n"

    # AI Answer
    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        temperature=0.2,
        messages=[
            {
                "role": "system",
                "content": """
You are InsightSearch AI.

Always give accurate and latest information.

Answer in this format:

📖 Summary
(2-3 lines)

📚 Details
(Simple explanation)

💡 Interesting Facts
(3 bullet points)

🌐 Latest Information
(Current information if available)

Always trust the latest web information provided.
Never answer from old knowledge if latest information is available.
"""
            },
            {
                "role": "user",
                "content": f"""
Question:
{query}

Latest Web Information:
{web_info}

Answer only using the latest web information.
If latest information exists, ignore old knowledge.
"""
            }
        ]
    )

    answer = response.choices[0].message.content
    session["last_query"] = query
    session["last_answer"] = answer

    # Sources
    sources = []

    for result in web["results"]:
     sources.append({
        "title": result["title"],
        "url": result["url"],
        "content": result["content"]
    })
    return render_template(
        "result.html",
        query=query,
        answer=answer,
        sources=sources
    )


@app.route("/follow-up", methods=["POST"])
def follow_up():

    question = request.form["question"]

    previous_query = session.get("last_query", "")
    previous_answer = session.get("last_answer", "")

    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        temperature=0.2,
        messages=[
            {
                "role": "system",
                "content": """
You are InsightSearch AI.

Answer the user's follow-up question clearly and simply.

Use the previous search and previous AI answer as context.
If the user asks a doubt about the previous answer, explain it directly.
"""
            },
            {
                "role": "user",
                "content": f"""
Previous Search:
{previous_query}

Previous AI Answer:
{previous_answer}

Follow-up Question:
{question}
"""
            }
        ]
    )

    follow_up_answer = response.choices[0].message.content

    return render_template(
        "follow_up.html",
        question=question,
        answer=follow_up_answer
    )

if __name__ == "__main__":
    app.run(debug=True)