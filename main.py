import urllib.parse
from dotenv import load_dotenv
import os
from pathlib import Path

# Get the directory of the current script
script_dir = Path(__file__).resolve().parent

# Construct the path to the jawn.env file
env_path = script_dir / 'jawn.env'

# Load environment variables from .env file
load_dotenv(dotenv_path=env_path)

from flask import Flask, render_template, request, jsonify, Response, stream_with_context
import logging
import sys
from story_generator import StoryGenerator
from protagonists import protagonists
import traceback

# Set up logging
logging.basicConfig(level=logging.DEBUG, 
                    format='%(asctime)s %(levelname)s: %(message)s',
                    handlers=[logging.StreamHandler(sys.stdout)])
logger = logging.getLogger(__name__)

logger.info("Starting application initialization")

# Check for ANTHROPIC_API_KEY
if not os.environ.get("ANTHROPIC_API_KEY"):
    logger.error("ANTHROPIC_API_KEY is not set in environment variables")
    raise ValueError("ANTHROPIC_API_KEY is not set")

try:
    # Initialize StoryGenerator
    logger.info("Attempting to initialize StoryGenerator")
    story_generator = StoryGenerator()
    logger.info("StoryGenerator initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize StoryGenerator: {str(e)}")
    logger.error(traceback.format_exc())
    raise

# Initialize Flask app
logger.info("Initializing Flask app")
app = Flask(__name__)
logger.info("Flask app initialized")

@app.route('/')
def index():
    logger.info("Index route accessed")
    return render_template('index.html', protagonists=protagonists)

@app.route('/generate', methods=['POST'])
def generate_story():
    try:
        logger.info("Generate story route called")
        circumstance = request.form['circumstance']
        protagonist_name = request.form['protagonist']
        logger.info(f"Generating story for {protagonist_name} in circumstance: {circumstance}")

        protagonist_info = next((p for p in protagonists if p['Protagonist'] == protagonist_name), None)
        if not protagonist_info:
            logger.error(f"Protagonist not found: {protagonist_name}")
            return jsonify({"error": "Protagonist not found"}), 400

        original_story = protagonist_info['Original Story']
        author = protagonist_info['Author']

        char_style_info = story_generator.generate_char_style_info(protagonist_name, original_story, author)
        situation_setup = story_generator.generate_situation_setup(circumstance, char_style_info)
        
        comic_url, story, visual_summary = story_generator.generate_story_and_comic(char_style_info, situation_setup, author)
        
        return jsonify({
            "comic_url": comic_url,
            "story": story,
            "visual_summary": visual_summary
        })

    except Exception as e:
        logger.error(f"An error occurred in generate_story route: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    try:
        logger.info("Starting Flask application")
        app.run(host='0.0.0.0', port=8080, debug=True)
    except Exception as e:
        logger.error(f"Failed to start Flask application: {str(e)}")
        logger.error(traceback.format_exc())
        sys.exit(1)

logger.info("End of main.py file reached")