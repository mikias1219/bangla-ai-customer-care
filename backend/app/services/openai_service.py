import openai
from typing import List, Dict, Any, Optional
import json
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)


class OpenAIService:
    def __init__(self):
        self.api_key = settings.openai_api_key
        self.model = settings.openai_model
        self.max_tokens = settings.openai_max_tokens

        if self.api_key:
            openai.api_key = self.api_key
        else:
            logger.warning("OpenAI API key not configured")

    async def generate_response(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        functions: Optional[List[Dict[str, Any]]] = None
    ) -> str:
        """Generate a response using OpenAI's Chat Completion API"""
        if not self.api_key:
            raise ValueError("OpenAI API key not configured")

        try:
            params = {
                "model": self.model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens or self.max_tokens,
            }

            if functions:
                params["functions"] = functions
                params["function_call"] = "auto"

            response = await openai.ChatCompletion.acreate(**params)

            if functions and response.choices[0].message.get("function_call"):
                return json.dumps({
                    "function_call": response.choices[0].message.function_call,
                    "content": response.choices[0].message.content
                })

            return response.choices[0].message.content.strip()

        except Exception as e:
            logger.error(f"OpenAI API error: {str(e)}")
            raise

    async def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment of text using OpenAI"""
        messages = [
            {"role": "system", "content": "You are a sentiment analysis expert. Analyze the sentiment of the given text and return a JSON response with 'sentiment' (positive/negative/neutral) and 'confidence' (0-1)."},
            {"role": "user", "content": f"Analyze the sentiment of this text: {text}"}
        ]

        try:
            response = await self.generate_response(messages, temperature=0.1)
            # Try to parse as JSON, fallback if not
            try:
                return json.loads(response)
            except:
                return {"sentiment": "neutral", "confidence": 0.5}
        except Exception as e:
            logger.error(f"Sentiment analysis failed: {str(e)}")
            return {"sentiment": "neutral", "confidence": 0.5}

    async def extract_entities(self, text: str, entity_types: List[str]) -> Dict[str, Any]:
        """Extract specific entities from text using OpenAI"""
        entity_list = ", ".join(entity_types)
        messages = [
            {"role": "system", "content": f"You are an entity extraction expert. Extract the following entity types from the text: {entity_list}. Return a JSON object with entity types as keys and extracted values as arrays."},
            {"role": "user", "content": f"Extract entities from: {text}"}
        ]

        try:
            response = await self.generate_response(messages, temperature=0.1)
            try:
                return json.loads(response)
            except:
                return {}
        except Exception as e:
            logger.error(f"Entity extraction failed: {str(e)}")
            return {}

    async def translate_text(self, text: str, target_language: str, source_language: str = "auto") -> str:
        """Translate text using OpenAI"""
        messages = [
            {"role": "system", "content": f"You are a professional translator. Translate the given text to {target_language}. If the source language is not specified, detect it automatically."},
            {"role": "user", "content": f"Translate this text to {target_language}: {text}"}
        ]

        try:
            response = await self.generate_response(messages, temperature=0.1)
            return response
        except Exception as e:
            logger.error(f"Translation failed: {str(e)}")
            return text  # Return original text if translation fails

    async def summarize_conversation(self, messages: List[Dict[str, str]], max_length: int = 200) -> str:
        """Summarize a conversation using OpenAI"""
        conversation_text = "\n".join([f"{msg['role']}: {msg['content']}" for msg in messages])

        messages = [
            {"role": "system", "content": f"You are a conversation summarizer. Provide a concise summary of the conversation in {max_length} characters or less."},
            {"role": "user", "content": f"Summarize this conversation:\n{conversation_text}"}
        ]

        try:
            response = await self.generate_response(messages, temperature=0.3, max_tokens=100)
            return response[:max_length]
        except Exception as e:
            logger.error(f"Conversation summarization failed: {str(e)}")
            return "Conversation summary unavailable"

    async def classify_intent(self, text: str, intents: List[str]) -> Dict[str, Any]:
        """Classify intent from a list of possible intents"""
        intent_list = ", ".join(intents)
        messages = [
            {"role": "system", "content": f"You are an intent classification expert. Classify the user's intent from these options: {intent_list}. Return a JSON with 'intent' and 'confidence' (0-1)."},
            {"role": "user", "content": f"Classify this message: {text}"}
        ]

        try:
            response = await self.generate_response(messages, temperature=0.1)
            try:
                return json.loads(response)
            except:
                # Fallback: pick first intent
                return {"intent": intents[0] if intents else "unknown", "confidence": 0.5}
        except Exception as e:
            logger.error(f"Intent classification failed: {str(e)}")
            return {"intent": "unknown", "confidence": 0.0}


# Global instance
openai_service = OpenAIService()
