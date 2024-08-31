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
            story_prompt = f"""Write a 500-word narrative that can be easily adapted into a 6-panel manga-style comic. Use these details:

            Character Profile: {char_style_info}
            Situation: {situation_setup}

            Structure the story in 6 distinct scenes, each corresponding to a comic panel:

            1. Opening Scene: Introduce the character and setting visually. Include a thought or short dialogue that establishes the mood.
            2. Inciting Incident: Show the event that draws the character into the situation. Focus on their immediate reaction.
            3. Rising Action: Depict the character facing the main conflict or challenge. Include dialogue or internal monologue that reveals their struggle.
            4. Complication: Introduce a twist or additional obstacle. Show how this affects the character emotionally or physically.
            5. Climax: Present the peak of the conflict. This should be the most visually and emotionally intense scene.
            6. Resolution: Conclude with the character's final decision or the outcome of their actions. Include a visual or dialogue element that echoes the opening scene.

            Guidelines:
            - Use vivid, visual language that can be easily translated into comic panels.
            - Include short, impactful dialogue or thought bubbles for each scene.
            - Incorporate the character's unique traits and the author's writing style throughout.
            - Ensure each scene has a clear visual focus and emotional beat.

            Write in the style of {author}, paying attention to their narrative techniques and tonal qualities."""

            logger.debug(f"Story generation prompt: {story_prompt[:200]}...")

            response = self.anthropic.messages.create(
                model="claude-3-5-sonnet-20240620",
                max_tokens=2000,
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

    def generate_comic(self, story_summary):
        try:
            logger.info("Starting comic generation with OpenAI")

            max_summary_length = 100
            truncated_summary = story_summary[:max_summary_length] + ("..." if len(story_summary) > max_summary_length else "")
            
            prompt = f"""Create a 6-panel manga-style webcomic without any text, inspired by this story concept: {truncated_summary}

            Comic Specifications:
            1. Style: Black and white manga art style with clean lines and expressive characters.
            2. Layout: 6 distinct panels arranged in a 2x3 grid.
            3. Panel Content:
               Panel 1: Introduce the main character in their everyday environment.
               Panel 2: Show the character encountering a new situation or challenge.
               Panel 3: Depict the character's reaction or initial attempt to address the situation.
               Panel 4: Illustrate a moment of reflection or decision-making.
               Panel 5: Show the character taking action based on their decision.
               Panel 6: Conclude with the character in a new state or environment, changed by their experience.
            4. Character Design: Create a relatable protagonist with clear, exaggerated expressions to convey emotions without text.
            5. Backgrounds: Include simple but effective backgrounds that establish the setting.
            6. Visual Storytelling: Use varied angles, perspectives, and visual metaphors to convey the story without words.
            7. Emotion: Focus on character expressions and body language to convey emotions clearly.
            8. NO TEXT: Do not include any speech bubbles, captions, or written elements of any kind.

            Generate as a single image with 6 clearly defined panels. Ensure a logical visual flow across panels and absolutely no text or writing in the images."""

            logger.info(f"Sending prompt to OpenAI: {prompt}")
            response = self.openai.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size="1024x1024",
                quality="standard",
                n=1,
            )
            logger.info("Received response from OpenAI")

            image_url = response.data[0].url
            logger.info(f"Comic generated successfully. URL: {image_url}")
            return image_url
        except Exception as e:
            logger.error(f"Error in generate_comic: {str(e)}")
            logger.error(traceback.format_exc())
            raise

    def generate_dialogue(self, story_summary, comic_url):
        dialogue_prompt = f"""Based on the following story summary and a 6-panel comic image, generate appropriate dialogue or narrative text for each panel:

        Story Summary: {story_summary}

        Comic Image URL: {comic_url}

        For each of the 6 panels, provide:
        1. A brief description of what's visually happening in the panel (2-3 sentences)
        2. Any dialogue that would be appropriate for the characters in the scene (if applicable)
        3. Any narrative text that would enhance the story (if needed)

        Format your response as follows:

        Panel 1:
        Visual Description: [Description here]
        Dialogue/Narrative: [Text here]

        Panel 2:
        Visual Description: [Description here]
        Dialogue/Narrative: [Text here]

        ... (continue for all 6 panels)

        Ensure the dialogue and narrative text align with the story summary and what can be inferred from the comic panels. Keep the text concise and impactful, suitable for a comic format."""

        try:
            response = self.anthropic.messages.create(
                model="claude-3-5-sonnet-20240620",
                max_tokens=1000,
                messages=[
                    {"role": "user", "content": dialogue_prompt}
                ]
            )
            return response.content[0].text
        except Exception as e:
            logger.error(f"Error in generate_dialogue: {str(e)}")
            logger.error(traceback.format_exc())
            raise

    def generate_story_and_comic(self, char_style_info, situation_setup, author):
        try:
            logger.info("Starting story and comic generation")
            
            # Generate the story
            story = self.generate_story(char_style_info, situation_setup, author)
            story_summary = story  # The story is already a complete text
            
            # Generate the textless comic
            comic_url = self.generate_comic(story_summary)
            
            # Generate dialogue for the comic
            dialogue = self.generate_dialogue(story_summary, comic_url)
            
            return story_summary, comic_url, dialogue
        except Exception as e:
            logger.error(f"Error in generate_story_and_comic: {str(e)}")
            logger.error(traceback.format_exc())
            raise