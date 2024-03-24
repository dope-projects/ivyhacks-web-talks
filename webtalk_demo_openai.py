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
    


def extract_actionable_content(html):
    soup = BeautifulSoup(html, 'html.parser')
    
    # Initialize an empty list to store summaries of actionable elements
    actionable_items = []

    # Look for form elements, highlighting their purpose in simple terms
    forms = soup.find_all('form')
    for form in forms:
        form_summary = "There is a form here for providing information or making requests."
        actionable_items.append(form_summary)

    # Identify and describe buttons in clear, actionable language
    buttons = soup.find_all('button')
    for button in buttons:
        button_text = button.text.strip() or "unnamed"
        button_summary = f"There's a '{button_text}' button that you can press for more actions."
        actionable_items.append(button_summary)

    # Simplify link descriptions, focusing on what the user can expect to find or do
    links = soup.find_all('a', href=True)
    for link in links:
        link_text = link.text.strip()
        if link_text:  # Only consider links with descriptive text
            link_summary = f"There's a link here titled '{link_text}'. Clicking it will take you to another page for more information or actions."
            actionable_items.append(link_summary)

    # Prioritize and present content in an accessible manner
    if not actionable_items:
        return "We couldn't find any specific actions to take on this page. You might want to look around or ask for help if you're looking for something specific."
    
    return "Here's what you can do on this page: " + "; ".join(actionable_items) + ". If anything is unclear, you may want to ask someone for help or try clicking on items that interest you."

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


def execute_actionable_js(driver, action_output):
    """
    Executes JavaScript actions extracted from the action output safely,
    including dynamic checks for the existence of elements referenced in the actions.
    """
    # Directly insert action_output into the f-string
    safety_wrapper = f"""
    function safelyExecute() {{
        try {{
            {action_output}
        }} catch (error) {{
            console.error('Execution Error:', error.toString());
        }}
    }}
    
    safelyExecute();
    """
    
    # Execute the safely wrapped JavaScript code
    try:
        driver.execute_script(safety_wrapper)
    except Exception as e:
        print(f"Error executing JavaScript: {e}")





def get_actionable_items(driver, api_key, user_input):
    """Generate a summary of the webpage with OpenAI's API and return actionable JavaScript for elderly users."""
    html = driver.page_source
    soup = extract_actionable_content(html)
    client = OpenAI(api_key=api_key)
    
    prompt = f"""
    Assist an elderly person with limited tech experience to fulfill their intention using the webpage content. 
    Simplify their task with JavaScript automation and enhance visibility of key elements.

    User's need: {user_input}
    Simplified Webpage content: {soup}

    Generate JavaScript that:
    1. Automates the action directly related to the user's need.
    2. Highlights important webpage elements for easier visibility.

    Format your response as actionable JavaScript snippets.
    
    """

    openai_response = client.chat.completions.create(
        model='gpt-3.5-turbo',
        messages=[{'role': 'user', 'content': prompt}]
    )

    return openai_response.choices[0].message.content


# Main execution
if __name__ == "__main__":
    driver = initialize_driver()
    url = "https://www.google.com"  # Example URL
    open_webpage(driver, url)
    inject_chatbox(driver)
    
    while True:
        summary = get_page_summary(driver, api_key)
        update_chatbox_prompt_1(driver, summary)
        # Get user input from the chatbox
        user_input = wait_for_user_input(driver)
        print(f"User input received: {user_input}")

        if user_input.lower() == "exit":  # Define a way for the user to exit the loop
            print("Exiting...")
            break

        # Generate actionable items based on the current page content and user input
        actionable_items = get_actionable_items(driver, api_key, user_input)
        print(actionable_items)

        # Execute any JavaScript provided by the actionable items
        execute_actionable_js(driver, actionable_items)
        time.sleep(5)
    print("Session ended. You can close the browser manually.")
