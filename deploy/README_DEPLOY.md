# 📦 Деплой UX-рецензента на reg.ru

Подробная инструкция по развертыванию на сервере reg.ru.

## 🎯 Предварительные требования

- ✅ SSH доступ к серверу reg.ru
- ✅ Python 3.10+ установлен на сервере
- ✅ Права sudo (или root доступ)
- ✅ API ключ ProxyAPI

## 🚀 Быстрый деплой (5 шагов)

### Шаг 1: Подключение к серверу
```bash
# Замените на ваши данные
ssh username@your-server.reg.ru
```

### Шаг 2: Загрузка проекта

#### Вариант A: Через SCP (с вашего компьютера)
```bash
# На локальной машине Windows (PowerShell)
scp -r C:\Users\SNHIM\ux_reviewer username@your-server.reg.ru:/tmp/

# На сервере
ssh username@your-server.reg.ru
cd /tmp
sudo mv ux_reviewer /var/www/
cd /var/www/ux_reviewer
```

#### Вариант B: Через Git (если есть репозиторий)
```bash
# На сервере
cd /var/www
sudo git clone https://your-repo/ux_reviewer.git
cd ux_reviewer
```

#### Вариант C: Через архив
```bash
# На локальной машине
tar -czf ux_reviewer.tar.gz ux_reviewer/
scp ux_reviewer.tar.gz username@your-server.reg.ru:/tmp/

# На сервере
ssh username@your-server.reg.ru
cd /tmp
tar -xzf ux_reviewer.tar.gz
sudo mv ux_reviewer /var/www/
cd /var/www/ux_reviewer
```

### Шаг 3: Запуск деплоя
```bash
cd /var/www/ux_reviewer
bash deploy/deploy.sh
```

Скрипт автоматически:
- ✅ Создаст виртуальное окружение
- ✅ Установит зависимости
- ✅ Создаст необходимые директории
- ✅ Проверит работоспособность

### Шаг 4: Настройка .env
```bash
nano /var/www/ux_reviewer/.env
```

Добавьте:
```env
PROXIAPI_API_KEY=ваш_ключ_proxiapi
PROXIAPI_BASE_URL=https://api.proxyapi.ru/openai/v1
OPENAI_MODEL=gpt-4o

# Опционально: Email уведомления
SMTP_HOST=smtp.yandex.ru
SMTP_PORT=587
SMTP_USER=your@yandex.ru
SMTP_PASSWORD=пароль_приложения
```

**Сохраните:** `Ctrl+X` → `Y` → `Enter`

### Шаг 5: Настройка автоматического запуска
```bash
cd /var/www/ux_reviewer
bash deploy/setup_cron.sh
```

Выберите частоту запуска (рекомендуется: вариант 1 - ежедневно в 2:00).

---

## ✅ Проверка работы

### Ручной запуск для проверки
```bash
cd /var/www/ux_reviewer
source venv/bin/activate
python scheduler.py
```

### Проверка cron
```bash
# Просмотр задач
crontab -l

# Просмотр логов
tail -f /var/www/ux_reviewer/logs/cron.log
```

### Проверка отчетов
```bash
ls -la /var/www/ux_reviewer/reports/json/
ls -la /var/www/ux_reviewer/reports/html/
```

---

## 🌐 Настройка веб-доступа к отчётам

### Вариант 1: Nginx (рекомендуется)

#### Установка Nginx
```bash
sudo apt update
sudo apt install nginx
```

#### Создание конфигурации
```bash
sudo nano /etc/nginx/sites-available/ux-reports
```

Вставьте:
```nginx
server {
    listen 80;
    server_name reports.your-domain.com;  # Замените на ваш домен
    
    root /var/www/ux_reviewer/reports/html;
    index index.html;
    
    # Базовая аутентификация
    auth_basic "UX Reports";
    auth_basic_user_file /etc/nginx/.htpasswd;
    
    location / {
        autoindex on;
        autoindex_exact_size off;
        autoindex_localtime on;
    }
    
    # Безопасность
    location ~ /\. {
        deny all;
    }
}
```

#### Создание пароля
```bash
sudo apt install apache2-utils
sudo htpasswd -c /etc/nginx/.htpasswd admin
# Введите пароль
```

#### Активация
```bash
sudo ln -s /etc/nginx/sites-available/ux-reports /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

Теперь отчёты доступны по адресу: `http://reports.your-domain.com`

### Вариант 2: Apache
```bash
sudo apt install apache2

sudo nano /etc/apache2/sites-available/ux-reports.conf
```
```apache
<VirtualHost *:80>
    ServerName reports.your-domain.com
    DocumentRoot /var/www/ux_reviewer/reports/html
    
    <Directory /var/www/ux_reviewer/reports/html>
        Options +Indexes
        AllowOverride All
        Require all granted
        
        AuthType Basic
        AuthName "UX Reports"
        AuthUserFile /etc/apache2/.htpasswd
        Require valid-user
    </Directory>
</VirtualHost>
```
```bash
sudo htpasswd -c /etc/apache2/.htpasswd admin
sudo a2ensite ux-reports
sudo systemctl reload apache2
```

### Вариант 3: Python SimpleHTTPServer (для тестирования)
```bash
cd /var/www/ux_reviewer/reports/html
python3 -m http.server 8080
```

Доступ: `http://your-server.reg.ru:8080`

---

## 🔒 Безопасность

### Защита .env файла
```bash
chmod 600 /var/www/ux_reviewer/.env
```

