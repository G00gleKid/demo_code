import { useState, useEffect } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { participantsApi } from '../api/participants';
import { ParticipantStatistics } from '../api/types';

interface ParticipantStatsModalProps {
  participantId: number;
  onClose: () => void;
}

const ROLE_COLORS: Record<string, string> = {
  moderator: '#3498db',
  speaker: '#2ecc71',
  time_manager: '#f39c12',
  critic: '#e74c3c',
  ideologue: '#9b59b6',
  mediator: '#1abc9c',
  harmonizer: '#34495e',
};

const ROLE_NAMES: Record<string, string> = {
  moderator: 'Модератор',
  speaker: 'Спикер',
  time_manager: 'Тайм-менеджер',
  critic: 'Критик',
  ideologue: 'Идеолог',
  mediator: 'Медиатор',
  harmonizer: 'Гармонизатор',
};

function ParticipantStatsModal({ participantId, onClose }: ParticipantStatsModalProps) {
  const [statistics, setStatistics] = useState<ParticipantStatistics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadStatistics();
  }, [participantId]);

  const loadStatistics = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await participantsApi.getStatistics(participantId);
      setStatistics(data);
    } catch (err) {
      console.error('Failed to load statistics:', err);
      setError('Не удалось загрузить статистику');
    } finally {
      setLoading(false);
    }
  };

  const handleOverlayClick = (e: React.MouseEvent) => {
    if (e.target === e.currentTarget) {
      onClose();
    }
  };

  // Transform data for Recharts
  const chartData = statistics?.daily_breakdown.map(day => {
    const formattedDate = new Date(day.date).toLocaleDateString('ru-RU', {
      day: 'numeric',
      month: 'short'
    });
    return {
      date: formattedDate,
      ...day.roles
    };
  }) || [];

  // Get unique roles from statistics
  const usedRoles = statistics
    ? Object.keys(statistics.role_distribution).sort()
    : [];

  return (
    <div
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        backgroundColor: 'rgba(0, 0, 0, 0.5)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        zIndex: 1000,
      }}
      onClick={handleOverlayClick}
    >
      <div
        className="card"
        style={{
          maxWidth: '900px',
          width: '90%',
          minHeight: '500px',
          maxHeight: '90vh',
          overflow: 'auto',
          position: 'relative',
        }}
      >
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
          <h2 style={{ margin: 0 }}>
            {loading ? 'Загрузка...' : `Ролевая нагрузка: ${statistics?.participant_name}`}
          </h2>
          <button
            className="btn-danger"
            onClick={onClose}
            style={{ padding: '0.5rem 1rem' }}
          >
            Закрыть
          </button>
        </div>

        {loading && (
          <div style={{ textAlign: 'center', padding: '3rem' }}>
            <p>Загрузка статистики...</p>
          </div>
        )}

        {error && (
          <div style={{ textAlign: 'center', padding: '2rem' }}>
            <p style={{ color: '#e74c3c', marginBottom: '1rem' }}>{error}</p>
            <button className="btn-primary" onClick={loadStatistics}>
              Попробовать снова
            </button>
          </div>
        )}

        {!loading && !error && statistics && (
          <>
            <div style={{ marginBottom: '2rem' }}>
              <p style={{ fontSize: '1.1rem', color: '#2c3e50' }}>
                <strong>Всего встреч за последние 7 дней:</strong> {statistics.total_meetings}
              </p>
            </div>

            {statistics.total_meetings === 0 ? (
              <div className="empty-state">
                <h3>Нет встреч за последние 7 дней</h3>
                <p>У этого участника пока нет назначенных ролей за выбранный период</p>
              </div>
            ) : (
              <>
                <div style={{ marginBottom: '2rem' }}>
                  <h3 style={{ marginBottom: '1rem' }}>Распределение по ролям</h3>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '1rem' }}>
                    {usedRoles.map(role => (
                      <div
                        key={role}
                        style={{
                          display: 'flex',
                          alignItems: 'center',
                          gap: '0.5rem',
                        }}
                      >
                        <div
                          style={{
                            width: '20px',
                            height: '20px',
                            backgroundColor: ROLE_COLORS[role],
                            borderRadius: '3px',
                          }}
                        />
                        <span>
                          {ROLE_NAMES[role]}: <strong>{statistics.role_distribution[role]}</strong>
                        </span>
                      </div>
                    ))}
                  </div>
                </div>

                <div>
                  <h3 style={{ marginBottom: '1rem' }}>График активности за 7 дней</h3>
                  <ResponsiveContainer width="100%" height={400}>
                    <BarChart
                      data={chartData}
                      margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
                    >
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="date" />
                      <YAxis allowDecimals={false} />
                      <Tooltip />
                      <Legend />
                      {usedRoles.map(role => (
                        <Bar
                          key={role}
                          dataKey={role}
                          name={ROLE_NAMES[role]}
                          stackId="a"
                          fill={ROLE_COLORS[role]}
                        />
                      ))}
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </>
            )}
          </>
        )}
      </div>
    </div>
  );
}

export default ParticipantStatsModal;
