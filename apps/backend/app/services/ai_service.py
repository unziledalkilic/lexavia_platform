"""
AI servisi - OpenAI/Anthropic ile içerik üretme.
"""
import json
import logging
from typing import Optional

from app.core.config import settings

logger = logging.getLogger(__name__)


class AIService:
    """AI ile kelime ve quiz soruları üretir."""
    
    def __init__(self):
        from app.core.config import settings
        self.openai_api_key: Optional[str] = settings.openai_api_key
        self.anthropic_api_key: Optional[str] = settings.anthropic_api_key
    
    async def generate_vocabulary_word(
        self,
        level: str,
        category: Optional[str] = None,
        target_language: str = "en",
        native_language: str = "tr"
    ) -> Optional[dict]:
        """
        AI ile yeni bir kelime kartı üretir.
        
        Args:
            level: Seviye (A1, A2, B1, vb.)
            category: Kategori (verb, noun, adjective, vb.)
            target_language: Hedef dil
            native_language: Ana dil
            
        Returns:
            {"word": "...", "translation": "...", "level": "...", "category": "...", "example_sentence": "..."}
        """
        if not self.openai_api_key and not self.anthropic_api_key:
            logger.warning("No AI API key configured")
            return None
        
        # Prompt oluştur
        prompt = f"""Generate a vocabulary word for language learning:
- Level: {level}
- Category: {category or "any"}
- Target language: {target_language}
- Native language: {native_language}

Return a JSON object with:
{{
  "word": "the word in {target_language}",
  "translation": "translation in {native_language}",
  "level": "{level}",
  "category": "verb|noun|adjective|adverb|preposition|conjunction",
  "example_sentence": "a simple example sentence using this word"
}}

Only return the JSON, no other text."""
        
        try:
            if self.openai_api_key:
                return await self._generate_with_openai(prompt)
            elif self.anthropic_api_key:
                return await self._generate_with_anthropic(prompt)
        except Exception as e:
            logger.error(f"Error generating vocabulary with AI: {e}", exc_info=True)
            return None
    
    async def generate_quiz_question(
        self,
        level: str,
        category: str = "grammar",
        target_language: str = "en"
    ) -> Optional[dict]:
        """
        AI ile quiz sorusu üretir.
        
        Args:
            level: Seviye (A1, A2, B1, vb.)
            category: Kategori (grammar, vocabulary, vb.)
            target_language: Hedef dil
            
        Returns:
            {{"question_text": "...", "correct_answer": "...", "options": [...], "explanation": "..."}}
        """
        if not self.openai_api_key and not self.anthropic_api_key:
            logger.warning("No AI API key configured")
            return None
        
        prompt = f"""Generate a {category} quiz question for {level} level in {target_language}:
- Question type: multiple_choice
- Level: {level}
- Category: {category}

Return a JSON object with:
{{
  "question_text": "a fill-in-the-blank question with _____",
  "correct_answer": "the correct answer",
  "options": ["option1", "option2", "option3", "option4"],
  "explanation": "brief explanation in Turkish"
}}

Only return the JSON, no other text."""
        
        try:
            if self.openai_api_key:
                return await self._generate_with_openai(prompt)
            elif self.anthropic_api_key:
                return await self._generate_with_anthropic(prompt)
        except Exception as e:
            logger.error(f"Error generating quiz with AI: {e}", exc_info=True)
            return None
    
    async def _generate_with_openai(self, prompt: str) -> Optional[dict]:
        """OpenAI API kullanarak içerik üretir."""
        try:
            import openai
            
            client = openai.AsyncOpenAI(api_key=self.openai_api_key)
            
            response = await client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a language learning content generator. Always return valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=500,
            )
            
            content = response.choices[0].message.content.strip()
            # JSON'u parse et
            if content.startswith("```json"):
                content = content[7:-3].strip()
            elif content.startswith("```"):
                content = content[3:-3].strip()
            
            return json.loads(content)
        except ImportError:
            logger.error("OpenAI library not installed. Run: pip install openai")
            return None
        except Exception as e:
            logger.error(f"OpenAI API error: {e}", exc_info=True)
            return None
    
    async def _generate_with_anthropic(self, prompt: str) -> Optional[dict]:
        """Anthropic API kullanarak içerik üretir."""
        try:
            import anthropic
            
            client = anthropic.AsyncAnthropic(api_key=self.anthropic_api_key)
            
            response = await client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=500,
                messages=[
                    {"role": "user", "content": prompt}
                ],
            )
            
            content = response.content[0].text.strip()
            # JSON'u parse et
            if content.startswith("```json"):
                content = content[7:-3].strip()
            elif content.startswith("```"):
                content = content[3:-3].strip()
            
            return json.loads(content)
        except ImportError:
            logger.error("Anthropic library not installed. Run: pip install anthropic")
            return None
        except Exception as e:
            logger.error(f"Anthropic API error: {e}", exc_info=True)
            return None

