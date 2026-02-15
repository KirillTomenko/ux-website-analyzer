"""
Веб-интерфейс для UX-рецензента
Запуск: streamlit run app.py
"""

import streamlit as st
from agent import run
import json
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import os
from dotenv import load_dotenv

load_dotenv()

# Настройка страницы
st.set_page_config(
    page_title="UX-рецензент",
    page_icon="🎨",
    layout="wide"
)

# Функция отправки email
def send_email_report(recipient_email: str, url: str, report, json_data: str, text_data: str) -> tuple[bool, str]:
    """
    Отправляет отчет на email
    
    Returns:
        (success, message)
    """
    # Проверка настроек SMTP
    smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_user = os.getenv("SMTP_USER", "")
    smtp_password = os.getenv("SMTP_PASSWORD", "")
    
    if not smtp_user or not smtp_password:
        return False, "⚠️ SMTP не настроен. Добавьте SMTP_USER и SMTP_PASSWORD в .env файл"
    
    try:
        # Создаём письмо
        msg = MIMEMultipart()
        msg['From'] = smtp_user
        msg['To'] = recipient_email
        msg['Subject'] = f"UX Отчёт для {url}"
        
        # Тело письма
        body = f"""
Здравствуйте!

Готов UX-отчёт для сайта: {url}
Дата анализа: {datetime.now().strftime('%d.%m.%Y %H:%M')}

ДОСТОИНСТВА:
{chr(10).join(f'{i}. {pro}' for i, pro in enumerate(report.pros, 1))}

СЛАБЫЕ МЕСТА:
{chr(10).join(f'{i}. {con}' for i, con in enumerate(report.cons, 1))}

РЕКОМЕНДАЦИИ ПО УЛУЧШЕНИЮ:
{chr(10).join(f'{i}. {rec}' for i, rec in enumerate(report.recommendations, 1))}

---
Во вложении полные отчёты в форматах JSON и TXT.

С уважением,
UX-рецензент
"""
        
        msg.attach(MIMEText(body, 'plain', 'utf-8'))
        
        # Прикрепляем JSON
        json_attachment = MIMEApplication(json_data.encode('utf-8'), _subtype="json")
        json_attachment.add_header('Content-Disposition', 'attachment', 
                                  filename=f'ux_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json')
        msg.attach(json_attachment)
        
        # Прикрепляем TXT
        txt_attachment = MIMEApplication(text_data.encode('utf-8'), _subtype="plain")
        txt_attachment.add_header('Content-Disposition', 'attachment', 
                                 filename=f'ux_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt')
        msg.attach(txt_attachment)
        
        # Отправляем
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.send_message(msg)
        
        return True, f"✅ Отчёт успешно отправлен на {recipient_email}"
        
    except Exception as e:
        return False, f"❌ Ошибка отправки: {str(e)}"


# Заголовок
st.title("🎨 UX-рецензент сайта")
st.markdown("Автоматический анализ UX с помощью искусственного интеллекта")

# Боковая панель с информацией
with st.sidebar:
    st.header("ℹ️ Информация")
    st.markdown("""
    **UX-рецензент** анализирует сайт и выдаёт:
    - ✅ Достоинства
    - ❌ Слабые места  
    - 💡 5 рекомендаций
    
    **Как использовать:**
    1. Введите URL сайта
    2. Нажмите "Анализировать"
    3. Дождитесь результата
    4. Скачайте или отправьте отчёт
    
    **Примеры сайтов:**
    - https://example.com
    - https://habr.com
    - https://stripe.com
    """)
    
    st.markdown("---")
    
    # Настройки email
    with st.expander("📧 Настройки Email"):
        st.markdown("""
        Для отправки отчётов на почту настройте в `.env`:
```
        SMTP_HOST=smtp.gmail.com
        SMTP_PORT=587
        SMTP_USER=your@gmail.com
        SMTP_PASSWORD=your_app_password
```
        
        **Для Gmail:**
        1. Включите 2FA
        2. Создайте App Password
        3. Используйте его в SMTP_PASSWORD
        """)
        
        smtp_status = "🟢 Настроен" if os.getenv("SMTP_USER") and os.getenv("SMTP_PASSWORD") else "🔴 Не настроен"
        st.markdown(f"**Статус:** {smtp_status}")
    
    st.markdown("---")
    st.markdown("*Работает на OpenAI через ProxyAPI*")

