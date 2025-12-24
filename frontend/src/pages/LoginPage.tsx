import { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import './LoginPage.css';

export default function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const { login } = useAuth();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    try {
      console.log('[LoginPage] Calling login...');
      await login({ email, password });
      console.log('[LoginPage] Login successful, redirecting...');
      // Use window.location to ensure full page reload with token
      window.location.href = '/';
    } catch (err: any) {
      console.error('[LoginPage] Login failed:', err);
      setError(err.response?.data?.detail || 'Ошибка входа. Попробуйте снова.');
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
