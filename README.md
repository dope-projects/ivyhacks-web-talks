# ivyhacks-web-talks
Ivy Hacks Hackathon: Web extension to interact with websites

[IvyHacks](https://www.ivyhacks.ai/) - Columbia x Cornell x NYU AI Hackathon

By Mert Bozkir, Mishahal Palakuniyil, Madhav Bhatia

![Python Code](https://github.com/thebadcoder96/ivyhacks-web-talks/assets/58310848/8a6b7f5c-f05b-4a82-b805-0316eb5cafc0)

![Chrome Extention](https://github.com/thebadcoder96/ivyhacks-web-talks/blob/main/assets/videos/Video%20Demo%20Chrome%20Extention.mp4)


## Tech Stack
- Python
- Selenium
- OpenAI
- Anthropic
- Chrome Extension

## How to use
### Python Code
1. Clone the repository
2. Install the required packages using `pip install -r requirements.txt`    
3. Create a `.env` file in the root directory and add your OpenAI API key and Anthropic API key
4. Run the Python code using `python webtalk_demo_openai.py`

### Chrome Extension
1. Clone the repository
2. Go to `chrome://extensions` in your Chrome browser
3. Enable Developer mode by clicking the toggle switch next to "Developer mode"
4. Click "Load unpacked" and select the `webtalk` directory in the repository
5. The options page automatically opens where you need to enter your Anthropic API key
6. Open a webpage and click the "Web Talks!" icon in the browser toolbar or extension popup
