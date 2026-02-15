"""
Планировщик для автоматического анализа сайтов
Используется через cron
"""

import sys
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List

from agent import run, UXReport
from config import (
    get_enabled_sites,
    REPORTS_DIR,
    LOGS_DIR,
    NOTIFY_EMAIL,
    SMTP_ENABLED
)


# Настройка логирования
log_file = LOGS_DIR / f"scheduler_{datetime.now().strftime('%Y%m%d')}.log"
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


def save_report_json(report: UXReport, site_name: str, url: str) -> Path:
    """
    Сохраняет отчет в JSON
    
    Args:
        report: UX отчет
        site_name: Название сайта
        url: URL сайта
        
    Returns:
        Path к сохраненному файлу
    """
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    safe_name = "".join(c for c in site_name if c.isalnum() or c in (' ', '_')).strip()
    safe_name = safe_name.replace(' ', '_')
    
    filename = f"{safe_name}_{timestamp}.json"
    filepath = REPORTS_DIR / "json" / filename
    
    data = {
        'site_name': site_name,
        'url': url,
        'analyzed_at': datetime.now().isoformat(),
        'report': {
            'pros': report.pros,
            'cons': report.cons,
            'recommendations': report.recommendations
        }
    }
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    logger.info(f"Otchet sokhranyon: {filepath}")
    return filepath


def save_report_html(report: UXReport, site_name: str, url: str) -> Path:
    """
    Сохраняет отчет в HTML
    
    Args:
        report: UX отчет
        site_name: Название сайта
        url: URL сайта
        
    Returns:
        Path к сохраненному файлу
    """
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    safe_name = "".join(c for c in site_name if c.isalnum() or c in (' ', '_')).strip()
    safe_name = safe_name.replace(' ', '_')
    
    filename = f"{safe_name}_{timestamp}.html"
    filepath = REPORTS_DIR / "html" / filename
    
    html = f"""<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>UX Otchet: {site_name}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            max-width: 900px;
            margin: 40px auto;
            padding: 0 20px;
            line-height: 1.6;
            color: #333;
        }}
        .header {{
            border-bottom: 3px solid #4CAF50;
            padding-bottom: 20px;
            margin-bottom: 30px;
        }}
        h1 {{
            color: #2c3e50;
            margin: 0;
        }}
        .meta {{
            color: #7f8c8d;
            font-size: 14px;
            margin-top: 10px;
        }}
        .section {{
            margin: 30px 0;
            padding: 20px;
            border-radius: 8px;
        }}
        .pros {{
            background: #e8f5e9;
            border-left: 4px solid #4CAF50;
        }}
        .cons {{
            background: #ffebee;
            border-left: 4px solid #f44336;
        }}
        .recommendations {{
            background: #e3f2fd;
            border-left: 4px solid #2196F3;
        }}
        h2 {{
            margin-top: 0;
            color: #2c3e50;
        }}
        ul {{
            padding-left: 20px;
        }}
        li {{
            margin: 10px 0;
        }}
        .footer {{
            margin-top: 50px;
            padding-top: 20px;
            border-top: 1px solid #ddd;
            text-align: center;
            color: #7f8c8d;
            font-size: 12px;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>UX Otchet</h1>
        <div class="meta">
            <strong>Sait:</strong> {site_name}<br>
            <strong>URL:</strong> <a href="{url}">{url}</a><br>
            <strong>Data analiza:</strong> {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}
        </div>
    </div>
    
    <div class="section pros">
        <h2>Dostoinstva</h2>
        <ul>
            {''.join(f'<li>{pro}</li>' for pro in report.pros)}
        </ul>
    </div>
    
    <div class="section cons">
        <h2>Slabye mesta</h2>
        <ul>
            {''.join(f'<li>{con}</li>' for con in report.cons)}
        </ul>
    </div>
    
    <div class="section recommendations">
        <h2>Rekomendatsii po uluchsheniyu</h2>
        <ul>
            {''.join(f'<li>{rec}</li>' for rec in report.recommendations)}
        </ul>
    </div>
    
    <div class="footer">
        Sgenerirováno avtomaticheski | UX-retsenzent v1.0
    </div>
</body>
</html>"""
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(html)
    
    logger.info(f"HTML otchet sokhranyon: {filepath}")
    return filepath


def send_email_notification(site_name: str, url: str, report_path: Path):
    """
    Отправляет email уведомление
    
    Args:
        site_name: Название сайта
        url: URL сайта
        report_path: Путь к отчету
    """
    if not SMTP_ENABLED or not NOTIFY_EMAIL:
        return
    
    try:
        import smtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart
        from config import SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD
        
        msg = MIMEMultipart()
        msg['From'] = SMTP_USER
        msg['To'] = NOTIFY_EMAIL
        msg['Subject'] = f"UX Otchet gotov: {site_name}"
        
        body = f"""
        Zavershen analiz saita: {site_name}
        URL: {url}
        
        Otchet sokhranyon: {report_path}
        
        ---
        UX-retsenzent
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.send_message(msg)
        
        logger.info(f"Email uvedomlenie otpravleno na {NOTIFY_EMAIL}")
        
    except Exception as e:
        logger.error(f"Oshibka otpravki email: {e}")


def analyze_site(site_config: Dict[str, str]) -> bool:
    """
    Анализирует один сайт
    
    Args:
        site_config: Конфигурация сайта
        
    Returns:
        True если успешно, False если ошибка
    """
    url = site_config['url']
    name = site_config.get('name', url)
    
    logger.info(f"Nachinaem analiz: {name} ({url})")
    
    try:
        # Запускаем анализ
        report = run(url)
        
        # Сохраняем отчеты
        json_path = save_report_json(report, name, url)
        html_path = save_report_html(report, name, url)
        
        # Отправляем уведомление
        send_email_notification(name, url, html_path)
        
        logger.info(f"Analiz zavershen: {name}")
        return True
        
    except Exception as e:
        logger.error(f"Oshibka analiza {name}: {e}")
        return False


def run_scheduled_analysis():
    """
    Запускает анализ всех активных сайтов
    Вызывается через cron
    """
    logger.info("="*60)
    logger.info("Zapusk planovogo analiza")
    logger.info("="*60)
    
    sites = get_enabled_sites()
    
    if not sites:
        logger.warning("Net aktivnykh saitov dlya analiza")
        return
    
    logger.info(f"Naydeno saitov dlya analiza: {len(sites)}")
    
    results = []
    for site in sites:
        success = analyze_site(site)
        results.append(success)
    
    # Итоговая статистика
    total = len(results)
    successful = sum(results)
    failed = total - successful
    
    logger.info("="*60)
    logger.info(f"Itogi: Vsego: {total} | Uspeshno: {successful} | Oshibki: {failed}")
    logger.info("="*60)


if __name__ == "__main__":
    try:
        run_scheduled_analysis()
    except KeyboardInterrupt:
        logger.info("\nPrervano polzovatelem")
        sys.exit(0)
    except Exception as e:
        logger.critical(f"Kriticheskaya oshibka: {e}", exc_info=True)
        sys.exit(1)