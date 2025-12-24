import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { meetingsApi } from '../api/meetings';
import { Meeting, RoleAssignment } from '../api/types';

function MeetingDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [meeting, setMeeting] = useState<Meeting | null>(null);
  const [assignments, setAssignments] = useState<RoleAssignment[]>([]);
  const [loading, setLoading] = useState(true);
  const [assigning, setAssigning] = useState(false);

  useEffect(() => {
    loadMeeting();
    loadAssignments();
  }, [id]);

  const loadMeeting = async () => {
    try {
      const data = await meetingsApi.getById(parseInt(id!));
      setMeeting(data);
    } catch (error) {
      console.error('Failed to load meeting:', error);
      alert('Failed to load meeting');
      navigate('/');
    } finally {
      setLoading(false);
    }
  };

  const loadAssignments = async () => {
    try {
      const data = await meetingsApi.getAssignments(parseInt(id!));
      setAssignments(data);
    } catch (error) {
      console.error('Failed to load assignments:', error);
    }
  };

  const handleAssignRoles = async () => {
    if (!meeting) return;

    if (meeting.participants.length < 7) {
      if (!confirm(`В этой встрече только ${meeting.participants.length} участников, но нужно назначить 7 ролей. Некоторые участники могут получить несколько ролей. Продолжить?`)) {
        return;
      }
    }

    setAssigning(true);
    try {
      const result = await meetingsApi.assignRoles(parseInt(id!));
      setAssignments(result.assignments);
      alert(`Успешно назначено ${result.total_assigned} ролей!`);
    } catch (error) {
      console.error('Failed to assign roles:', error);
      alert('Не удалось назначить роли. Проверьте, есть ли участники во встрече.');
    } finally {
      setAssigning(false);
    }
  };

  const formatMeetingType = (type: string) => {
    const types: Record<string, string> = {
      'brainstorm': 'Мозговой штурм',
      'review': 'Ревью/Ретроспектива',
      'planning': 'Планирование',
      'status_update': 'Статус-обновление'
    };
    return types[type] || type;
  };

  const formatDateTime = (dateStr: string) => {
    const date = new Date(dateStr);
    return date.toLocaleString('ru-RU', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const formatRole = (role: string) => {
    const roles: Record<string, string> = {
      'moderator': 'Модератор',
      'speaker': 'Спикер',
      'time_manager': 'Тайм-менеджер',
      'critic': 'Критик',
      'ideologue': 'Идеолог',
      'mediator': 'Медиатор',
      'harmonizer': 'Гармонизатор'
    };
    return roles[role] || role;
  };

  const getRoleColor = (score: number) => {
    if (score >= 80) return '#2ecc71';
    if (score >= 60) return '#f39c12';
    return '#e74c3c';
  };

  if (loading) return <div className="loading">Загрузка...</div>;
  if (!meeting) return <div>Встреча не найдена</div>;

  return (
    <div>
      <button
        onClick={() => navigate('/')}
        style={{ marginBottom: '1rem', backgroundColor: '#95a5a6', color: 'white' }}
      >
        ← Назад к встречам
      </button>

      <h1 className="page-title">{meeting.title}</h1>

      <div className="card" style={{ marginBottom: '2rem' }}>
        <h2 style={{ marginBottom: '1rem' }}>Детали встречи</h2>
        <div className="grid grid-2">
          <div>
            <p><strong>Тип:</strong> {formatMeetingType(meeting.meeting_type)}</p>
            <p><strong>Запланирована на:</strong> {formatDateTime(meeting.scheduled_time)}</p>
          </div>
          <div>
            <p><strong>Участники:</strong> {meeting.participants.length}</p>
          </div>
        </div>

        <div style={{ marginTop: '1.5rem' }}>
          <h3 style={{ marginBottom: '0.5rem' }}>Участники:</h3>
          <ul style={{ listStyle: 'none', padding: 0 }}>
            {meeting.participants.map((p) => (
              <li key={p.id} style={{ padding: '0.25rem 0' }}>
                • {p.name} ({p.email})
              </li>
            ))}
          </ul>
        </div>
      </div>

      <div className="card">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
          <h2>Распределение ролей</h2>
          <button
            className="btn-success"
            onClick={handleAssignRoles}
            disabled={assigning || meeting.participants.length === 0}
          >
            {assigning ? 'Назначение...' : assignments.length > 0 ? 'Пересчитать роли' : 'Назначить роли'}
          </button>
        </div>

        {meeting.participants.length === 0 && (
          <p className="error">Во встрече нет участников. Сначала добавьте участников.</p>
        )}

        {assignments.length === 0 ? (
          <div className="empty-state">
            <h3>Роли еще не назначены</h3>
            <p>Нажмите "Назначить роли" для запуска алгоритма распределения</p>
          </div>
        ) : (
          <>
            <table>
              <thead>
                <tr>
                  <th>Участник</th>
                  <th>Роль</th>
                  <th>Оценка соответствия</th>
                </tr>
              </thead>
              <tbody>
                {assignments.map((assignment) => (
                  <tr key={assignment.id}>
                    <td>{assignment.participant_name || `Участник #${assignment.participant_id}`}</td>
                    <td><strong>{formatRole(assignment.role)}</strong></td>
                    <td>
                      <span style={{
                        color: getRoleColor(assignment.fitness_score),
                        fontWeight: 'bold'
                      }}>
                        {assignment.fitness_score.toFixed(1)}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>

            <div style={{ marginTop: '1rem', padding: '1rem', backgroundColor: '#f8f9fa', borderRadius: '4px' }}>
              <p style={{ fontSize: '0.9rem', color: '#7f8c8d' }}>
                <strong>Легенда оценки соответствия:</strong>{' '}
                <span style={{ color: '#2ecc71' }}>80-100: Отлично подходит</span>,{' '}
                <span style={{ color: '#f39c12' }}>60-79: Хорошо подходит</span>,{' '}
                <span style={{ color: '#e74c3c' }}>Менее 60: Плохо подходит</span>
              </p>
            </div>
          </>
        )}
      </div>
    </div>
  );
}

export default MeetingDetailPage;
