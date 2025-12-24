/**
 * SI Testing Module - Screen 3: Questionnaire
 *
 * Public page (no authentication required)
 * 8-question SI assessment with progress tracking and score calculation
 *
 * @route /testing/si/team/:teamId/member/:memberId
 * @temporary Remove when SI integration from external source is implemented
 */

import { useState, useEffect } from 'react';
import { useNavigate, useParams, useLocation } from 'react-router-dom';
import { testingApi, ParticipantWithSI } from '../api/testing';
import './EITesting.css';

// SI Questions (8 items, 3 blocks)
const SI_QUESTIONS = [
  // Блок 1: Понимание эмоций и намерений (Social Awareness)
  { id: 1, text: "Я легко замечаю, когда коллега расстроен или обеспокоен, даже если он ничего не говорит", block: 1 },
  { id: 2, text: "Я понимаю скрытые мотивы людей в рабочих ситуациях (почему они предлагают то или иное решение)", block: 1 },
  { id: 3, text: "Я чувствую общее настроение команды на встрече (напряжение, энтузиазм, усталость)", block: 1 },

  // Блок 2: Управление социальными ситуациями (Social Skills)
  { id: 4, text: "Мне легко найти подход к разным типам людей в команде", block: 2 },
  { id: 5, text: "Я знаю, как разрядить напряжённую атмосферу во время конфликта или спора", block: 2 },
  { id: 6, text: "Я быстро адаптируюсь к изменениям групповой динамики (новые участники, смена формата встречи)", block: 2 },

  // Блок 3: Коммуникативная эффективность (Social Processing)
  { id: 7, text: "Я хорошо предвижу, как человек отреагирует на мои слова или предложения", block: 3 },
  { id: 8, text: "Я понимаю невербальные сигналы (жесты, мимику, тон голоса) и учитываю их в общении", block: 3 },
];

const BLOCK_NAMES: Record<number, string> = {
  1: "Понимание эмоций и намерений (Social Awareness)",
  2: "Управление социальными ситуациями (Social Skills)",
  3: "Коммуникативная эффективность (Social Processing)",
};

