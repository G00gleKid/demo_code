# Следующие шаги для завершения авторизации

## ✅ Что уже реализовано (Backend - 70%)

### Инфраструктура
1. ✅ Зависимости: python-jose, passlib добавлены в [pyproject.toml](backend/pyproject.toml)
2. ✅ Конфигурация: SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_HOURS в [config.py](backend/app/config.py)

### Модели данных
3. ✅ [Team](backend/app/models/team.py) - модель команды
4. ✅ [User](backend/app/models/user.py) - модель пользователя (тимлид)
5. ✅ [Participant](backend/app/models/participant.py) - обновлён с team_id
6. ✅ [Meeting](backend/app/models/meeting.py) - обновлён с team_id
7. ✅ [models/__init__.py](backend/app/models/__init__.py) - обновлён

### Схемы Pydantic
8. ✅ [team.py](backend/app/schemas/team.py) - Team, TeamCreate, TeamBase
9. ✅ [user.py](backend/app/schemas/user.py) - User, UserWithTeam, UserLogin, TokenResponse
10. ✅ [schemas/__init__.py](backend/app/schemas/__init__.py) - обновлён

### Сервисы
11. ✅ [auth_service.py](backend/app/services/auth_service.py) - JWT создание/валидация, verify_password
12. ✅ [user_service.py](backend/app/services/user_service.py) - get_user_by_email, authenticate_user

### Зависимости и роутеры
13. ✅ [dependencies/auth.py](backend/app/dependencies/auth.py) - get_current_user, get_current_team_id
14. ✅ [routers/auth.py](backend/app/routers/auth.py) - /login, /me, /logout
15. ✅ [main.py](backend/app/main.py) - роутер auth зарегистрирован

### Миграции и скрипты
16. ✅ [Миграция БД](backend/alembic/versions/aaecafab3c0c_add_authentication.py) - teams, users, team_id
17. ✅ [seed_auth_data.py](backend/seed_auth_data.py) - создание тестовых данных
18. ✅ [migrate_existing_data.py](backend/migrate_existing_data.py) - миграция существующих данных

---

## ⏳ Что нужно доделать (Backend - 30%)

### 1. Обновить роутеры для фильтрации по team_id

#### a) [participants.py](backend/app/routers/participants.py)

Добавить import:
```python
from app.dependencies.auth import get_current_team_id
```

Обновить каждый эндпоинт:
```python
@router.get("/")
async def list_participants(
    team_id: int = Depends(get_current_team_id),  # ДОБАВИТЬ
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Participant).where(Participant.team_id == team_id)  # ДОБАВИТЬ ФИЛЬТР
    )
    return result.scalars().all()
```

Аналогично для всех эндпоинтов: create, get, update, delete.

#### b) [meetings.py](backend/app/routers/meetings.py)

Добавить import и фильтрацию по team_id во все эндпоинты.

Важно для `add_participants`:
```python
# Проверить что участники из той же команды
stmt = select(Participant).where(
    Participant.id.in_(participant_ids),
    Participant.team_id == team_id  # ДОБАВИТЬ
)
participants = (await db.execute(stmt)).scalars().all()
if len(participants) != len(participant_ids):
    raise HTTPException(
        status_code=400,
        detail="Some participants do not belong to your team"
    )
```

#### c) [assignments.py](backend/app/routers/assignments.py)

Добавить проверку принадлежности participant к команде пользователя.

### 2. Выполнить миграцию БД

```bash
cd backend

# Установить зависимости
uv sync

# Выполнить миграцию
uv run alembic upgrade head

# Мигрировать существующие данные
uv run python migrate_existing_data.py

# Создать тестовые данные
uv run python seed_auth_data.py
```

### 3. Проверить что backend работает

