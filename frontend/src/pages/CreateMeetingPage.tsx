import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { meetingsApi } from '../api/meetings';
import { participantsApi } from '../api/participants';
import { MeetingCreate, Participant } from '../api/types';

function CreateMeetingPage() {
  const navigate = useNavigate();
  const [participants, setParticipants] = useState<Participant[]>([]);
  const [loading, setLoading] = useState(true);
  const [formData, setFormData] = useState<MeetingCreate>({
    title: '',
    meeting_type: 'brainstorm',
    scheduled_time: '',
    participant_ids: [],
  });

  useEffect(() => {
    loadParticipants();
  }, []);

  const loadParticipants = async () => {
    try {
      const data = await participantsApi.getAll();
      setParticipants(data);
    } catch (error) {
      console.error('Failed to load participants:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (formData.participant_ids.length === 0) {
      alert('Пожалуйста, выберите хотя бы одного участника');
      return;
    }

    try {
      const meeting = await meetingsApi.create(formData);
      navigate(`/meetings/${meeting.id}`);
    } catch (error) {
      console.error('Failed to create meeting:', error);
      alert('Не удалось создать встречу');
    }
  };

  const toggleParticipant = (id: number) => {
    setFormData({
      ...formData,
      participant_ids: formData.participant_ids.includes(id)
        ? formData.participant_ids.filter((pid) => pid !== id)
        : [...formData.participant_ids, id]
    });
  };

  if (loading) return <div className="loading">Загрузка...</div>;

  return (
    <div>
      <h1 className="page-title">Создать новую встречу</h1>

      <div className="card">
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Название встречи</label>
            <input
              type="text"
              required
              value={formData.title}
              onChange={(e) => setFormData({...formData, title: e.target.value})}
              placeholder="Например: Еженедельный мозговой штурм"
            />
          </div>

          <div className="form-group">
            <label>Тип встречи</label>
            <select
              value={formData.meeting_type}
              onChange={(e) => setFormData({...formData, meeting_type: e.target.value as any})}
            >
              <option value="brainstorm">Мозговой штурм</option>
              <option value="review">Ревью/Ретроспектива</option>
              <option value="planning">Планирование</option>
              <option value="status_update">Статус-обновление</option>
            </select>
          </div>

          <div className="form-group">
            <label>Запланированное время</label>
            <input
              type="datetime-local"
              required
              value={formData.scheduled_time}
              onChange={(e) => setFormData({...formData, scheduled_time: e.target.value})}
            />
          </div>

          <div className="form-group">
            <label>Участники (выбрано: {formData.participant_ids.length})</label>
            {participants.length === 0 ? (
              <p className="error">Нет доступных участников. Сначала создайте участников.</p>
            ) : (
              <div style={{ border: '1px solid #ddd', borderRadius: '4px', padding: '1rem', maxHeight: '300px', overflowY: 'auto' }}>
                {participants.map((p) => (
                  <div key={p.id} style={{ marginBottom: '0.5rem' }}>
                    <label style={{ display: 'flex', alignItems: 'center', cursor: 'pointer' }}>
                      <input
                        type="checkbox"
                        checked={formData.participant_ids.includes(p.id)}
                        onChange={() => toggleParticipant(p.id)}
                        style={{ marginRight: '0.5rem' }}
                      />
                      <span>{p.name} - {p.email}</span>
                    </label>
                  </div>
                ))}
              </div>
            )}
          </div>

          <div className="actions" style={{ marginTop: '1.5rem' }}>
            <button
              type="submit"
              className="btn-success"
              disabled={participants.length === 0}
            >
              Создать встречу
            </button>
            <button
              type="button"
              onClick={() => navigate('/')}
              style={{ backgroundColor: '#95a5a6', color: 'white' }}
            >
              Отмена
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default CreateMeetingPage;
