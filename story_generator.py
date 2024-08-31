import logging
from anthropic import Anthropic
from openai import OpenAI
import os
import traceback
import time

logger = logging.getLogger(__name__)

class StoryGenerator:
    FACE_REMINDER = ("CRITICAL: The protagonist's face must NEVER be shown under any circumstances. "
                     "Use creative techniques like showing the character from behind, using objects to obstruct the face, "
                     "cropping the image, or focusing on other body parts to convey emotions and actions.")

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

            {self.FACE_REMINDER}

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

            Important: When describing the character's appearance, do not include any details about their face. Focus on other physical attributes, clothing style, and body language.

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

            {self.FACE_REMINDER}

            Provide:
            1. Setting: Describe the specific location and time of day. What visual elements would be prominent?
            2. Inciting Incident: What exactly happens to bring the character into this circumstance?
            3. Character's Initial Reaction: How does the character physically and emotionally respond?
            4. Immediate Conflict: What obstacle or dilemma does the character face right away?
            5. Supporting Characters: Introduce 1-2 other characters who might be involved. How do they look and act?
            6. Potential for Drama: What elements of this scenario could lead to interesting visual storytelling?

            Important: When describing the character's actions and appearance, avoid mentioning their facial features or expressions. Instead, focus on body language, gestures, and other visual cues to convey emotions and reactions.

            Describe the scenario in about 150 words, focusing on vivid, visual details and emotionally charged moments that would translate well to a comic format without showing the protagonist's face."""

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

            {self.FACE_REMINDER}

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
            - Convey the protagonist's emotions through body language, actions, and surroundings rather than facial expressions.
            - Never describe the protagonist's facial features or expressions directly.

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

            {self.FACE_REMINDER}

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
            4. Character Design: Create a relatable protagonist without showing their face. Use body language, clothing, and surroundings to convey personality and emotions.
            5. Backgrounds: Include simple but effective backgrounds that establish the setting and help convey the protagonist's emotions.
            6. Visual Storytelling: Use varied angles, perspectives, and visual metaphors to convey the story without words or facial expressions.
            7. Emotion: Focus on the protagonist's body language, gestures, and interaction with the environment to convey emotions clearly.
            8. NO TEXT: Do not include any speech bubbles, captions, or written elements of any kind.
            9. Protagonist's Face: Never show the protagonist's face. Use creative angles, objects in the foreground, or show the character from behind to maintain this consistency.

            Generate as a single image with 6 clearly defined panels. Ensure a logical visual flow across panels, absolutely no text or writing in the images, and never reveal the protagonist's face."""

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
        1. A brief description of what's visually happening in the panel (2-3 sentences), focusing on the protagonist's body language and surroundings rather than facial expressions.
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

        Ensure the dialogue and narrative text align with the story summary and what can be inferred from the comic panels. Keep the text concise and impactful, suitable for a comic format. Remember that the protagonist's face is never shown, so focus on other ways to convey their emotions and reactions."""

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
            
            # Generate the panels sequentially
            panels = []
            for i in range(6):
                panel_prompt = self.create_panel_prompt(story, panels, i+1)
                panel_url = self.generate_panel(panel_prompt)
                panels.append({"url": panel_url, "prompt": panel_prompt})
            
            # Generate dialogue for the comic
            dialogue = self.generate_dialogue(story, panels)
            
            return panels, dialogue
        except Exception as e:
            logger.error(f"Error in generate_story_and_comic: {str(e)}")
            logger.error(traceback.format_exc())
            raise

    def create_panel_prompt(self, story, existing_panels, panel_number):
        context = f"Story so far: {story}\n\n"
        if existing_panels:
            context += "Previous panels:\n"
            for i, panel in enumerate(existing_panels):
                context += f"Panel {i+1}: {panel['prompt']}\n"
        
        prompt = f"""{context}

        {self.FACE_REMINDER}

        Create a prompt for panel {panel_number} of a 6-panel manga-style webcomic based on the story above. This panel should:

        1. Logically follow from the previous panels (if any) and advance the story.
        2. Focus on a key moment or action that's visually interesting.
        3. Convey character emotions through body language, gestures, and interaction with the environment.
        4. Include relevant background details that establish the setting and mood.
        5. Be described in a way that can be clearly visualized and drawn without showing the protagonist's face.

        Remember:
        - The image should be in black and white manga style with clean lines and expressive characters.
        - The protagonist's face must never be shown. Use creative angles, objects in the foreground, or show the character from behind.
        - Do not include any text, speech bubbles, or written elements in the description.
        - Focus on visual elements only, emphasizing body language and environmental cues to convey emotions.

        Describe the panel in about 2-3 sentences, focusing on what should be drawn while maintaining the 'faceless protagonist' constraint."""

        return self.anthropic.messages.create(
            model="claude-3-5-sonnet-20240620",
            max_tokens=150,
            messages=[
                {"role": "user", "content": prompt}
            ]
        ).content[0].text

    def generate_panel(self, panel_prompt):
        try:
            logger.info(f"Generating panel with prompt: {panel_prompt[:100]}...")
            response = self.openai.images.generate(
                model="dall-e-3",
                prompt=f"Create a black and white manga-style panel for a webcomic. {self.FACE_REMINDER} {panel_prompt} Do not include any text or speech bubbles. Explicitly ensure that the protagonist's face is not visible in any way - use creative angles, objects in the foreground, or show them from behind. Focus on body language and environmental cues to convey emotions.",
                size="1024x1024",
                quality="standard",
                n=1,
            )
            image_url = response.data[0].url
            logger.info(f"Panel generated successfully. URL: {image_url}")
            return image_url
        except Exception as e:
            logger.error(f"Error in generate_panel: {str(e)}")
            logger.error(traceback.format_exc())
            raise