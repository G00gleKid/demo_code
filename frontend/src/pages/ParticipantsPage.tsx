import { useState, useEffect } from 'react';
import { participantsApi } from '../api/participants';
import { Participant, ParticipantCreate } from '../api/types';
import ParticipantStatsModal from '../components/ParticipantStatsModal';

function ParticipantsPage() {
  const [participants, setParticipants] = useState<Participant[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [selectedParticipantId, setSelectedParticipantId] = useState<number | null>(null);
  const [formData, setFormData] = useState<ParticipantCreate>({
    name: '',
    email: '',
    chronotype: 'intermediate',
    peak_hours_start: 9,
    peak_hours_end: 13,
    emotional_intelligence: 75,
    social_intelligence: 75,
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
    try {
      await participantsApi.create(formData);
      setShowForm(false);
      setFormData({
        name: '',
        email: '',
        chronotype: 'intermediate',
        peak_hours_start: 9,
        peak_hours_end: 13,
        emotional_intelligence: 75,
        social_intelligence: 75,
      });
      loadParticipants();
    } catch (error) {
      console.error('Failed to create participant:', error);
      alert('Не удалось создать участника');
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm('Вы уверены, что хотите удалить этого участника?')) return;

    try {
      await participantsApi.delete(id);
      loadParticipants();
    } catch (error) {
      console.error('Failed to delete participant:', error);
      alert('Не удалось удалить участника');
    }
  };

  const handleRowClick = (participantId: number) => {
    setSelectedParticipantId(participantId);
  };

  if (loading) return <div className="loading">Загрузка...</div>;

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
        <h1 className="page-title">Участники</h1>
        <button className="btn-primary" onClick={() => setShowForm(!showForm)}>
          {showForm ? 'Отмена' : 'Добавить участника'}
        </button>
      </div>

      {showForm && (
        <div className="card" style={{ marginBottom: '2rem' }}>
          <h2 style={{ marginBottom: '1rem' }}>Новый участник</h2>
          <form onSubmit={handleSubmit}>
            <div className="grid grid-2">
              <div className="form-group">
                <label>Имя</label>
                <input
                  type="text"
                  required
                  value={formData.name}
                  onChange={(e) => setFormData({...formData, name: e.target.value})}
                />
              </div>

              <div className="form-group">
                <label>Email</label>
                <input
                  type="email"
                  required
                  value={formData.email}
                  onChange={(e) => setFormData({...formData, email: e.target.value})}
                />
              </div>

              <div className="form-group">
                <label>Хронотип</label>
                <select
                  value={formData.chronotype}
                  onChange={(e) => setFormData({...formData, chronotype: e.target.value as any})}
                >
                  <option value="morning">Утренний</option>
                  <option value="intermediate">Промежуточный</option>
                  <option value="evening">Вечерний</option>
                </select>
              </div>

              <div className="form-group">
                <label>Часы пиковой активности: {formData.peak_hours_start}:00 - {formData.peak_hours_end}:00</label>
                <div style={{ display: 'flex', gap: '0.5rem' }}>
                  <input
                    type="number"
                    min="0"
                    max="23"
                    value={formData.peak_hours_start}
                    onChange={(e) => setFormData({...formData, peak_hours_start: parseInt(e.target.value)})}
                  />
                  <span>до</span>
                  <input
                    type="number"
                    min="0"
                    max="23"
                    value={formData.peak_hours_end}
                    onChange={(e) => setFormData({...formData, peak_hours_end: parseInt(e.target.value)})}
                  />
                </div>
              </div>

              <div className="form-group">
                <label>Эмоциональный интеллект: {formData.emotional_intelligence}</label>
                <input
                  type="range"
                  min="0"
                  max="100"
                  value={formData.emotional_intelligence}
                  onChange={(e) => setFormData({...formData, emotional_intelligence: parseInt(e.target.value)})}
                />
              </div>

              <div className="form-group">
                <label>Социальный интеллект: {formData.social_intelligence}</label>
                <input
                  type="range"
                  min="0"
                  max="100"
                  value={formData.social_intelligence}
                  onChange={(e) => setFormData({...formData, social_intelligence: parseInt(e.target.value)})}
                />
              </div>
            </div>

            <button type="submit" className="btn-success" style={{ marginTop: '1rem' }}>
              Создать участника
            </button>
          </form>
        </div>
      )}

      {participants.length === 0 ? (
        <div className="empty-state">
          <h3>Пока нет участников</h3>
          <p>Добавьте первого участника для начала работы</p>
        </div>
      ) : (
        <table>
          <thead>
            <tr>
              <th>Имя</th>
              <th>Email</th>
              <th>Хронотип</th>
              <th>Часы активности</th>
              <th>ЭИ</th>
              <th>СИ</th>
              <th>Действия</th>
            </tr>
          </thead>
          <tbody>
            {participants.map((p) => (
              <tr
                key={p.id}
                onClick={() => handleRowClick(p.id)}
                style={{ cursor: 'pointer' }}
              >
                <td>{p.name}</td>
                <td>{p.email}</td>
                <td>
                  {p.chronotype === 'morning' ? 'Утренний' :
                   p.chronotype === 'intermediate' ? 'Промежуточный' : 'Вечерний'}
                </td>
                <td>{p.peak_hours_start}:00 - {p.peak_hours_end}:00</td>
                <td>{p.emotional_intelligence}</td>
                <td>{p.social_intelligence}</td>
                <td>
                  <button
                    className="btn-danger"
                    onClick={(e) => {
                      e.stopPropagation();
                      handleDelete(p.id);
                    }}
                  >
                    Удалить
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}

      {selectedParticipantId && (
        <ParticipantStatsModal
          participantId={selectedParticipantId}
          onClose={() => setSelectedParticipantId(null)}
        />
      )}
    </div>
  );
}

export default ParticipantsPage;