```bash
# Запустить сервер
cd backend
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Проверить:
- http://localhost:8000/docs - Swagger UI должен показывать /api/auth endpoints
- POST /api/auth/login с `{"email": "frontend@team.com", "password": "password123"}` должен вернуть токен

---

## ⏳ Что нужно сделать (Frontend - 100%)

### 1. Создать API модуль авторизации

**Файл:** [frontend/src/api/auth.ts](frontend/src/api/auth.ts)

```typescript
import client from './client';

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface User {
  id: number;
  email: string;
  full_name: string;
  team_id: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  team: {
    id: number;
    name: string;
    created_at: string;
    updated_at: string;
  };
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export const authAPI = {
  async login(credentials: LoginCredentials): Promise<LoginResponse> {
    const response = await client.post<LoginResponse>('/auth/login', credentials);
    return response.data;
  },

  async getCurrentUser(): Promise<User> {
    const response = await client.get<User>('/auth/me');
    return response.data;
  },

  async logout(): Promise<void> {
    await client.post('/auth/logout');
  },
};
```

### 2. Обновить Axios клиент

**Файл:** [frontend/src/api/client.ts](frontend/src/api/client.ts)

Добавить interceptors:

```typescript
import axios from 'axios';

const client = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor - добавить токен
client.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor - обработать 401
client.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default client;
```

### 3. Создать контекст авторизации

**Файл:** [frontend/src/contexts/AuthContext.tsx](frontend/src/contexts/AuthContext.tsx)

```typescript
import { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { authAPI, LoginCredentials, User } from '../api/auth';

interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (credentials: LoginCredentials) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem('access_token');
    const storedUser = localStorage.getItem('user');

    if (token && storedUser) {
      try {
        setUser(JSON.parse(storedUser));
      } catch (e) {
        localStorage.removeItem('access_token');
        localStorage.removeItem('user');
      }
    }

    setIsLoading(false);
  }, []);

  const login = async (credentials: LoginCredentials) => {
    const response = await authAPI.login(credentials);
    localStorage.setItem('access_token', response.access_token);
    localStorage.setItem('user', JSON.stringify(response.user));
    setUser(response.user);
  };

  const logout = () => {
    authAPI.logout().catch(() => {});
    localStorage.removeItem('access_token');
    localStorage.removeItem('user');
    setUser(null);
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        isLoading,
        isAuthenticated: !!user,
        login,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
```

### 4. Создать Protected Route

**Файл:** [frontend/src/components/ProtectedRoute.tsx](frontend/src/components/ProtectedRoute.tsx)

```typescript
import { Navigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

interface ProtectedRouteProps {
  children: React.ReactNode;
}

export function ProtectedRoute({ children }: ProtectedRouteProps) {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return <div style={{ display: 'flex', justifyContent: 'center', padding: '2rem' }}>Загрузка...</div>;
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return <>{children}</>;
}
```

### 5. Создать страницу входа

**Файл:** [frontend/src/pages/LoginPage.tsx](frontend/src/pages/LoginPage.tsx)

```typescript
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import './LoginPage.css';

export default function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    try {
      await login({ email, password });
      navigate('/');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Ошибка входа. Попробуйте снова.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="login-container">
      <div className="login-card">
        <h1>Вход в систему</h1>
        <p className="login-subtitle">Система распределения ролей</p>

        <form onSubmit={handleSubmit} className="login-form">
          <div className="form-group">
            <label htmlFor="email">Email</label>
            <input
              id="email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              autoFocus
              placeholder="your@email.com"
            />
          </div>

          <div className="form-group">
            <label htmlFor="password">Пароль</label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              placeholder="••••••••"
            />
          </div>

          {error && <div className="error-message">{error}</div>}

          <button type="submit" disabled={isLoading} className="login-button">
            {isLoading ? 'Вход...' : 'Войти'}
          </button>
        </form>

        <div className="demo-credentials">
          <p><strong>Демо-аккаунты:</strong></p>
          <p>frontend@team.com / password123</p>
          <p>backend@team.com / password123</p>
          <p>devops@team.com / password123</p>
        </div>
      </div>
    </div>
  );
}
```

**Файл:** [frontend/src/pages/LoginPage.css](frontend/src/pages/LoginPage.css)

```css
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.login-card {
  background: white;
  padding: 2rem;
  border-radius: 8px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 400px;
}

.login-card h1 {
  margin: 0 0 0.5rem;
  color: #333;
}

.login-subtitle {
  margin: 0 0 2rem;
  color: #666;
  font-size: 0.9rem;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-group label {
  font-weight: 500;
  color: #333;
}

.form-group input {
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
}

.form-group input:focus {
  outline: none;
  border-color: #667eea;
}

.error-message {
  padding: 0.75rem;
  background: #fee;
  border: 1px solid #fcc;
  border-radius: 4px;
  color: #c33;
  font-size: 0.9rem;
}

.login-button {
  padding: 0.75rem;
  background: #667eea;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.2s;
}

.login-button:hover:not(:disabled) {
  background: #5568d3;
}

.login-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.demo-credentials {
  margin-top: 1.5rem;
  padding-top: 1.5rem;
  border-top: 1px solid #eee;
  font-size: 0.85rem;
  color: #666;
}

.demo-credentials p {
  margin: 0.25rem 0;
}
```

### 6. Обновить App.tsx

**Файл:** [frontend/src/App.tsx](frontend/src/App.tsx)

```typescript
import { BrowserRouter, Routes, Route, Link, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import { ProtectedRoute } from './components/ProtectedRoute';
import LoginPage from './pages/LoginPage';
import ParticipantsPage from './pages/ParticipantsPage';
import MeetingsPage from './pages/MeetingsPage';
import CreateMeetingPage from './pages/CreateMeetingPage';
import MeetingDetailPage from './pages/MeetingDetailPage';
import AlgorithmSettingsPage from './pages/AlgorithmSettingsPage';
import './App.css';

function AppContent() {
  const { user, logout, isAuthenticated } = useAuth();

  if (!isAuthenticated) {
    return (
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="*" element={<Navigate to="/login" replace />} />
      </Routes>
    );
  }

  return (
    <div className="app">
      <nav className="navbar">
        <h1>Система распределения ролей</h1>
        <div className="nav-links">
          <Link to="/">Встречи</Link>
          <Link to="/participants">Участники</Link>
          <Link to="/meetings/new">Новая встреча</Link>
          <Link to="/settings">Настройки алгоритма</Link>
        </div>
        <div className="user-info">
          <span>{user?.full_name} ({user?.team.name})</span>
          <button onClick={logout} className="logout-button">Выйти</button>
        </div>
      </nav>

      <main className="main-content">
        <Routes>
          <Route path="/" element={<ProtectedRoute><MeetingsPage /></ProtectedRoute>} />
          <Route path="/participants" element={<ProtectedRoute><ParticipantsPage /></ProtectedRoute>} />
          <Route path="/meetings/new" element={<ProtectedRoute><CreateMeetingPage /></ProtectedRoute>} />
          <Route path="/meetings/:id" element={<ProtectedRoute><MeetingDetailPage /></ProtectedRoute>} />
          <Route path="/settings" element={<ProtectedRoute><AlgorithmSettingsPage /></ProtectedRoute>} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </main>
    </div>
  );
}

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <AppContent />
      </AuthProvider>
    </BrowserRouter>
  );
}

export default App;
```

**Обновить стили в [App.css](frontend/src/App.css):**

Добавить:
```css
.user-info {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-left: auto;
}

.user-info span {
  color: white;
  font-size: 0.9rem;
}

.logout-button {
  padding: 0.5rem 1rem;
  background: rgba(255, 255, 255, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.3);
  color: white;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: background 0.2s;
}

.logout-button:hover {
  background: rgba(255, 255, 255, 0.3);
}
```

---

## 🧪 Тестирование

После завершения всех шагов:

1. **Backend:**
```bash
cd backend
uv run uvicorn app.main:app --reload
```

2. **Frontend:**
```bash
cd frontend
npm run dev
```

3. **Тесты:**
   - Войти как frontend@team.com - увидеть только участников Frontend Team
   - Войти как backend@team.com - увидеть только участников Backend Team
   - Создать участника - проверить что team_id устанавливается автоматически
   - Попытаться добавить участника из другой команды во встречу - должна быть ошибка
   - Выйти - проверить перенаправление на /login

---

## 📋 Чеклист

### Backend
- [ ] Обновить participants.py (фильтрация)
- [ ] Обновить meetings.py (фильтрация)
- [ ] Обновить assignments.py (фильтрация)
- [ ] Выполнить миграцию БД
- [ ] Запустить seed скрипты
- [ ] Проверить /api/docs

### Frontend
- [ ] Создать auth.ts
- [ ] Обновить client.ts
- [ ] Создать AuthContext.tsx
- [ ] Создать ProtectedRoute.tsx
- [ ] Создать LoginPage.tsx + CSS
- [ ] Обновить App.tsx + CSS
- [ ] Тестировать поток авторизации

### Проверка
- [ ] Login/logout работает
- [ ] Токены сохраняются в localStorage
- [ ] Защищенные роуты перенаправляют на /login
- [ ] Фильтрация по team_id работает
- [ ] Разные тимлиды видят только свои данные
