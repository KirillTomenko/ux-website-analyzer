#!/bin/bash

# Настройка cron для автоматического запуска UX-рецензента
# Использование: bash setup_cron.sh

set -e

echo "=================================="
echo "⏰ Настройка cron"
echo "=================================="

# Получаем абсолютный путь к проекту
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON_PATH="$PROJECT_DIR/venv/bin/python"
SCHEDULER_PATH="$PROJECT_DIR/scheduler.py"

# Проверка файлов
if [ ! -f "$PYTHON_PATH" ]; then
    echo "❌ Ошибка: Python не найден в $PYTHON_PATH"
    echo "Запустите сначала deploy.sh"
    exit 1
fi

if [ ! -f "$SCHEDULER_PATH" ]; then
    echo "❌ Ошибка: scheduler.py не найден"
    exit 1
fi

echo "✓ Проект найден: $PROJECT_DIR"
echo ""

# Показываем варианты расписания
echo "Выберите частоту запуска анализа:"
echo ""
echo "1) Каждый день в 2:00 ночи (рекомендуется)"
echo "2) Каждый понедельник в 9:00"
echo "3) Каждые 6 часов"
echo "4) Каждый час"
echo "5) Каждые 12 часов"
echo "6) Пользовательское расписание"
echo ""
read -p "Ваш выбор (1-6): " choice

case $choice in
    1)
        CRON_SCHEDULE="0 2 * * *"
        DESCRIPTION="ежедневно в 2:00"
        ;;
    2)
        CRON_SCHEDULE="0 9 * * 1"
        DESCRIPTION="каждый понедельник в 9:00"
        ;;
    3)
        CRON_SCHEDULE="0 */6 * * *"
        DESCRIPTION="каждые 6 часов"
        ;;
    4)
        CRON_SCHEDULE="0 * * * *"
        DESCRIPTION="каждый час"
        ;;
    5)
        CRON_SCHEDULE="0 */12 * * *"
        DESCRIPTION="каждые 12 часов"
        ;;
    6)
        echo ""
        echo "Формат cron: минута час день месяц день_недели"
        echo "Примеры:"
        echo "  0 2 * * *     - каждый день в 2:00"
        echo "  */30 * * * *  - каждые 30 минут"
        echo "  0 */3 * * *   - каждые 3 часа"
        echo ""
        read -p "Введите расписание: " CRON_SCHEDULE
        DESCRIPTION="пользовательское"
        ;;
    *)
        echo "❌ Неверный выбор"
        exit 1
        ;;
esac

# Формируем команду для cron
CRON_COMMAND="$PYTHON_PATH $SCHEDULER_PATH >> $PROJECT_DIR/logs/cron.log 2>&1"

# Создаем временный файл с текущим crontab
TEMP_CRON=$(mktemp)
crontab -l > $TEMP_CRON 2>/dev/null || true

# Проверяем, нет ли уже такой задачи
if grep -q "$SCHEDULER_PATH" $TEMP_CRON; then
    echo ""
    echo "⚠️  Задача уже существует в crontab"
    echo "Удаляем старую задачу..."
    grep -v "$SCHEDULER_PATH" $TEMP_CRON > ${TEMP_CRON}.new || true
    mv ${TEMP_CRON}.new $TEMP_CRON
fi

# Добавляем новую задачу
echo "" >> $TEMP_CRON
echo "# UX-рецензент - автоматический анализ ($DESCRIPTION)" >> $TEMP_CRON
echo "$CRON_SCHEDULE $CRON_COMMAND" >> $TEMP_CRON

# Устанавливаем новый crontab
crontab $TEMP_CRON
rm $TEMP_CRON

echo ""
echo "=================================="
echo "✅ Cron задача добавлена успешно!"
echo "=================================="
echo ""
echo "📋 Детали:"
echo "   Расписание: $DESCRIPTION"
echo "   Команда: $PYTHON_PATH $SCHEDULER_PATH"
echo "   Логи: $PROJECT_DIR/logs/cron.log"
echo ""
echo "🔧 Управление:"
echo "   Просмотр задач:  crontab -l"
echo "   Редактирование:  crontab -e"
echo "   Удаление всех:   crontab -r"
echo ""
echo "📊 Просмотр логов:"
echo "   tail -f $PROJECT_DIR/logs/cron.log"
echo ""
echo "🧪 Тестовый запуск:"
echo "   cd $PROJECT_DIR"
echo "   source venv/bin/activate"
echo "   python scheduler.py"
echo ""

# Проверка синтаксиса cron
echo "📝 Текущие cron задачи:"
echo "---"
crontab -l | grep -A 1 "UX-рецензент" || echo "Задача добавлена"
echo "---"
echo ""
echo "✅ Готово! Анализ будет запускаться автоматически ($DESCRIPTION)"