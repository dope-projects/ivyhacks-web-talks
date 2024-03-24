from selenium import webdriver
from bs4 import BeautifulSoup
from openai import OpenAI
import time
from dotenv import load_dotenv
import os
from selenium.webdriver.common.alert import Alert
from selenium.common.exceptions import NoAlertPresentException


# Load environment variables from .env file
load_dotenv()

# Access your environment variable
api_key = os.getenv('OPENAI_API_KEY')


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
    


# def extract_important_content(html):
    # soup = BeautifulSoup(html, 'html.parser')
    
    # # Find the main content area; adjust selectors as necessary
    # main_content = soup.find('main') or soup.find('article') or soup.body
    
    # # Exclude less relevant sections
    # for script_or_style in main_content.find_all(['script', 'style', 'nav', 'footer']):
        # script_or_style.decompose()  # Remove these tags
    
    # # Extract text, optionally further process it to remove or summarize
    # text = main_content.get_text(separator=' ', strip=True)
    
    # # Here you could further summarize the text if needed
    # return text

def extract_actionable_content(html):
    soup = BeautifulSoup(html, 'html.parser')
    
    # Initialize an empty list to store summaries of actionable elements
    actionable_items = []

    # Look for form elements, as they typically indicate user input actions
    forms = soup.find_all('form')
    for form in forms:
        form_summary = "Form available for user input."
        actionable_items.append(form_summary)

    # Look for clickable buttons and links
    buttons = soup.find_all('button')
    links = soup.find_all('a', href=True)

    for button in buttons:
        button_summary = f"Button: {button.text.strip()}" if button.text.strip() else "Unnamed Button"
        actionable_items.append(button_summary)

    for link in links:
        if link.text.strip():  # Only consider links with text
            link_summary = f"Link to {link['href']}: {link.text.strip()}"
            actionable_items.append(link_summary)

    # Summarize actionable content
    if not actionable_items:
        return "No actionable items found."
    return "Actionable items include: " + ", ".join(actionable_items)

def get_page_summary(driver, api_key):
    """Generate a summary of the webpage using Anthropic API and return it."""
    html = driver.page_source
    soup = extract_actionable_content(html)
    
    client = OpenAI(
      api_key=api_key,  # Ensure your API key is set as an environment variable
    )
    
    prompt = ("You are an AI helper.\nI want you to prepare the 2 line summary of webpage for an old person who is not tech savvy and potentially vision disabled.\n"
              "Follow the instructions below carefully:\nRequirements:\n Generate the 2 line summary of webpage.\n Workflow:\n Ask for clarification if my webpage does not contain anything. \n"
              "Focus on actionable items for an elderly person. \n Ignore Javascript if it is not tied to any actionable item on page.\nGenerate the summary based on your assumptions for for an old person who is not tech savvy and potentially vision disabled.\n"
              "Follow the above carefully and think step by step. I will tip you $200 if you do a great job and don't miss anything.\n HTML Content starts from here:" + str(soup))

    # Generating response from gpt-3.5-turbo
    openai_response = client.chat.completions.create(
        model='gpt-3.5-turbo',  # You may want to update the model if needed
        messages=[{'role': 'user', 'content': prompt}]
    )

    content_block = openai_response.choices[0].message.content
    return content_block


def wait_for_user_input(driver):
    while True:
        try:
            Alert(driver).accept()  # Close the alert if present
        except NoAlertPresentException:
            pass  # If no alert is present, just ignore
        
        is_submitted = driver.execute_script("return document.getElementById('is_submitted').value;")
        if is_submitted == 'yes':
            user_input = driver.execute_script("return document.getElementById('chatbox_input').value;")
            return user_input
        time.sleep(1)  # Wait a bit before checking again to reduce load


