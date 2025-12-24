import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { meetingsApi } from '../api/meetings';
import { Meeting } from '../api/types';

function MeetingsPage() {
  const [meetings, setMeetings] = useState<Meeting[]>([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    loadMeetings();
  }, []);

  const loadMeetings = async () => {
    try {
      console.log('[MeetingsPage] Loading meetings...');
      const data = await meetingsApi.getAll();
      console.log('[MeetingsPage] Meetings loaded:', data);
      setMeetings(data);
    } catch (error) {
      console.error('[MeetingsPage] Failed to load meetings:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm('Вы уверены, что хотите удалить эту встречу?')) return;

    try {
      await meetingsApi.delete(id);
      loadMeetings();
    } catch (error) {
      console.error('Failed to delete meeting:', error);
      alert('Не удалось удалить встречу');
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
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (loading) return <div className="loading">Загрузка...</div>;

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
        <h1 className="page-title">Встречи</h1>
        <button className="btn-primary" onClick={() => navigate('/meetings/new')}>
          Создать встречу
        </button>
      </div>

      {meetings.length === 0 ? (
        <div className="empty-state">
          <h3>Пока нет встреч</h3>
          <p>Создайте первую встречу для начала распределения ролей</p>
        </div>
      ) : (
        <div className="grid grid-2">
          {meetings.map((meeting) => (
            <div key={meeting.id} className="card">
              <h3 style={{ marginBottom: '0.5rem' }}>{meeting.title}</h3>
              <p style={{ color: '#7f8c8d', marginBottom: '0.5rem' }}>
                {formatMeetingType(meeting.meeting_type)}
              </p>
              <p style={{ marginBottom: '0.5rem' }}>
                <strong>Время:</strong> {formatDateTime(meeting.scheduled_time)}
              </p>
              <p style={{ marginBottom: '1rem' }}>
                <strong>Участники:</strong> {meeting.participants.length}
              </p>

              <div className="actions">
                <button
                  className="btn-primary"
                  onClick={() => navigate(`/meetings/${meeting.id}`)}
                >
                  Подробнее
                </button>
                <button
                  className="btn-danger"
                  onClick={() => handleDelete(meeting.id)}
                >
                  Удалить
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default MeetingsPage;
