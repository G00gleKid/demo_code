import { BrowserRouter, Routes, Route, Link, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import { ProtectedRoute } from './components/ProtectedRoute';
import LoginPage from './pages/LoginPage';
import ParticipantsPage from './pages/ParticipantsPage';
import MeetingsPage from './pages/MeetingsPage';
import CreateMeetingPage from './pages/CreateMeetingPage';
import MeetingDetailPage from './pages/MeetingDetailPage';
import AlgorithmSettingsPage from './pages/AlgorithmSettingsPage';
import EITestingTeamSelectionPage from './pages/EITestingTeamSelectionPage';
import EITestingParticipantSelectionPage from './pages/EITestingParticipantSelectionPage';
import EITestingQuestionnairePage from './pages/EITestingQuestionnairePage';
import EITestingResultPage from './pages/EITestingResultPage';
import SITestingTeamSelectionPage from './pages/SITestingTeamSelectionPage';
import SITestingParticipantSelectionPage from './pages/SITestingParticipantSelectionPage';
import SITestingQuestionnairePage from './pages/SITestingQuestionnairePage';
import SITestingResultPage from './pages/SITestingResultPage';
import './App.css';

function AppContent() {
  const { user, logout, isAuthenticated, isLoading } = useAuth();

  console.log('[AppContent] Render - isLoading:', isLoading, 'isAuthenticated:', isAuthenticated, 'user:', user);

  if (isLoading) {
    console.log('[AppContent] Showing loading screen');
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
        Загрузка...
      </div>
    );
  }

  if (!isAuthenticated) {
    console.log('[AppContent] Not authenticated, redirecting to login');
    return (
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        {/* Public EI Testing Routes - TEMPORARY for demo */}
        <Route path="/testing/ei" element={<EITestingTeamSelectionPage />} />
        <Route path="/testing/ei/team/:teamId" element={<EITestingParticipantSelectionPage />} />
        <Route path="/testing/ei/team/:teamId/member/:memberId" element={<EITestingQuestionnairePage />} />
        <Route path="/testing/ei/result" element={<EITestingResultPage />} />
        {/* Public SI Testing Routes - TEMPORARY for demo */}
        <Route path="/testing/si" element={<SITestingTeamSelectionPage />} />
        <Route path="/testing/si/team/:teamId" element={<SITestingParticipantSelectionPage />} />
        <Route path="/testing/si/team/:teamId/member/:memberId" element={<SITestingQuestionnairePage />} />
        <Route path="/testing/si/result" element={<SITestingResultPage />} />
        <Route path="*" element={<Navigate to="/login" replace />} />
      </Routes>
    );
  }

  console.log('[AppContent] Authenticated, showing main app');

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
  // Add debug helper to window
  if (typeof window !== 'undefined') {
    (window as any).showDebugLogs = () => {
      const logs = JSON.parse(localStorage.getItem('debug_logs') || '[]');
      console.log('=== DEBUG LOGS ===');
      logs.forEach((log: string) => console.log(log));
      console.log('=== END DEBUG LOGS ===');
    };
    (window as any).clearDebugLogs = () => {
      localStorage.removeItem('debug_logs');
      console.log('Debug logs cleared');
    };
  }

  return (
    <BrowserRouter>
      <AuthProvider>
        <AppContent />
      </AuthProvider>
    </BrowserRouter>
  );
}

export default App;