def update_chatbox_prompt_1(driver, summary):
    """Update the chatbox to hide the submit button and clear the summary after submission, then show 'working on it', while retaining button aesthetics."""
    escaped_text = summary.replace("\\", "\\\\").replace("'", "\\'").replace("\n", "\\n")

    # Update the chatbox content and make input field and button visible
    update_script = f"""
    document.getElementById('messages').innerText = '{escaped_text}';
    document.getElementById('chatbox_input').style.display = 'block';
    document.getElementById('submit_button').style.display = 'block';
    document.getElementById('submit_button').style.backgroundColor = '#f0f0f0';
    document.getElementById('submit_button').style.border = '1px solid #ccc';
    document.getElementById('submit_button').style.padding = '10px';
    document.getElementById('submit_button').style.cursor = 'pointer';
    """
    driver.execute_script(update_script)

    # Modify script for button click to hide the submit button, display "working on it..." message, and retain aesthetics
    input_script = """
    var input = document.getElementById('chatbox_input');
    var button = document.getElementById('submit_button');
    var messages = document.getElementById('messages');
    input.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            button.click();
        }
    });
    button.addEventListener('click', function() {
        document.getElementById('is_submitted').value = 'yes';
        messages.innerText = 'Working on it...';
        input.style.display = 'none';   // Optionally hide the input as well
        // Hide the button by setting display to 'none'
        this.style.display = 'none';
    });
    // Add the aesthetics and functionality to handle mouse down and up events for the button
    button.onmousedown = function() {
        this.style.backgroundColor = '#d0d0d0';
    };
    button.onmouseup = function() {
        this.style.backgroundColor = '#f0f0f0';
    };
    if (!document.getElementById('is_submitted')) {
        var hiddenInput = document.createElement('input');
        hiddenInput.type = 'hidden';
        hiddenInput.id = 'is_submitted';
        hiddenInput.value = 'no';
        document.body.appendChild(hiddenInput);
    }
    """
    driver.execute_script(input_script)

def get_actionable_items(driver, api_key, user_input):
    """Generate a summary of the webpage using OpenAI's API and return it."""
    html = driver.page_source
    soup = extract_actionable_content(html)
    client = OpenAI(
      api_key=api_key,  # Ensure your API key is set as an environment variable
    )
    prompt = ("""You are now an advanced intelligent assistant tasked with meticulously examining the content of a webpage. Your primary objective is to identify all forms that require user input and any text that suggests actionable items such as filling out information, signing up, or providing feedback. Importantly, you must also take into account any specific input or queries provided by a user interacting with the webpage. This means, if a user has entered certain information or posed questions, you should use this context to guide your identification and explanation of relevant actionable items.

                For instance, if the user has shown interest in signing up for a newsletter by asking about it, focus on detailing the signup process and what information is needed (like name, email address, preferences). Similarly, if the user input suggests they are looking for feedback options, direct your attention to summarizing how and where they can leave their feedback on the webpage.

                Remember, your role is to do this analysis quietly and without taking any direct actions such as clicking buttons or following links. Your goal is to compile a comprehensive list of these actionable items, clearly describing each and linking them back to the user's input or queries where applicable. Your insights should aim to support users in navigating the webpage, making their experience as personalized, seamless, and efficient as possible.

                You will only share javascript which can be executed on the webpage and nothing else.
                
                Your output will be in following format:
                Action Number , Javascript code
                1, [Code1]
                2, [Code2]

                User Input : """ + str(user_input) + """ HTML page Details: """ + str(soup))

    # Generating response from gpt-3.5-turbo
    # Generating response from gpt-3.5-turbo
    openai_response = client.chat.completions.create(
        model='gpt-3.5-turbo',  # You may want to update the model if needed
        messages=[{'role': 'user', 'content': prompt}]
    )

    content_block = openai_response.choices[0].message.content

    return content_block

# Main execution
if __name__ == "__main__":
    driver = initialize_driver()
    open_webpage(driver, "https://www.google.com")
    inject_chatbox(driver)
    summary = get_page_summary(driver, api_key)  # Replace "YOUR_API_KEY_HERE" with your actual API key
    update_chatbox_prompt_1(driver, summary)
    # The browser will stay open until manually closed.
    # Wait for and get user input
    user_input = wait_for_user_input(driver)
    print(f"User input received: {user_input}")
    actionable_items = get_actionable_items(driver, api_key,user_input)
    print(actionable_items)
    print("Waiting for 1000 seconds. Close the browser manually if needed.")
    
    time.sleep(1000)  # Wait for 1000 seconds before ending the script
