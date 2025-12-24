/**
 * EI Testing Module - Screen 1: Team Selection
 *
 * Public page (no authentication required)
 * Displays all teams from database, allows selection to proceed to participant selection
 *
 * @route /testing/ei
 * @temporary Remove when EI integration from external source is implemented
 */

import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { testingApi, TeamBasic } from '../api/testing';
import './EITesting.css';

function EITestingTeamSelectionPage() {
  const [teams, setTeams] = useState<TeamBasic[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>('');
  const navigate = useNavigate();

  useEffect(() => {
    loadTeams();
  }, []);

  const loadTeams = async () => {
    try {
      setLoading(true);
      setError('');
      const data = await testingApi.getAllTeams();
      setTeams(data);
    } catch (err) {
      console.error('Failed to load teams:', err);
      setError('Не удалось загрузить список команд. Проверьте подключение к серверу.');
    } finally {
      setLoading(false);
    }
  };

  const handleTeamSelect = (teamId: number) => {
    navigate(`/testing/ei/team/${teamId}`);
  };

  if (loading) {
    return (
      <div className="ei-testing-container">
        <div className="loading">Загрузка...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="ei-testing-container">
        <div className="card">
          <h1>Тестирование эмоционального интеллекта</h1>
          <div className="error-message">{error}</div>
          <button onClick={loadTeams} className="btn-primary">
            Попробовать снова
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="ei-testing-container">
      <div className="card">
        <h1>Тестирование эмоционального интеллекта</h1>
        <p className="subtitle">Выберите команду для начала тестирования</p>

        {teams.length === 0 ? (
          <div className="empty-state">
            <p>Пока нет команд в системе.</p>
            <p className="hint">Создайте команду в основном приложении.</p>
          </div>
        ) : (
          <div className="team-list">
            {teams.map((team) => (
              <div
                key={team.id}
                className="team-card"
                onClick={() => handleTeamSelect(team.id)}
              >
                <h3>{team.name}</h3>
                <p className="card-hint">Нажмите для выбора участников →</p>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default EITestingTeamSelectionPage;
