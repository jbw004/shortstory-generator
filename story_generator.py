import logging
from anthropic import Anthropic
import os
import traceback
import time

logger = logging.getLogger(__name__)

class StoryGenerator:
    def __init__(self):
        logger.info("Initializing StoryGenerator")
        self.anthropic = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
        if not os.environ.get("ANTHROPIC_API_KEY"):
            logger.error("ANTHROPIC_API_KEY not found in environment variables")

    def generate_char_style_info(self, protagonist_name, original_story, author):
        try:
            logger.info(f"Generating character style info for {protagonist_name}")
            char_style_prompt = f"""Provide two separate pieces of information:

            1. Describe the core personality traits, general outlook, and typical reactions of a young adult (20s-30s) living in a modern Western city who embodies the essence of {protagonist_name} from {original_story}. Focus on universal human qualities, avoiding any superhuman abilities or specific plot references. Consider:
               - Their general attitude towards life and others
               - How they typically handle stress or challenges
               - Their communication style and social tendencies
               - Any notable quirks or habits that define their character

            2. Summarize the key elements of {author}'s writing style in {original_story}, focusing on:
               - Narrative voice and perspective
               - Pacing and rhythm of storytelling
               - Use of dialogue and internal monologue
               - Descriptive techniques and atmosphere creation
               - Any unique literary devices or tones characteristic of the author

            Ensure all descriptions are applicable to a realistic, modern-day setting."""


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
            situation_prompt = f"""Create a detailed scenario where a young adult (20s-30s) with the following traits directly faces this circumstance in a modern Western metropolitan city: {circumstance}

            Character traits: {char_style_info}

            Consider:
            1. How does this circumstance intersect with the character's daily life or routine?
            2. What specific aspects of the situation would challenge or engage someone with these personality traits?
            3. What internal conflict or dilemma might this create for the character?
            4. How might their background or worldview influence their initial reaction?

            Describe the scenario in about 100 words, focusing on the immediate situation and the character's initial thoughts or reactions. Avoid mentioning any specific names or references to the original story."""

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
            story_prompt = f"""Write a 500-word first-person narrative set in a modern Western city, featuring a young adult (20s-30s) with these traits:

            {char_style_info}

            They find themselves in this situation:
            {situation_setup}

            Guidelines:
            1. Begin the story in media res, immersing the reader in the character's thoughts or actions.
            2. Use internal monologue to reveal the character's unique perspective and decision-making process.
            3. Incorporate subtle references to the character's background or past experiences that shape their reactions, without explicitly mentioning their original story.
            4. Focus on the character's emotional journey and growth through the situation.
            5. Conclude with a resolution or pivotal decision that reflects the character's core traits.

            Write in the style of {author}, paying attention to their narrative techniques and tonal qualities. Aim for approximately 500 words."""

            logger.debug(f"Story generation prompt: {story_prompt[:200]}...")

            start_time = time.time()
            try:
                logger.info("Sending request to Anthropic API")
                response = self.anthropic.messages.create(
                    model="claude-3-5-sonnet-20240620",
                    max_tokens=2000,
                    temperature=0.7,
                    stream=True,
                    messages=[
                        {"role": "user", "content": story_prompt}
                    ]
                )
                logger.info("Request sent successfully")

                for event in response:
                    if event.type == "content_block_start":
                        continue
                    elif event.type == "content_block_delta":
                        yield event.delta.text
                    elif event.type == "message_delta":
                        if event.delta.stop_reason:
                            logger.info(f"Story generation stopped: {event.delta.stop_reason}")
                    elif event.type == "message_stop":
                        logger.info("Story generation complete")

            except Exception as e:
                logger.error(f"Error sending request to Anthropic API: {str(e)}")
                yield f"Error sending request to API: {str(e)}"
                return

            end_time = time.time()
            logger.info(f"Story generation complete. Time taken: {end_time - start_time:.2f} seconds")

        except Exception as e:
            logger.error(f"Unexpected error in generate_story: {str(e)}")
            logger.error(traceback.format_exc())
            yield f"An unexpected error occurred during story generation: {str(e)}"