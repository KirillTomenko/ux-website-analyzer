#!/bin/bash

# Скрипт деплоя UX-рецензента на reg.ru сервер
# Использование: bash deploy.sh

set -e  # Остановка при ошибке

echo "=================================="
echo "Деплой UX-рецензента"
echo "=================================="

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Конфигурация
PROJECT_NAME="ux_reviewer"
DEPLOY_DIR="/var/www/$PROJECT_NAME"
PYTHON_VERSION="python3"

# Проверка Python
echo -e "${YELLOW}Проверка Python...${NC}"
if ! command -v $PYTHON_VERSION &> /dev/null; then
    echo -e "${RED}Ошибка: Python не найден${NC}"
    echo "Установите Python 3.10 или выше"
    exit 1
fi
echo -e "${GREEN}✓ Python найден: $($PYTHON_VERSION --version)${NC}"

# Создание директории проекта
echo -e "${YELLOW}Создание директории проекта...${NC}"
sudo mkdir -p $DEPLOY_DIR
sudo chown $USER:$USER $DEPLOY_DIR
echo -e "${GREEN}✓ Директория создана: $DEPLOY_DIR${NC}"

# Копирование файлов
echo -e "${YELLOW}Копирование файлов...${NC}"
cp -r . $DEPLOY_DIR/
cd $DEPLOY_DIR
echo -e "${GREEN}✓ Файлы скопированы${NC}"

# Создание виртуального окружения
echo -e "${YELLOW}Создание виртуального окружения...${NC}"
$PYTHON_VERSION -m venv venv
source venv/bin/activate
echo -e "${GREEN}✓ Виртуальное окружение создано${NC}"

# Обновление pip
echo -e "${YELLOW}Обновление pip...${NC}"
pip install --upgrade pip --quiet
echo -e "${GREEN}✓ pip обновлён${NC}"

# Установка зависимостей
echo -e "${YELLOW}Установка зависимостей...${NC}"
pip install -r requirements.txt --quiet
echo -e "${GREEN}✓ Зависимости установлены${NC}"

# Проверка .env файла
if [ ! -f .env ]; then
    echo -e "${YELLOW}⚠️  Файл .env не найден${NC}"
    echo "Создаём .env из примера..."
    if [ -f .env.example ]; then
        cp .env.example .env
        echo -e "${RED}ВАЖНО: Отредактируйте .env и добавьте ваш PROXIAPI_API_KEY${NC}"
        echo -e "${YELLOW}Команда: nano $DEPLOY_DIR/.env${NC}"
    else
        echo -e "${RED}Ошибка: .env.example не найден${NC}"
        exit 1
    fi
else
    echo -e "${GREEN}✓ .env файл найден${NC}"
fi

# Создание необходимых директорий
echo -e "${YELLOW}Создание директорий для отчетов и логов...${NC}"
mkdir -p reports/json reports/html logs config
echo -e "${GREEN}✓ Директории созданы${NC}"

# Проверка конфигурации
if [ ! -f config/sites.yaml ]; then
    echo -e "${YELLOW}Создание примера конфигурации sites.yaml...${NC}"
    cat > config/sites.yaml << 'EOF'
# Конфигурация сайтов для мониторинга UX

sites:
  - url: https://example.com
    name: Example Site
    enabled: true
EOF
    echo -e "${GREEN}✓ Конфигурация создана${NC}"
fi

# Настройка прав
echo -e "${YELLOW}Настройка прав доступа...${NC}"
chmod +x deploy/setup_cron.sh
chmod 755 $DEPLOY_DIR
chmod 600 .env
echo -e "${GREEN}✓ Права настроены${NC}"

# Тестовый запуск
echo -e "${YELLOW}Тестовый запуск...${NC}"
if $DEPLOY_DIR/venv/bin/python agent.py https://example.com > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Тестовый запуск успешен${NC}"
else
    echo -e "${YELLOW}⚠️  Тестовый запуск завершился с предупреждением${NC}"
    echo -e "${YELLOW}Проверьте настройки API ключа в .env${NC}"
fi

echo ""
echo -e "${GREEN}=================================="
echo "✅ Деплой завершен успешно!"
echo "==================================${NC}"
echo ""
echo "📋 Следующие шаги:"
echo ""
echo "1. Настройте API ключ:"
echo "   nano $DEPLOY_DIR/.env"
echo "   Добавьте: PROXIAPI_API_KEY=ваш_ключ"
echo ""
echo "2. Настройте список сайтов:"
echo "   nano $DEPLOY_DIR/config/sites.yaml"
echo ""
echo "3. Настройте автоматический запуск (cron):"
echo "   cd $DEPLOY_DIR && bash deploy/setup_cron.sh"
echo ""
echo "4. Ручной запуск для проверки:"
echo "   cd $DEPLOY_DIR"
echo "   source venv/bin/activate"
echo "   python scheduler.py"
echo ""
echo "📁 Пути:"
echo "   Проект: $DEPLOY_DIR"
echo "   Отчеты: $DEPLOY_DIR/reports/"
echo "   Логи: $DEPLOY_DIR/logs/"
echo ""