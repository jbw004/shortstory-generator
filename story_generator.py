import logging
from anthropic import Anthropic
from openai import OpenAI
import os
import traceback
import time

logger = logging.getLogger(__name__)

class StoryGenerator:

    def __init__(self):
        logger.info("Initializing StoryGenerator")
        self.anthropic = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
        self.openai = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        if not os.environ.get("ANTHROPIC_API_KEY"):
            logger.error("ANTHROPIC_API_KEY not found in environment variables")
        if not os.environ.get("OPENAI_API_KEY"):
            logger.error("OPENAI_API_KEY not found in environment variables")

    def generate_char_style_info(self, protagonist_name, original_story, author):
        try:
            logger.info(f"Generating character style info for {protagonist_name}")
            char_style_prompt = f"""Provide a detailed character profile and writing style analysis for a modern adaptation of {protagonist_name} from {original_story} by {author}:

            1. Character Profile:
               a) Core personality traits (list 3-5 key traits)
               b) Typical emotional responses to stress or challenges
               c) Communication style and social tendencies
               d) Notable quirks or habits
               e) Key values or beliefs that drive their actions
               f) A typical day in their life in a modern Western city

            2. Writing Style Analysis:
               a) Narrative perspective (e.g., first-person, third-person limited)
               b) Tone and mood (e.g., introspective, humorous, melancholic)
               c) Pacing and rhythm of storytelling
               d) Use of dialogue (e.g., sparse and meaningful, witty banter)
               e) Descriptive techniques for settings and characters
               f) Literary devices frequently employed (e.g., metaphors, flashbacks)
               g) Sentence structure and vocabulary level

            Ensure all descriptions are applicable to a realistic, modern-day setting and provide specific examples where possible."""

            logger.debug(f"Character style prompt: {char_style_prompt[:200]}...")
            char_style_response = self.anthropic.messages.create(
                model="claude-3-5-sonnet-20240620",
                max_tokens=400,
                messages=[
                    {"role": "user", "content": char_style_prompt}
                ]
            )
            logger.info(f"Character style info generated: {char_style_response.content[0].text[:100]}...")
            return char_style_response.content[0].text
        except Exception as e:
            logger.error(f"Error in generate_char_style_info: {str(e)}")
            logger.error(traceback.format_exc())
            raise

    def generate_situation_setup(self, circumstance, char_style_info):
        try:
            logger.info(f"Generating situation setup for circumstance: {circumstance[:50]}...")
            situation_prompt = f"""Create a vivid and detailed scenario for a 6-panel manga-style comic where a young adult with the following traits faces this circumstance in a modern Western city: {circumstance}

            Character traits: {char_style_info}

            Provide:
            1. Setting: Describe the specific location and time of day. What visual elements would be prominent?
            2. Inciting Incident: What exactly happens to bring the character into this circumstance?
            3. Character's Initial Reaction: How does the character physically and emotionally respond?
            4. Immediate Conflict: What obstacle or dilemma does the character face right away?
            5. Supporting Characters: Introduce 1-2 other characters who might be involved. How do they look and act?
            6. Potential for Drama: What elements of this scenario could lead to interesting visual storytelling?

            Important: When describing the character's actions and appearance, avoid mentioning their facial features or expressions. Instead, focus on body language, gestures, and other visual cues to convey emotions and reactions.

            Describe the scenario in about 150 words, focusing on vivid, visual details and emotionally charged moments that would translate well to a comic format."""

            logger.debug(f"Situation setup prompt: {situation_prompt[:200]}...")
            situation_response = self.anthropic.messages.create(
                model="claude-3-5-sonnet-20240620",
                max_tokens=300,
                messages=[
                    {"role": "user", "content": situation_prompt}
                ]
            )
            logger.info(f"Situation setup generated: {situation_response.content[0].text[:100]}...")
            return situation_response.content[0].text
        except Exception as e:
            logger.error(f"Error in generate_situation_setup: {str(e)}")
            logger.error(traceback.format_exc())
            raise

    def generate_story(self, char_style_info, situation_setup, author):
        try:
            logger.info("Starting story generation")
            story_prompt = f"""Write a high-quality short story of approximately 500 words based on the following details:

            Character Profile: {char_style_info}
            Situation: {situation_setup}

            Guidelines:
            1. Write the story in a "cinematic first-person" viewpoint, using "I" as the narrator (the protagonist).
            2. Describe scenes vividly through the protagonist's eyes, focusing on sensory details.
            3. Use present tense to create a sense of immediacy.
            4. Emulate the distinctive voice and style of {author}, adapting it to this first-person perspective.
            5. Create a compelling narrative arc with a clear beginning, middle, and end.
            6. Incorporate dialogue that reflects the character's voice and advances the plot.
            7. Explore the protagonist's inner thoughts and emotions as they navigate the situation.
            8. Include a subtle theme or message that resonates with the character's journey.
            9. Conclude with a satisfying resolution true to the author's style.

            After writing the story, provide a brief summary of key visual elements in the following format:

            VISUAL SUMMARY:
            - Setting: [Describe the main setting or settings]
            - Protagonist: [Describe the protagonist's appearance and most notable visual characteristics]
            - Key Object: [Describe an important object or symbol in the story]
            - Action: [Describe a key action or scene that encapsulates the story's climax or theme]
            - Mood: [Describe the overall visual mood or atmosphere of the story]

            Ensure this visual summary captures the most striking and important visual aspects of your story."""

            logger.debug(f"Story generation prompt: {story_prompt[:200]}...")

            response = self.anthropic.messages.create(
                model="claude-3-5-sonnet-20240620",
                max_tokens=2500,
                temperature=0.7,
                messages=[
                    {"role": "user", "content": story_prompt}
                ]
            )
            logger.info("Story generated successfully")
            return response.content[0].text

        except Exception as e:
            logger.error(f"Unexpected error in generate_story: {str(e)}")
            logger.error(traceback.format_exc())
            raise

    def generate_story_and_comic(self, char_style_info, situation_setup, author):
        try:
            logger.info("Starting story and comic generation")
            
            # Generate the story with visual summary
            full_story = self.generate_story(char_style_info, situation_setup, author)
            
            # Split the story and visual summary
            story_parts = full_story.split("VISUAL SUMMARY:")
            story = story_parts[0].strip()
            visual_summary = "VISUAL SUMMARY:" + story_parts[1].strip() if len(story_parts) > 1 else ""
            
            # Generate the single comic image
            comic_url = self.generate_comic(full_story)
            
            return comic_url, story, visual_summary
        except Exception as e:
            logger.error(f"Error in generate_story_and_comic: {str(e)}")
            logger.error(traceback.format_exc())
            raise

    def generate_comic(self, story):
        try:
            logger.info("Starting comic generation with OpenAI")

            # Extract the visual summary from the story
            visual_summary_start = story.find("VISUAL SUMMARY:")
            visual_summary = story[visual_summary_start:].strip() if visual_summary_start != -1 else ""

            prompt = f"""Create a single, detailed manga-style webcomic image in the style of Tsutomu Nihei, inspired by this story concept and visual summary:

            {visual_summary}

            Image Specifications:
            1. Style: Black and white manga art style inspired by Tsutomu Nihei's work, known for:
               - Intricate, highly detailed architectural and mechanical designs
               - Vast, often dystopian or post-apocalyptic settings
               - Stark contrast between black and white elements
               - Complex, biomechanical aesthetics
            2. Composition: A single, full-page image that captures the essence of the story
            3. Character Design: Create a protagonist based on the description, fitting Nihei's style:
               - Intricate, often utilitarian or biomechanical outfits
               - Stoic or intense expressions
               - Integration with the surrounding environment
            4. Setting: Develop a detailed, immersive background that reflects the story's setting:
               - Vast, labyrinthine structures or cityscapes
               - Blend of organic and mechanical elements
               - Use of perspective to create a sense of scale and depth
            5. Visual Storytelling: 
               - Incorporate the key object and action described in the visual summary
               - Use visual metaphors or symbolic elements to convey the story's essence
               - Create a sense of action or tension through character positioning and environmental details
            6. Lighting and Texture:
               - Employ strong contrasts between light and shadow
               - Use intricate textures and patterns to add depth and detail
               - Create a mood that reflects the story's described atmosphere
            7. NO TEXT: Do not include any speech bubbles, captions, or written elements of any kind.

            Generate as a single, highly detailed image that captures the essence of the story in Tsutomu Nihei's distinctive style, while accurately representing the specific elements described in the visual summary."""

            logger.info(f"Sending prompt to OpenAI: {prompt[:200]}...")
            response = self.openai.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size="1024x1024",
                quality="hd",
                n=1,
            )
            logger.info("Received response from OpenAI")

            image_url = response.data[0].url
            logger.info(f"Comic image generated successfully. URL: {image_url}")
            return image_url
        except Exception as e:
            logger.error(f"Error in generate_comic: {str(e)}")
            logger.error(traceback.format_exc())
            raise