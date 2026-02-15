"""
Конфигурация приложения
"""

import os
from pathlib import Path
from typing import List, Dict
import yaml
from dotenv import load_dotenv

load_dotenv()

# Базовые пути
BASE_DIR = Path(__file__).parent
CONFIG_DIR = BASE_DIR / "config"
REPORTS_DIR = BASE_DIR / "reports"
LOGS_DIR = BASE_DIR / "logs"

# Создаем директории если их нет
REPORTS_DIR.mkdir(exist_ok=True)
(REPORTS_DIR / "json").mkdir(exist_ok=True)
(REPORTS_DIR / "html").mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)
CONFIG_DIR.mkdir(exist_ok=True)

# API настройки
PROXIAPI_API_KEY = os.getenv("PROXIAPI_API_KEY")
PROXIAPI_BASE_URL = os.getenv("PROXIAPI_BASE_URL", "https://api.proxiapi.com/v1")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o")

# Email уведомления (опционально)
SMTP_ENABLED = os.getenv("SMTP_ENABLED", "false").lower() == "true"
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
NOTIFY_EMAIL = os.getenv("NOTIFY_EMAIL", "")

# Настройки анализа
MAX_TEXT_LENGTH = int(os.getenv("MAX_TEXT_LENGTH", "12000"))
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "15"))


def load_sites_config() -> List[Dict[str, str]]:
    """
    Загружает список сайтов из YAML конфига
    
    Returns:
        Список словарей с настройками сайтов
    """
    config_path = CONFIG_DIR / "sites.yaml"
    
    if not config_path.exists():
        # Создаем пример конфига
        example_config = {
            'sites': [
                {
                    'url': 'https://example.com',
                    'name': 'Example Site',
                    'enabled': True
                }
            ]
        }
        
        with open(config_path, 'w', encoding='utf-8') as f:
            yaml.dump(example_config, f, allow_unicode=True, default_flow_style=False)
        
        return example_config['sites']
    
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
        return config.get('sites', [])


def get_enabled_sites() -> List[Dict[str, str]]:
    """Возвращает только активные сайты"""
    sites = load_sites_config()
    return [site for site in sites if site.get('enabled', True)]