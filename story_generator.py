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
        self.openai_client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        if not os.environ.get("ANTHROPIC_API_KEY"):
            logger.error("ANTHROPIC_API_KEY not found in environment variables")
        if not os.environ.get("OPENAI_API_KEY"):
            logger.error("OPENAI_API_KEY not found in environment variables")

    def generate_char_style_info(self, protagonist_name, original_story, author):
        try:
            logger.info(f"Generating character style info for {protagonist_name}")
            char_style_prompt = f"""Create a detailed character profile for a modern adaptation of {protagonist_name}, originally from {original_story} by {author}. Focus on the core essence of the character without directly referencing their original story, specific plot elements, or other characters from that story. Adapt their traits to a contemporary, relatable context:

            1. Character Essence:
               a) Core personality traits (list 3-5 key traits)
               b) Fundamental motivations and values
               c) Typical responses to challenges or setbacks
               d) Communication style and social tendencies
               e) Notable quirks or habits
               f) Basic physical characteristics (age range, build, general appearance)

            2. Inner Strength and Growth:
               a) Sources of the character's inner strength
               b) Areas where the character might struggle or feel unsure
               c) How the character typically handles being underestimated by others
               d) The character's unique approach to overcoming obstacles
               e) Past experiences that have shaped the character's resilience

            3. Modern Context:
               a) Potential contemporary profession or lifestyle
               b) How their core traits might manifest in today's world
               c) Types of modern-day challenges they might face
               d) Their relationship with technology and social media

            4. First-Person Narration Voice:
               a) Distinctive speech patterns or expressions (without using catchphrases from the original story)
               b) Level of self-awareness as a narrator
               c) Tendency towards introspection or external observation
               d) Use of humor, sarcasm, or other stylistic elements
               e) How their background and experiences influence their narration style
               f) Examples of how they might describe feelings of uncertainty or determination

            5. Writing Style Guidance:
               a) Tone and mood that best suits the character (e.g., introspective, humorous, determined)
               b) Pacing and rhythm of storytelling that matches the character's personality
               c) Balance of dialogue, action, and internal monologue
               d) Descriptive techniques that align with the character's perspective
               e) Literary devices that would effectively convey the character's journey of personal growth

            Ensure all descriptions are applicable to a realistic, modern-day setting and provide specific examples where possible. Focus on creating a unique and consistent character voice that captures the essence of {protagonist_name} without relying on specific elements from their original story, emphasizing their journey of personal growth and resilience."""

            logger.debug(f"Character style prompt: {char_style_prompt[:200]}...")
            char_style_response = self.anthropic.messages.create(
                model="claude-3-5-sonnet-20240620",
                max_tokens=1000,
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

            Character Profile and Style: {char_style_info}
            Situation: {situation_setup}

            Guidelines:
            1. Write the story in a "cinematic first-person" viewpoint, using "I" as the narrator (the protagonist).
            2. Use present tense to create a sense of immediacy.
            3. Incorporate the specific first-person narration voice and writing style details provided in the character profile.
            4. Create a compelling narrative arc focused on the protagonist's personal growth within the context of the given situation.
            5. Establish the main conflict as an internal or external challenge that tests the protagonist's beliefs or capabilities.
            6. Subtly showcase the protagonist's unique strengths and how they apply them to face the challenge.
            7. Illustrate the character's internal struggle and growth through their actions, thoughts, and interactions.
            8. Incorporate dialogue that reflects the character's unique voice and subtly reveals how others perceive them.
            9. Explore the protagonist's inner thoughts and emotions as they navigate the challenges, without explicitly labeling their feelings.
            10. Conclude with a satisfying resolution where the protagonist overcomes the challenge in a way that aligns with their core personality traits.
            11. Ensure the story feels contemporary and relatable, avoiding any direct references to the character's original story or universe.
            12. Focus on vivid descriptions of the setting and the protagonist's emotional state, as this will be used for image generation.

            After writing the story, provide a brief summary of key visual elements in the following format:

            VISUAL SUMMARY:
            - Setting: [Describe the main setting or settings]
            - Protagonist: [Describe the protagonist's appearance and most notable visual characteristics]
            - Key Object: [Describe an important object or symbol in the story that represents the character's struggle or growth]
            - Action: [Describe a key action or scene that encapsulates the protagonist's moment of triumph or realization]
            - Mood: [Describe the overall visual mood or atmosphere of the story, reflecting the character's emotional journey]

            Ensure this visual summary captures the most striking and important visual aspects of your story, emphasizing the character's emotional journey without explicitly mentioning concepts like doubt or confidence."""

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

    def generate_derivative_story(self, original_story, visual_summary, char_style_info):
        try:
            logger.info("Starting generation of 1-minute read-aloud snippet")
            snippet_prompt = f"""Create a captivating 1-minute read-aloud snippet based on the following story and visual summary. This snippet should hook listeners scrolling through social media, compelling them to stop and listen to the entire piece.

            Original Story:
            {original_story}

            Visual Summary:
            {visual_summary}

            Character Profile and Style:
            {char_style_info}

            Guidelines for the 1-minute read-aloud snippet:
            1. Start with a powerful, attention-grabbing sentence that introduces the protagonist's dilemma or the story's central conflict.
            2. Use vivid, sensory language to quickly immerse the listener in the scene.
            3. Maintain a cinematic first-person perspective, incorporating the character's unique voice.
            4. Focus on a pivotal moment or decision that encapsulates the protagonist's journey.
            5. Use short, punchy sentences interspersed with occasional longer ones for rhythm.
            6. Incorporate one or two lines of impactful dialogue if relevant.
            7. End with a compelling cliffhanger or thought-provoking statement that leaves the listener wanting more.
            8. Aim for approximately 150-175 words to fit a ~1-minute read-aloud format.
            9. Ensure the snippet feels complete enough to be satisfying, yet open-ended enough to intrigue.
            10. Subtly showcase the protagonist's growth or internal struggle without explicitly stating it.
            11. Use active voice and strong verbs to maintain a sense of immediacy and urgency.
            12. Avoid any direct references to the character's original story or universe.

            Create a gripping, fast-paced snippet that captures the essence of the story and character, designed to be irresistible when heard as a voice-over on social media."""

            logger.debug(f"1-minute snippet generation prompt: {snippet_prompt[:200]}...")

            response = self.anthropic.messages.create(
                model="claude-3-5-sonnet-20240620",
                max_tokens=1000,
                temperature=0.7,
                messages=[
                    {"role": "user", "content": snippet_prompt}
                ]
            )
            logger.info("1-minute read-aloud snippet generated successfully")
            return response.content[0].text

        except Exception as e:
            logger.error(f"Unexpected error in generate_derivative_story: {str(e)}")
            logger.error(traceback.format_exc())
            raise

    def generate_image_with_dalle(self, prompt):
        try:
            logger.info(f"Generating image with DALL-E. Prompt: {prompt[:100]}...")
            response = self.openai_client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size="1024x1024",
                quality="standard",
                n=1,
            )
            image_url = response.data[0].url
            logger.info(f"Image generated successfully. URL: {image_url}")
            return image_url
        except Exception as e:
            logger.error(f"Error in generate_image_with_dalle: {str(e)}")
            logger.error(traceback.format_exc())
            raise

    def extract_key_traits(self, char_style_info):
        # Extract and summarize key traits from the character info
        # This is a simplified example; you may need to adjust based on your char_style_info structure
        traits = []
        if "Core personality traits" in char_style_info:
            traits.extend(char_style_info.split("Core personality traits:")[1].split("\n")[1:4])
        if "Basic physical characteristics" in char_style_info:
            traits.append(char_style_info.split("Basic physical characteristics:")[1].split("\n")[1])
        
        # Filter out potentially problematic words
        safe_traits = [trait for trait in traits if not any(word in trait.lower() for word in ["violent", "aggressive", "weapon", "blood", "gore", "explicit"])]
        
        return ", ".join(trait.strip() for trait in safe_traits if trait.strip())

    def generate_character_images(self, char_style_info):
        try:
            logger.info("Starting character image generation with DALL-E")

            # Extract key information from char_style_info
            key_traits = self.extract_key_traits(char_style_info)

            # Base prompt template
            base_prompt = """Create a tasteful, family-friendly manga-style image inspired by the art of Tsutomu Nihei. The image should be black and white, featuring a character with the following traits: {traits}

            Image Specifications:
            1. Black and white manga art style
            2. Intricate details in clothing and background
            3. Strong use of light and shadow
            4. Minimal abstract background
            5. Suitable for all audiences

            The character should appear contemplative and determined, avoiding any aggressive or controversial poses or expressions."""

            side_profile_prompt = base_prompt.format(traits=key_traits) + """
            Additional details:
            - Detailed side view of the character's face and upper body
            - Character looking thoughtfully to the side

            Generate a single, highly detailed side profile image in a respectful and artistic style."""

            headshot_prompt = base_prompt.format(traits=key_traits) + """
            Additional details:
            - Close-up, front-facing view of the character's face and upper shoulders
            - Character with a calm, focused expression

            Generate a single, highly detailed headshot image in a respectful and artistic style."""

            side_profile_url = self.generate_image_with_dalle(side_profile_prompt)
            headshot_url = self.generate_image_with_dalle(headshot_prompt)

            logger.info("Character images generated successfully with DALL-E")
            return side_profile_url, headshot_url

        except Exception as e:
            logger.error(f"Error in generate_character_images: {str(e)}")
            logger.error(traceback.format_exc())
            raise

    def generate_story_and_images(self, char_style_info, situation_setup, author):
        try:
            logger.info("Starting story and image generation")
            
            # Generate the original story with visual summary
            full_story = self.generate_story(char_style_info, situation_setup, author)
            
            # Split the story and visual summary
            story_parts = full_story.split("VISUAL SUMMARY:")
            original_story = story_parts[0].strip()
            visual_summary = "VISUAL SUMMARY:" + story_parts[1].strip() if len(story_parts) > 1 else ""
            
            # Generate the derivative story
            derivative_story = self.generate_derivative_story(original_story, visual_summary, char_style_info)
            
            # Generate the comic image
            comic_url = self.generate_comic(full_story)
            
            # Generate character images
            side_profile_url, headshot_url = self.generate_character_images(char_style_info)
            
            return comic_url, derivative_story, visual_summary, side_profile_url, headshot_url
        except Exception as e:
            logger.error(f"Error in generate_story_and_images: {str(e)}")
            logger.error(traceback.format_exc())
            raise

    def generate_comic(self, story):
        try:
            logger.info("Starting comic generation with DALL-E")

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

            Generate a single, highly detailed image that captures the essence of the story in Tsutomu Nihei's distinctive style, while accurately representing the specific elements described in the visual summary."""

            comic_url = self.generate_image_with_dalle(prompt)
            logger.info("Comic image generated successfully with DALL-E")
            return comic_url

        except Exception as e:
            logger.error(f"Error in generate_comic: {str(e)}")
            logger.error(traceback.format_exc())
            raise