# Основная форма
url = st.text_input(
    "🔗 Введите URL сайта для анализа:",
    placeholder="https://example.com",
    help="Введите полный URL с http:// или https://"
)

col1, col2, col3 = st.columns([1, 1, 2])
with col1:
    analyze_button = st.button("🚀 Анализировать", type="primary", use_container_width=True)
with col2:
    clear_button = st.button("🗑️ Очистить", use_container_width=True)

if clear_button:
    st.rerun()

# Анализ
if analyze_button:
    if not url:
        st.error("❌ Пожалуйста, введите URL сайта!")
    elif not url.startswith(('http://', 'https://')):
        st.error("❌ URL должен начинаться с http:// или https://")
    else:
        with st.spinner(f"🔍 Анализирую {url}..."):
            try:
                # Запуск анализа
                report = run(url)
                
                # Сохраняем результат в session_state
                st.session_state.report = report
                st.session_state.url = url
                
                # Успешный результат
                st.success("✅ Анализ завершён!")
                
            except ValueError as e:
                st.error(f"❌ Ошибка: {e}")
                st.session_state.report = None
            except Exception as e:
                st.error(f"❌ Критическая ошибка: {e}")
                st.exception(e)
                st.session_state.report = None

# Отображение результатов (если есть)
if 'report' in st.session_state and st.session_state.report:
    report = st.session_state.report
    url = st.session_state.url
    
    # Вывод результатов в красивых блоках
    st.markdown("---")
    
    # Достоинства
    st.markdown("### ✅ Достоинства")
    with st.container():
        for i, pro in enumerate(report.pros, 1):
            st.markdown(f"**{i}.** {pro}")
    
    st.markdown("")
    
    # Слабые места
    st.markdown("### ❌ Слабые места")
    with st.container():
        for i, con in enumerate(report.cons, 1):
            st.markdown(f"**{i}.** {con}")
    
    st.markdown("")
    
    # Рекомендации
    st.markdown("### 💡 Рекомендации по улучшению")
    with st.container():
        for i, rec in enumerate(report.recommendations, 1):
            st.markdown(f"**{i}.** {rec}")
    
    # Подготовка данных для экспорта
    json_data = json.dumps({
        'url': url,
        'analyzed_at': datetime.now().isoformat(),
        'pros': report.pros,
        'cons': report.cons,
        'recommendations': report.recommendations
    }, ensure_ascii=False, indent=2)
    
    text_report = f"""UX ОТЧЁТ
URL: {url}
Дата: {datetime.now().strftime('%d.%m.%Y %H:%M')}

ДОСТОИНСТВА:
{chr(10).join(f'{i}. {pro}' for i, pro in enumerate(report.pros, 1))}

СЛАБЫЕ МЕСТА:
{chr(10).join(f'{i}. {con}' for i, con in enumerate(report.cons, 1))}

РЕКОМЕНДАЦИИ:
{chr(10).join(f'{i}. {rec}' for i, rec in enumerate(report.recommendations, 1))}
"""
    
    # Кнопки действий
    st.markdown("---")
    st.markdown("### 📤 Экспорт отчёта")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # JSON экспорт
        st.download_button(
            label="📥 Скачать JSON",
            data=json_data,
            file_name=f"ux_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json",
            use_container_width=True
        )
    
    with col2:
        # Текстовый экспорт
        st.download_button(
            label="📄 Скачать TXT",
            data=text_report,
            file_name=f"ux_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            mime="text/plain",
            use_container_width=True
        )
    
    # Email форма
    st.markdown("---")
    st.markdown("### 📧 Отправить на Email")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        recipient_email = st.text_input(
            "Email получателя:",
            placeholder="example@gmail.com",
            help="Введите email адрес для отправки отчёта"
        )
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)  # Выравнивание
        send_email_button = st.button("📧 Отправить", use_container_width=True, type="secondary")
    
    if send_email_button:
        if not recipient_email:
            st.error("❌ Введите email адрес!")
        elif '@' not in recipient_email or '.' not in recipient_email:
            st.error("❌ Некорректный email адрес!")
        else:
            with st.spinner(f"📤 Отправляю отчёт на {recipient_email}..."):
                success, message = send_email_report(
                    recipient_email, 
                    url, 
                    report, 
                    json_data, 
                    text_report
                )
                
                if success:
                    st.success(message)
                else:
                    st.error(message)

# Футер
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: gray;'>UX-рецензент v1.0 | Powered by OpenAI</div>",
    unsafe_allow_html=True
)