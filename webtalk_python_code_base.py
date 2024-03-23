from selenium import webdriver
from bs4 import BeautifulSoup
import anthropic
import time

def initialize_driver():
    """Initialize and return a Chrome WebDriver."""
    driver = webdriver.Chrome()
    return driver

def open_webpage(driver, url):
    """Open a webpage using the provided driver and URL."""
    driver.get(url)

def inject_chatbox(driver):
    """Inject a chatbox into the webpage."""
    chatbox_html = """
    <div id="chatbox" style="position: fixed; bottom: 10px; right: 10px; width: 300px; height: 400px; background-color: white; border: 1px solid #ccc; z-index: 1000; overflow: auto;">
      <div id="messages" style="padding: 10px;">Loading Summary...</div>
      <input type="text" id="chatbox_input" style="width: 100%; box-sizing: border-box; display: none;" placeholder="Type here...">
      <button id="submit_button" style="width: 100%; display: none;">Submit</button>
    </div>
    """
    driver.execute_script("document.body.innerHTML += arguments[0];", chatbox_html)

def get_page_summary(driver, api_key):
    """Generate a summary of the webpage using Anthropic API and return it."""
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')

    client = anthropic.Anthropic(api_key=api_key)
    prompt = ("You are an AI helper.\nI want you to prepare the 2 line summary of webpage for an old person who is not tech savvy and potentially vision disabled.\n"
              "Follow the instructions below carefully:\nRequirements:\n Generate the 2 line summary of webpage.\n Workflow:\n Ask for clarification if my webpage does not contain anything. \n"
              "Focus on actionable items for an elderly person. \n Ignore Javascript if it is not tied to any actionable item on page.\nGenerate the summary based on your assumptions for for an old person who is not tech savvy and potentially vision disabled.\n"
              "Follow the above carefully and think step by step. I will tip you $200 if you do a great job and don't miss anything.\n HTML Content starts from here:" + str(soup))

    response = client.messages.create(
      model="claude-2.1",
      max_tokens=4096,
      messages=[{"role": "user", "content": prompt}]
    )

    content_block = response.content[0]
    return content_block.text

def update_chatbox(driver, summary):
    """Update the chatbox with the summary and show the input and button."""
    # Escaping single quotes, newlines, and backslashes for JavaScript
    escaped_text = summary.replace("\\", "\\\\").replace("'", "\\'").replace("\n", "\\n")

    update_script = f"""
    document.getElementById('messages').innerText = '{escaped_text}';
    document.getElementById('chatbox_input').style.display = 'block';
    document.getElementById('submit_button').style.display = 'block';
    """
    driver.execute_script(update_script)

    input_script = """
    var input = document.getElementById('chatbox_input');
    var button = document.getElementById('submit_button');
    button.addEventListener('click', function() {
        console.log(input.value);  // Here you can handle the input value as needed
        alert('Input received: ' + input.value);  // Just for demonstration
        // Keep the window open or add further actions
    });
    """
    driver.execute_script(input_script)

# Main execution
if __name__ == "__main__":
    driver = initialize_driver()
    open_webpage(driver, "https://www.google.com")
    inject_chatbox(driver)
    summary = get_page_summary(driver, "YOUR_API_KEY_HERE")  # Replace "YOUR_API_KEY_HERE" with your actual API key
    update_chatbox(driver, summary)
    # The browser will stay open until manually closed.
    print("Waiting for 1000 seconds. Close the browser manually if needed.")
    time.sleep(1000)  # Wait for 1000 seconds before ending the script