function SITestingQuestionnairePage() {
  const { teamId, memberId } = useParams<{ teamId: string; memberId: string }>();
  const location = useLocation();
  const navigate = useNavigate();

  const [participant, setParticipant] = useState<ParticipantWithSI | null>(null);
  const [answers, setAnswers] = useState<Record<number, number>>({});
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string>('');

  // Get participant name from navigation state or fetch from API
  const participantName = location.state?.participantName || participant?.name || '';

  useEffect(() => {
    if (memberId) {
      loadParticipant();
    }
  }, [memberId]);

  // Warn before leaving if questionnaire is incomplete
  useEffect(() => {
    const handleBeforeUnload = (e: BeforeUnloadEvent) => {
      const answeredCount = Object.keys(answers).length;
      if (answeredCount > 0 && answeredCount < 8) {
        e.preventDefault();
        e.returnValue = '';
      }
    };

    window.addEventListener('beforeunload', handleBeforeUnload);
    return () => window.removeEventListener('beforeunload', handleBeforeUnload);
  }, [answers]);

  const loadParticipant = async () => {
    try {
      setLoading(true);
      setError('');
      const data = await testingApi.getParticipantSI(Number(memberId));
      setParticipant(data);
    } catch (err) {
      console.error('Failed to load participant:', err);
      setError('Не удалось загрузить данные участника.');
    } finally {
      setLoading(false);
    }
  };

  const handleAnswerChange = (questionId: number, value: number) => {
    setAnswers((prev) => ({
      ...prev,
      [questionId]: value,
    }));
  };

  const calculateScore = (): number => {
    // Formula: (sum / 56) × 100
    // 8 questions × 7 max points = 56
    const sum = Object.values(answers).reduce((acc, val) => acc + val, 0);
    return Math.round((sum / 56) * 100);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (Object.keys(answers).length < 8) {
      alert('Пожалуйста, ответьте на все 8 вопросов перед отправкой.');
      return;
    }

    try {
      setSubmitting(true);
      const score = calculateScore();
      await testingApi.updateSIScore(Number(memberId), score);

      // Navigate to results page with participant info
      navigate('/testing/si/result', {
        state: {
          participantName: participantName || participant?.name || 'Участник',
          score: score,
        },
      });
    } catch (err) {
      console.error('Failed to save SI score:', err);
      alert('Не удалось сохранить результаты. Проверьте подключение и попробуйте снова.');
      setSubmitting(false);
    }
  };

  const handleBack = () => {
    const answeredCount = Object.keys(answers).length;
    if (answeredCount > 0 && answeredCount < 8) {
      const confirmed = window.confirm(
        'У вас есть несохранённые ответы. Вы уверены, что хотите вернуться назад?'
      );
      if (!confirmed) {
        return;
      }
    }
    navigate(`/testing/si/team/${teamId}`);
  };

  if (loading) {
    return (
      <div className="ei-testing-container">
        <div className="loading">Загрузка...</div>
      </div>
    );
  }

  if (error || !participant) {
    return (
      <div className="ei-testing-container">
        <div className="card">
          <h1>Опросник социального интеллекта</h1>
          <div className="error-message">{error || 'Участник не найден.'}</div>
          <button onClick={handleBack} className="btn-secondary">
            ← Назад
          </button>
        </div>
      </div>
    );
  }

  const answeredCount = Object.keys(answers).length;
  const isComplete = answeredCount === 8;
  const progressPercent = (answeredCount / 8) * 100;

  return (
    <div className="ei-testing-container">
      <div className="card questionnaire-container">
        <button onClick={handleBack} className="back-button">
          ← Назад
        </button>

        <h1>Опросник социального интеллекта</h1>
        <p className="participant-subtitle">
          Участник: <strong>{participantName}</strong> ({participant.email})
        </p>

        <div className="instruction">
          Оцените каждое утверждение по шкале от 1 до 7, где 1 — совершенно не согласен,
          4 — нейтрально/иногда, 7 — полностью согласен. Отвечайте честно, здесь нет
          правильных или неправильных ответов.
        </div>

        {/* Progress Bar */}
        <div className="progress-bar">
          <div className="progress-fill" style={{ width: `${progressPercent}%` }} />
          <span className="progress-text">
            {answeredCount} / 8
          </span>
        </div>

        <form onSubmit={handleSubmit} className="questionnaire-form">
          {SI_QUESTIONS.map((question, index) => {
            const isNewBlock = index === 0 || question.block !== SI_QUESTIONS[index - 1].block;

            return (
              <div key={question.id}>
                {isNewBlock && (
                  <h3 className="block-title">Блок {question.block}: {BLOCK_NAMES[question.block]}</h3>
                )}
                <div className="question-item">
                  <p className="question-text">
                    <span className="question-number">{question.id}.</span> {question.text}
                  </p>

                  <div className="radio-group">
                    <span className="scale-label">1 — совершенно не согласен</span>
                    {[1, 2, 3, 4, 5, 6, 7].map((value) => (
                      <label key={value} className="radio-label">
                        <input
                          type="radio"
                          name={`question-${question.id}`}
                          value={value}
                          checked={answers[question.id] === value}
                          onChange={() => handleAnswerChange(question.id, value)}
                        />
                        <span className="radio-value">{value}</span>
                      </label>
                    ))}
                    <span className="scale-label">7 — полностью согласен</span>
                  </div>
                </div>
              </div>
            );
          })}

          <div className="form-actions">
            <button
              type="submit"
              className="btn-primary"
              disabled={!isComplete || submitting}
            >
              {submitting ? 'Сохранение...' : 'Завершить тестирование'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default SITestingQuestionnairePage;
