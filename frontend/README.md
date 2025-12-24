# Role Distribution Frontend

Frontend приложение для системы динамического распределения ролей в agile-командах.

## Технологический стек

- **React 18** - библиотека для построения UI
- **TypeScript** - типизированный JavaScript
- **Vite** - быстрый build tool
- **React Router** - маршрутизация
- **Axios** - HTTP клиент

## Установка и запуск

### 1. Установка зависимостей

```bash
cd frontend
npm install
```

### 2. Запуск development сервера

```bash
npm run dev
```

Приложение будет доступно по адресу: `http://localhost:5173`

### 3. Build для production

```bash
npm run build
```

Готовые файлы будут в директории `dist/`.

## Структура проекта

```
frontend/
├── src/
│   ├── api/                # API клиенты и типы
│   │   ├── client.ts       # Axios instance
│   │   ├── types.ts        # TypeScript interfaces
│   │   ├── participants.ts # Participants API
│   │   └── meetings.ts     # Meetings API
│   ├── pages/              # Страницы приложения
│   │   ├── ParticipantsPage.tsx
│   │   ├── MeetingsPage.tsx
│   │   ├── CreateMeetingPage.tsx
│   │   └── MeetingDetailPage.tsx
│   ├── App.tsx             # Главный компонент с роутингом
│   ├── main.tsx            # Точка входа
│   └── index.css           # Глобальные стили
├── index.html
├── package.json
└── vite.config.ts
```

## Основные страницы

### Participants (/participants)
- Просмотр всех участников команды
- Добавление нового участника с параметрами:
  - Имя, Email
  - Хронотип (утро/вечер/промежуточный)
  - Пик часов активности
  - Эмоциональный интеллект (слайдер 0-100)
  - Социальный интеллект (слайдер 0-100)
- Удаление участников

### Meetings (/)
- Список всех встреч
- Просмотр деталей встречи
- Удаление встреч

### Create Meeting (/meetings/new)
- Создание новой встречи
- Выбор типа: Brainstorm, Review, Planning, Status Update
- Указание времени проведения
- Выбор участников (multi-select)

### Meeting Detail (/meetings/:id)
- Просмотр информации о встрече
- Список участников
- **Кнопка "Assign Roles"** - запускает алгоритм распределения
- Таблица результатов:
  - Participant Name
  - Assigned Role
  - Fitness Score (цветовая индикация качества назначения)

## Пример использования

1. Добавьте участников через страницу `/participants`
2. Создайте встречу через `/meetings/new`
3. Выберите участников и тип встречи
4. Перейдите в детали встречи
5. Нажмите "Assign Roles" для запуска алгоритма
6. Просмотрите результаты распределения ролей

## Прокси для API

Vite настроен на проксирование запросов `/api/*` на `http://localhost:8000` (backend).
Убедитесь, что backend запущен на порту 8000.
