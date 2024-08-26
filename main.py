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

        logger.info("Generating character style info")
        char_style_info = story_generator.generate_char_style_info(protagonist_name, original_story, author)
        logger.info(f"Character style info generated: {char_style_info[:100]}...")

        logger.info("Generating situation setup")
        situation_setup = story_generator.generate_situation_setup(circumstance, char_style_info)
        logger.info(f"Situation setup generated: {situation_setup[:100]}...")

        def generate():
            logger.info("Starting story generation")
            story_chunks = []
            for chunk in story_generator.generate_story(char_style_info, situation_setup, author):
                story_chunks.append(chunk)
                yield chunk

            # After story generation is complete, generate the comic
            full_story = "".join(story_chunks)
            logger.info("Story generation complete. Generating comic...")
            try:
                comic_url = story_generator.generate_comic(full_story)
                # URL encode the comic URL
                encoded_comic_url = urllib.parse.quote(comic_url)
                logger.info(f"Comic generated successfully. Encoded URL: {encoded_comic_url}")
            except Exception as e:
                logger.error(f"Error generating comic: {str(e)}")
                encoded_comic_url = ""
            
            # Yield the encoded comic URL as a special chunk
            yield f"\n\nCOMIC_URL:{encoded_comic_url}"

        return Response(stream_with_context(generate()), content_type='text/plain; charset=utf-8')

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