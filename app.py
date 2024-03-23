from flask import Flask
import anthropic
import os
from bs4 import BeautifulSoup


app = Flask(__name__)

@app.route("/")
def summarize_web_page():
    with open("expedia.html", "r") as file:
        html_content = file.read()

    soup = BeautifulSoup(html_content, 'html.parser')
    main_content = str(soup.get_text())
    
    prompt = "Summarize this web page to elder people or non tech people in one or two simple sentences. guide them what they can do with this website. Here's the web page in HTML format: \n\n" + main_content[:50000] + "\n\n  "
    
    client = anthropic.Anthropic(
        api_key=os.environ.get("ANTHROPIC_API_KEY"),
    )
    message = client.messages.create(
        model="claude-3-opus-20240229",
        max_tokens=1000,
        temperature=0,
        messages=[
        {"role": "user", "content": prompt},
    ]
    )
    print(message.content)
    return message.content[0].text