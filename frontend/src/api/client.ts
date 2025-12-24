import axios from 'axios';

const client = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Debug logger
function debugLog(message: string, ...args: any[]) {
  const timestamp = new Date().toISOString();
  const logEntry = `[${timestamp}] ${message} ${args.map(a => JSON.stringify(a)).join(' ')}`;
  console.log(message, ...args);

  // Save to localStorage for debugging across page reloads
  const logs = JSON.parse(localStorage.getItem('debug_logs') || '[]');
  logs.push(logEntry);
  if (logs.length > 50) logs.shift(); // Keep last 50 logs
  localStorage.setItem('debug_logs', JSON.stringify(logs));
}

// Request interceptor - add token to requests
client.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    debugLog('[Axios Request]', config.method?.toUpperCase(), config.url, 'Token:', token ? `${token.substring(0, 20)}...` : 'NONE');
    if (token) {
      if (!config.headers) {
        config.headers = {} as any;
      }
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor - handle 401 errors
client.interceptors.response.use(
  (response) => response,
  (error) => {
    // Don't redirect on login endpoint failures
    const isLoginRequest = error.config?.url?.includes('/auth/login');

    if (error.response?.status === 401 && !isLoginRequest) {
      debugLog('[Axios Interceptor] 401 Unauthorized on:', error.config?.url);
      debugLog('[Axios Interceptor] Clearing auth and redirecting to /login');
      localStorage.removeItem('access_token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default client;
