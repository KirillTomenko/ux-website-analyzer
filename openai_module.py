"""
Модуль для работы OpenAI API через Proxiapi
"""

import os
from typing import Optional
from openai import OpenAI
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type
)
import json


class OpenAIClient:
    """Клиент для работы с OpenAI через Proxiapi"""
    
    def __init__(
        self, 
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: str = "gpt-4o"
    ):
        """
        Инициализация клиента
        
        Args:
            api_key: API ключ Proxiapi (если None, берется из .env)
            base_url: Base URL Proxiapi (если None, берется из .env)
            model: Модель для использования (по умолчанию gpt-4o)
        """
        self.api_key = api_key or os.getenv("PROXIAPI_API_KEY")
        self.base_url = base_url or os.getenv("PROXIAPI_BASE_URL", "https://api.proxiapi.com/v1")
        self.model = model or os.getenv("OPENAI_MODEL", "gpt-4o")
        
        if not self.api_key:
            raise ValueError(
                "PROXIAPI_API_KEY не найден. "
                "Создайте файл .env и добавьте ключ."
            )
        
        # Инициализация OpenAI клиента с Proxiapi
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((Exception,))
    )
    def generate_response(
        self, 
        system_prompt: str, 
        user_content: str,
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> str:
        """
        Генерация ответа от модели с retry логикой
        
        Args:
            system_prompt: Системный промпт (роль)
            user_content: Контент от пользователя
            temperature: Температура генерации (0-2)
            max_tokens: Максимальное количество токенов
            
        Returns:
            Ответ модели в виде строки
            
        Raises:
            Exception: При ошибках API после всех попыток
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_content}
                ],
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"⚠️  Ошибка API (повтор...): {str(e)}")
            raise
    
    def generate_json_response(
        self,
        system_prompt: str,
        user_content: str,
        temperature: float = 0.7
    ) -> dict:
        """
        Генерация JSON ответа от модели
        
        Args:
            system_prompt: Системный промпт
            user_content: Контент от пользователя
            temperature: Температура генерации
            
        Returns:
            Распарсенный JSON ответ
        """
        response_text = self.generate_response(
            system_prompt,
            user_content,
            temperature=temperature
        )
        
        # Попытка извлечь JSON из ответа
        try:
            # Удаляем markdown блоки если есть
            response_text = response_text.strip()
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.startswith("```"):
                response_text = response_text[3:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
            
            return json.loads(response_text.strip())
        except json.JSONDecodeError as e:
            raise ValueError(f"Не удалось распарсить JSON: {e}\nОтвет: {response_text}")