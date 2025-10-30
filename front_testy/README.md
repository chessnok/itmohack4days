# Зинфин AI — демо интерфейс документов

Мини-приложение на React + TypeScript, воссоздающее трёхпанельный интерфейс: дерево компаний/сделок/документов, центральный просмотр PDF (заглушка) с вкладками и правую колонку с информацией и чат-логом.

## Запуск

1) Установите зависимости (Node 18+ уже найден):
```bash
cd /Users/nickgotswag/hack/zinfin-ai
npm i
```

2) Старт dev-сервера:
```bash
npm run dev
```
Откройте http://localhost:5173

3) Опционально: для реального обогащения DaData создайте `.env.local` и добавьте токен:
```
VITE_DADATA_TOKEN=ваш_токен
```

## Скрипты
- dev — запуск Vite dev server
- build — сборка
- preview — предпросмотр сборки

## Структура
- src/ui/Sidebar.tsx — дерево навигации
- src/ui/CenterPane.tsx — вкладки и просмотр документа (изображение)
- src/ui/InfoPane.tsx — карточка метаданных
- src/ui/ActionLog.tsx — чат-лог действий
- src/ui/mockData.ts — мок-данные
- src/ui/styles.css — стили
- src/ui/pipeline/* — извлечение, обогащение (DaData), проверки и саммари
