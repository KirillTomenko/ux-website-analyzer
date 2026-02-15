"""
UX-рецензент сайта
Анализирует веб-страницу и генерирует UX-отчёт
"""

import sys
import os
from dataclasses import dataclass
from typing import List, Optional
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

from openai_module import OpenAIClient


# Системный промпт для UX-анализа
SYSTEM_PROMPT = """Ты опытный UX-эксперт с 10+ годами опыта в веб-дизайне и юзабилити.

Проанализируй текст веб-страницы и составь профессиональный UX-отчёт.

ВАЖНО: Ответь СТРОГО в формате JSON без дополнительного текста:

{
  "pros": ["достоинство 1", "достоинство 2", "достоинство 3"],
  "cons": ["проблема 1", "проблема 2", "проблема 3"],
  "recommendations": [
    "конкретная рекомендация 1",
    "конкретная рекомендация 2",
    "конкретная рекомендация 3",
    "конкретная рекомендация 4",
    "конкретная рекомендация 5"
  ]
}

Требования:
- pros: 2-3 главных достоинства UX
- cons: 2-3 основных проблемы
- recommendations: ровно 5 конкретных, реализуемых предложений по улучшению

Фокусируйся на:
- Навигации и информационной архитектуре
- Читабельности и структуре контента
- Призывах к действию (CTA)
- Доступности и понятности
- Пользовательском пути"""


@dataclass
class UXReport:
    """Структура UX-отчёта"""
    pros: List[str]
    cons: List[str]
    recommendations: List[str]
    
    def __str__(self) -> str:
        """Форматированный вывод отчёта"""
        output = "\n" + "="*60 + "\n"
        output += "UX OTCHYOT\n"
        output += "="*60 + "\n\n"
        
        output += "DOSTOINSTVA:\n"
        for i, pro in enumerate(self.pros, 1):
            output += f"  {i}. {pro}\n"
        
        output += "\nSLABYE MESTA:\n"
        for i, con in enumerate(self.cons, 1):
            output += f"  {i}. {con}\n"
        
        output += "\nREKOMENDATSII PO ULUCHSHENIYU:\n"
        for i, rec in enumerate(self.recommendations, 1):
            output += f"  {i}. {rec}\n"
        
        output += "\n" + "="*60 + "\n"
        return output


def fetch_html(url: str, timeout: int = 15) -> str:
    """
    Загружает HTML страницы
    
    Args:
        url: URL страницы
        timeout: Таймаут запроса в секундах
        
    Returns:
        HTML контент страницы
        
    Raises:
        ValueError: При проблемах с загрузкой
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        print(f"Zagruzka stranitsy: {url}")
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()
        
        print(f"Stranitsa zagruzhena ({len(response.content)} bait)")
        return response.text
        
    except requests.exceptions.Timeout:
        raise ValueError(f"Taimaut pri zagruzke stranitsy: {url}")
    except requests.exceptions.RequestException as e:
        raise ValueError(f"Oshibka zagruzki stranitsy: {e}")


def extract_text(html: str, max_length: int = 12000) -> str:
    """
    Извлекает текст из HTML
    
    Args:
        html: HTML контент
        max_length: Максимальная длина текста
        
    Returns:
        Очищенный текст
        
    Raises:
        ValueError: Если текст слишком короткий
    """
    print("Izvlechenie teksta...")
    
    soup = BeautifulSoup(html, 'html.parser')
    
    # Удаляем ненужные теги
    for tag in soup(['script', 'style', 'meta', 'link', 'noscript', 'svg']):
        tag.decompose()
    
    # Извлекаем текст
    text = soup.get_text(separator=' ', strip=True)
    
    # Очистка
    lines = [line.strip() for line in text.split('\n')]
    text = ' '.join(line for line in lines if line)
    
    # Сокращаем если нужно
    if len(text) > max_length:
        text = text[:max_length] + "..."
        print(f"Tekst sokrashchyon do {max_length} simvolov")
    
    if len(text) < 100:
        raise ValueError("Slishkom malo teksta na stranitse dlya analiza")
    
    print(f"Izvlecheno {len(text)} simvolov teksta")
    return text


def analyze_ux(text: str, openai_client: OpenAIClient) -> UXReport:
    """
    Анализирует UX на основе текста страницы
    
    Args:
        text: Текст страницы
        openai_client: Клиент OpenAI
        
    Returns:
        UXReport с результатами анализа
        
    Raises:
        ValueError: При проблемах с парсингом ответа
    """
    print("Analiz UX cherez AI...")
    
    try:
        # Получаем JSON ответ
        result = openai_client.generate_json_response(
            system_prompt=SYSTEM_PROMPT,
            user_content=f"Proanaliziruyi UX etoi veb-stranitsy:\n\n{text}",
            temperature=0.7
        )
        
        # Валидация структуры
        if not all(key in result for key in ['pros', 'cons', 'recommendations']):
            raise ValueError("Nevernaya struktura otveta ot modeli")
        
        if len(result['recommendations']) != 5:
            print(f"Polucheno {len(result['recommendations'])} rekomendatsiy vmesto 5")
        
        print("Analiz zavershen")
        
        return UXReport(
            pros=result['pros'],
            cons=result['cons'],
            recommendations=result['recommendations']
        )
        
    except Exception as e:
        raise ValueError(f"Oshibka pri analize UX: {e}")


def run(url: str) -> UXReport:
    """
    Основная функция агента
    
    Args:
        url: URL страницы для анализа
        
    Returns:
        UXReport с результатами анализа
        
    Raises:
        ValueError: При проблемах с URL, загрузкой или анализом
        Exception: При критических ошибках
    """
    # Загружаем переменные окружения
    load_dotenv()
    
    # Валидация URL
    if not url.startswith(('http://', 'https://')):
        raise ValueError("URL dolzhen nachinat'sya s http:// ili https://")
    
    # 1. Загрузка HTML
    html = fetch_html(url)
    
    # 2. Извлечение текста
    text = extract_text(html)
    
    # 3. Инициализация OpenAI клиента
    try:
        openai_client = OpenAIClient()
    except ValueError as e:
        raise ValueError(f"Problema s nastroykoy API: {e}")
    
    # 4. Анализ UX
    report = analyze_ux(text, openai_client)
    
    return report


def main():
    """Точка входа CLI"""
    print("\nUX-RETSENZENT SAITA\n")
    
    # Проверка аргументов
    if len(sys.argv) < 2:
        print("OSHIBKA: ne ukazan URL")
        print("\nIspol'zovanie:")
        print("  python agent.py <URL>\n")
        print("Primer:")
        print("  python agent.py https://example.com\n")
        sys.exit(1)
    
    url = sys.argv[1]
    
    try:
        # Запуск анализа
        report = run(url)
        
        # Вывод результата
        print(report)
        
    except ValueError as e:
        print(f"\nOSHIBKA: {e}\n")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\nPrervano pol'zovatelem\n")
        sys.exit(0)
    except Exception as e:
        print(f"\nKRITICHESKAYA OSHIBKA: {e}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()