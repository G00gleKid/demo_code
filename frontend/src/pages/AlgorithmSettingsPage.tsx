import { useEffect, useState } from 'react';
import { settingsApi, RoleRequirements, MeetingMultipliers } from '../api/settings';

const ROLE_NAMES: { [key: string]: string } = {
  moderator: 'Модератор',
  speaker: 'Спикер',
  time_manager: 'Тайм-менеджер',
  critic: 'Критик',
  ideologue: 'Идеолог',
  mediator: 'Медиатор',
  harmonizer: 'Гармонизатор',
};

const MEETING_TYPE_NAMES: { [key: string]: string } = {
  brainstorm: 'Мозговой штурм',
  review: 'Ревью',
  planning: 'Планирование',
  status_update: 'Статус-встреча',
};

const PARAMETER_NAMES: { [key: string]: string } = {
  ei: 'Эмоциональный интеллект (EI)',
  si: 'Социальный интеллект (SI)',
  energy: 'Энергия',
};

function AlgorithmSettingsPage() {
  const [roleRequirements, setRoleRequirements] = useState<RoleRequirements | null>(null);
  const [meetingMultipliers, setMeetingMultipliers] = useState<MeetingMultipliers | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchSettings = async () => {
      try {
        setLoading(true);
        const [requirements, multipliers] = await Promise.all([
          settingsApi.getRoleRequirements(),
          settingsApi.getMeetingMultipliers(),
        ]);
        setRoleRequirements(requirements);
        setMeetingMultipliers(multipliers);
      } catch (err) {
        setError('Ошибка загрузки настроек алгоритма');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchSettings();
  }, []);

  if (loading) {
    return (
      <div style={{ padding: '20px' }}>
        <h1>Настройки алгоритма</h1>
        <p>Загрузка...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ padding: '20px' }}>
        <h1>Настройки алгоритма</h1>
        <p style={{ color: 'red' }}>{error}</p>
      </div>
    );
  }

  return (
    <div style={{ padding: '20px', maxWidth: '1400px', margin: '0 auto' }}>
      <h1>Настройки алгоритма распределения ролей</h1>

      <div style={{ marginBottom: '40px' }}>
        <h2>📊 Требования к ролям</h2>
        <p style={{ color: '#666', marginBottom: '20px' }}>
          Для каждой роли указаны минимальные и максимальные значения параметров участника.
          Алгоритм оценивает, насколько характеристики участника попадают в эти диапазоны.
        </p>

        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(350px, 1fr))',
          gap: '20px'
        }}>
          {roleRequirements && Object.entries(roleRequirements).map(([role, req]) => (
            <div
              key={role}
              style={{
                border: '1px solid #ddd',
                borderRadius: '8px',
                padding: '15px',
                backgroundColor: '#f9f9f9'
              }}
            >
              <h3 style={{ marginTop: 0, marginBottom: '15px', color: '#333' }}>
                {ROLE_NAMES[role] || role}
              </h3>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                {(['ei', 'si', 'energy'] as const).map((param) => (
                  <div key={param}>
                    <div style={{
                      fontSize: '13px',
                      color: '#666',
                      marginBottom: '4px',
                      fontWeight: 500
                    }}>
                      {PARAMETER_NAMES[param]}
                    </div>
                    <div style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: '10px',
                      fontSize: '14px'
                    }}>
                      <div style={{
                        flex: 1,
                        height: '24px',
                        backgroundColor: '#e0e0e0',
                        borderRadius: '4px',
                        position: 'relative',
                        overflow: 'hidden'
                      }}>
                        <div style={{
                          position: 'absolute',
                          left: `${req[`${param}_min` as keyof typeof req]}%`,
                          width: `${req[`${param}_max` as keyof typeof req] - req[`${param}_min` as keyof typeof req]}%`,
                          height: '100%',
                          backgroundColor: '#4CAF50',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          color: 'white',
                          fontSize: '12px',
                          fontWeight: 'bold'
                        }}>
                          {req[`${param}_min` as keyof typeof req]}–{req[`${param}_max` as keyof typeof req]}
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>

      <div>
        <h2>⚖️ Множители типов встреч</h2>
        <p style={{ color: '#666', marginBottom: '20px' }}>
          В зависимости от типа встречи, важность некоторых ролей увеличивается или уменьшается.
          Базовая оценка соответствия умножается на эти коэффициенты.
        </p>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '30px' }}>
          {meetingMultipliers && Object.entries(meetingMultipliers).map(([meetingType, multipliers]) => (
            <div
              key={meetingType}
              style={{
                border: '1px solid #ddd',
                borderRadius: '8px',
                padding: '20px',
                backgroundColor: '#f9f9f9'
              }}
            >
              <h3 style={{ marginTop: 0, marginBottom: '15px', color: '#333' }}>
                {MEETING_TYPE_NAMES[meetingType] || meetingType}
              </h3>

              <div style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))',
                gap: '10px'
              }}>
                {Object.entries(multipliers)
                  .sort((a, b) => b[1] - a[1])
                  .map(([role, multiplier]) => {
                    const isHigh = multiplier >= 1.3;
                    const isLow = multiplier < 0.8;

                    return (
                      <div
                        key={role}
                        style={{
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'space-between',
                          padding: '10px 12px',
                          borderRadius: '6px',
                          backgroundColor: isHigh ? '#e8f5e9' : isLow ? '#ffebee' : '#fff',
                          border: `1px solid ${isHigh ? '#4CAF50' : isLow ? '#f44336' : '#ddd'}`,
                        }}
                      >
                        <span style={{ fontSize: '14px', color: '#333' }}>
                          {ROLE_NAMES[role] || role}
                        </span>
                        <span
                          style={{
                            fontWeight: 'bold',
                            fontSize: '15px',
                            color: isHigh ? '#2e7d32' : isLow ? '#c62828' : '#666'
                          }}
                        >
                          {multiplier.toFixed(1)}×
                        </span>
                      </div>
                    );
                  })}
              </div>

              <div style={{
                marginTop: '15px',
                fontSize: '12px',
                color: '#666',
                display: 'flex',
                gap: '20px'
              }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                  <div style={{
                    width: '16px',
                    height: '16px',
                    backgroundColor: '#e8f5e9',
                    border: '1px solid #4CAF50',
                    borderRadius: '3px'
                  }}></div>
                  <span>Высокий приоритет (≥1.3)</span>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                  <div style={{
                    width: '16px',
                    height: '16px',
                    backgroundColor: '#ffebee',
                    border: '1px solid #f44336',
                    borderRadius: '3px'
                  }}></div>
                  <span>Низкий приоритет (&lt;0.8)</span>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                  <div style={{
                    width: '16px',
                    height: '16px',
                    backgroundColor: '#fff',
                    border: '1px solid #ddd',
                    borderRadius: '3px'
                  }}></div>
                  <span>Нейтральный (1.0)</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div style={{
        marginTop: '40px',
        padding: '20px',
        backgroundColor: '#e3f2fd',
        borderRadius: '8px',
        border: '1px solid #2196F3'
      }}>
        <h3 style={{ marginTop: 0, color: '#1565c0' }}>ℹ️ Как работает алгоритм</h3>
        <ol style={{ margin: 0, paddingLeft: '20px', color: '#333' }}>
          <li style={{ marginBottom: '8px' }}>
            <strong>Расчет энергии:</strong> Определяется текущая энергия участника на основе хронотипа и времени встречи
          </li>
          <li style={{ marginBottom: '8px' }}>
            <strong>Базовая оценка:</strong> Для каждой пары участник-роль вычисляется, насколько EI, SI и энергия попадают в требуемые диапазоны
          </li>
          <li style={{ marginBottom: '8px' }}>
            <strong>Штраф за повторение:</strong> Если участник выполнял роль ранее: 2 раза подряд = -40%, 3 раза = -70%, 4+ раза = исключение
          </li>
          <li style={{ marginBottom: '8px' }}>
            <strong>Корректировка по типу встречи:</strong> Базовая оценка умножается на множитель для данного типа встречи
          </li>
          <li style={{ marginBottom: '8px' }}>
            <strong>Жадное назначение:</strong> Роли распределяются в порядке убывания финальной оценки, каждому участнику не более 1 роли
          </li>
        </ol>
      </div>
    </div>
  );
}

export default AlgorithmSettingsPage;