### Ограничение доступа к директориям
```bash
chmod 750 /var/www/ux_reviewer
chmod 750 /var/www/ux_reviewer/reports
chmod 750 /var/www/ux_reviewer/logs
```

### Настройка firewall (если нужно)
```bash
# Открыть только SSH и HTTP
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw enable
```

---

## 📊 Мониторинг

### Просмотр логов
```bash
# Логи scheduler
tail -f /var/www/ux_reviewer/logs/scheduler_*.log

# Логи cron
tail -f /var/www/ux_reviewer/logs/cron.log

# Системные логи cron
grep CRON /var/log/syslog
```

### Размер отчётов и логов
```bash
du -sh /var/www/ux_reviewer/reports/
du -sh /var/www/ux_reviewer/logs/
```

### Очистка старых файлов
```bash
# Удалить отчёты старше 30 дней
find /var/www/ux_reviewer/reports/ -name "*.html" -mtime +30 -delete
find /var/www/ux_reviewer/reports/ -name "*.json" -mtime +30 -delete

# Удалить логи старше 30 дней
find /var/www/ux_reviewer/logs/ -name "*.log" -mtime +30 -delete
```

### Автоматическая очистка (добавить в cron)
```bash
crontab -e
```

Добавить:
```
# Очистка старых отчётов (каждую неделю)
0 3 * * 0 find /var/www/ux_reviewer/reports/ -mtime +30 -delete
```

---

## 🔄 Обновление проекта

### Через Git
```bash
cd /var/www/ux_reviewer
git pull origin main
source venv/bin/activate
pip install -r requirements.txt --upgrade
```

### Вручную
```bash
# На локальной машине
scp agent.py username@your-server.reg.ru:/var/www/ux_reviewer/

# На сервере
cd /var/www/ux_reviewer
source venv/bin/activate
# Перезапустите cron если нужно
```

---

## 🐛 Решение проблем

### Python не найден
```bash
# Проверка версии
python3 --version

# Установка Python 3.10+
sudo apt update
sudo apt install python3.10 python3.10-venv python3-pip
```

### Ошибки прав доступа
```bash
sudo chown -R $USER:$USER /var/www/ux_reviewer
chmod +x /var/www/ux_reviewer/deploy/*.sh
```

### Cron не запускается
```bash
# Проверка службы cron
sudo systemctl status cron

# Перезапуск
sudo systemctl restart cron

# Проверка логов
grep CRON /var/log/syslog | tail -20
```

### API ошибки
```bash
# Проверка .env
cat /var/www/ux_reviewer/.env

# Тест OpenAI клиента
cd /var/www/ux_reviewer
source venv/bin/activate
python -c "from openai_module import OpenAIClient; client = OpenAIClient(); print('OK')"
```

### Недостаточно места на диске
```bash
# Проверка места
df -h

# Очистка старых отчётов
find /var/www/ux_reviewer/reports/ -mtime +7 -delete
```

---

## 📧 Настройка email уведомлений

### Для Yandex
```env
SMTP_HOST=smtp.yandex.ru
SMTP_PORT=587
SMTP_USER=your@yandex.ru
SMTP_PASSWORD=пароль_приложения
```

Получить пароль: https://id.yandex.ru/security/app-passwords

### Для Gmail
```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your@gmail.com
SMTP_PASSWORD=app_password
```

Получить App Password: https://myaccount.google.com/apppasswords

---

## 📈 Оптимизация производительности

### Увеличение лимита файлов
```bash
# Добавить в /etc/security/limits.conf
* soft nofile 65536
* hard nofile 65536
```

### Настройка logrotate
```bash
sudo nano /etc/logrotate.d/ux-reviewer
```
```
/var/www/ux_reviewer/logs/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 username username
}
```

---

## 🎯 Типичные сценарии использования

### Ежедневный мониторинг конкурентов
```yaml
# config/sites.yaml
sites:
  - url: https://competitor1.com
    name: Competitor 1
    enabled: true
  - url: https://competitor2.com
    name: Competitor 2
    enabled: true
```

Cron: каждый день в 9:00

### Еженедельная проверка своего сайта
```yaml
sites:
  - url: https://mysite.com
    name: My Site
    enabled: true
```

Cron: каждый понедельник в 8:00

### Мониторинг после деплоя

Запуск вручную после каждого обновления сайта:
```bash
cd /var/www/ux_reviewer
source venv/bin/activate
python agent.py https://mysite.com
```

---

## 📞 Поддержка reg.ru

- **Документация:** https://www.reg.ru/support/hosting-i-servery
- **Техподдержка:** https://www.reg.ru/support/
- **Панель управления:** https://www.reg.ru/user/

---

## ✅ Чеклист успешного деплоя

- [ ] Проект загружен на сервер
- [ ] Скрипт deploy.sh выполнен
- [ ] .env файл настроен с API ключом
- [ ] config/sites.yaml заполнен
- [ ] Ручной запуск scheduler.py успешен
- [ ] Cron настроен и работает
- [ ] Отчёты генерируются
- [ ] Логи пишутся
- [ ] (Опционально) Веб-доступ к отчётам настроен
- [ ] (Опционально) Email уведомления работают

---

🎉 **Поздравляем! UX-рецензент успешно развёрнут на сервере!**
```

**Сохраните:** `Ctrl + S`

---

## ✅ ИТОГО: ВСЕ ФАЙЛЫ СОЗДАНЫ!

Теперь у вас есть:
```
deploy/
├── deploy.sh            ✅ Скрипт автоматического деплоя
├── setup_cron.sh        ✅ Настройка cron
└── README_DEPLOY.md     ✅ Подробная инструкция