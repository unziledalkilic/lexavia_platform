import logging
from transformers import T5Tokenizer, T5ForConditionalGeneration

logger = logging.getLogger(__name__)

class AIQuestionGenerator:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AIQuestionGenerator, cls).__new__(cls)
            cls._instance.model_name = "google/flan-t5-small"
            cls._instance.tokenizer = None
            cls._instance.model = None
            cls._instance.is_loaded = False
        return cls._instance

    def load_model(self):
        """Loads the model into memory. Call this on app startup."""
        if self.is_loaded:
            return

        logger.info(f"Loading AI Model: {self.model_name}...")
        try:
            self.tokenizer = T5Tokenizer.from_pretrained(self.model_name)
            self.model = T5ForConditionalGeneration.from_pretrained(self.model_name)
            self.is_loaded = True
            logger.info("AI Model loaded successfully.")
        except Exception as e:
            logger.error(f"Failed to load AI model: {e}")
            raise e

    def generate_question(self, word: str, context: str, level: str) -> dict:
        """
        Generates a quiz question for the word using the context.
        Returns: {
            "question_text": str,
            "options": list[str],
            "correct_answer": str,
            "explanation": str
        }
        """
        if not self.is_loaded:
            self.load_model()

        # Prompt Engineering for FLAN-T5
        # We ask it to generate a fill-in-the-blank sentence
        # Note: FLAN-T5 is good at following instructions.
        
        prompt = f"""
        Task: Create a fill-in-the-blank question for learning English.
        Target Word: {word}
        Level: {level}
        Context: {context}
        
        Instruction: Rewrite the context sentence by replacing '{word}' with blanks '_______'. Do not change other words.
        """
        
        try:
            input_ids = self.tokenizer(prompt, return_tensors="pt").input_ids
            outputs = self.model.generate(input_ids, max_length=100)
            question_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # Post-processing fallback
            if "_______" not in question_text:
                # If model failed to put blanks, manual fallback
                import re
                pattern = re.compile(re.escape(word), re.IGNORECASE)
                question_text = pattern.sub("_______", context)

            return {
                "question_text": question_text,
                "correct_answer": word,
                "explanation": f"Context: {context}"
            }

        except Exception as e:
            logger.error(f"Generation failed: {e}")
            # Fallback
            return {
                "question_text": f"Select the correct word for: ... {context.replace(word, '_______')} ...",
                "correct_answer": word,
                "explanation": "Review mode."
            }

ai_generator = AIQuestionGenerator()
