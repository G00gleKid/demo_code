/**
 * SI Testing Module - Screen 2: Participant Selection
 *
 * Public page (no authentication required)
 * Displays team participants, allows selection with warning if SI exists
 *
 * @route /testing/si/team/:teamId
 * @temporary Remove when SI integration from external source is implemented
 */

import { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { testingApi, ParticipantWithSI } from '../api/testing';
import './EITesting.css';

function SITestingParticipantSelectionPage() {
  const { teamId } = useParams<{ teamId: string }>();
  const [participants, setParticipants] = useState<ParticipantWithSI[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>('');
  const navigate = useNavigate();

  useEffect(() => {
    if (teamId) {
      loadParticipants();
    }
  }, [teamId]);

  const loadParticipants = async () => {
    try {
      setLoading(true);
      setError('');
      const data = await testingApi.getTeamParticipantsSI(Number(teamId));
      setParticipants(data);
    } catch (err) {
      console.error('Failed to load participants:', err);
      setError('Не удалось загрузить список участников. Команда не найдена или пуста.');
    } finally {
      setLoading(false);
    }
  };

  const handleParticipantSelect = (participant: ParticipantWithSI) => {
    // Check if participant already has SI score
    if (participant.social_intelligence > 0) {
      const confirmed = window.confirm(
        `У этого участника уже есть результат тестирования (${participant.social_intelligence} баллов). ` +
        `Новое прохождение перезапишет старый результат. Продолжить?`
      );
      if (!confirmed) {
        return;
      }
    }

    // Navigate to questionnaire
    navigate(`/testing/si/team/${teamId}/member/${participant.id}`, {
      state: { participantName: participant.name }
    });
  };

  const handleBack = () => {
    navigate('/testing/si');
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
          <h1>Выбор участника</h1>
          <div className="error-message">{error}</div>
          <button onClick={handleBack} className="btn-secondary">
            ← Назад к командам
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="ei-testing-container">
      <div className="card">
        <button onClick={handleBack} className="back-button">
          ← Назад к командам
        </button>

        <h1>Выберите участника для тестирования</h1>

        {participants.length === 0 ? (
          <div className="empty-state">
            <p>В этой команде пока нет участников.</p>
            <p className="hint">Добавьте участников в основном приложении.</p>
          </div>
        ) : (
          <div className="participant-list">
            {participants.map((participant) => (
              <div
                key={participant.id}
                className="participant-card"
                onClick={() => handleParticipantSelect(participant)}
              >
                <div className="participant-info">
                  <h3>{participant.name}</h3>
                  <p className="participant-email">{participant.email}</p>
                </div>
                <div className="participant-status">
                  {participant.social_intelligence > 0 ? (
                    <span className="ei-score">
                      СИ: {participant.social_intelligence}
                    </span>
                  ) : (
                    <span className="ei-score-empty">Не протестирован</span>
                  )}
                  <span className="card-arrow">→</span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default SITestingParticipantSelectionPage;
