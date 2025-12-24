/**
 * EI Testing Module - Screen 3: Questionnaire
 *
 * Public page (no authentication required)
 * 16-question WLEIS form with progress tracking and score calculation
 *
 * @route /testing/ei/team/:teamId/member/:memberId
 * @temporary Remove when EI integration from external source is implemented
 */

import { useState, useEffect } from 'react';
import { useNavigate, useParams, useLocation } from 'react-router-dom';
import { testingApi, ParticipantWithEI } from '../api/testing';
import './EITesting.css';

// WLEIS Questions (16 items, 4 blocks)
const WLEIS_QUESTIONS = [
  // Блок 1: Самооценка эмоций
  { id: 1, text: "Я хорошо понимаю, почему испытываю те или иные чувства", block: 1 },
  { id: 2, text: "Я хорошо осознаю свои эмоции в любой момент времени", block: 1 },
  { id: 3, text: "Я всегда знаю, счастлив ли я или нет", block: 1 },
  { id: 4, text: "Я хорошо чувствую, что именно вызывает у меня определённые эмоции", block: 1 },

  // Блок 2: Оценка эмоций других
  { id: 5, text: "Я хорошо понимаю эмоции людей вокруг меня", block: 2 },
  { id: 6, text: "Я хорошо наблюдаю за эмоциями других людей", block: 2 },
  { id: 7, text: "Я чувствителен к переживаниям и эмоциям других", block: 2 },
  { id: 8, text: "Я хорошо понимаю эмоции своих коллег/друзей", block: 2 },

  // Блок 3: Использование эмоций
  { id: 9, text: "Я всегда ставлю себе цели и стараюсь изо всех сил их достичь", block: 3 },
  { id: 10, text: "Я мотивирую себя, думая о хороших результатах", block: 3 },
  { id: 11, text: "Я мотивирую себя на продуктивную работу", block: 3 },
  { id: 12, text: "Я умею контролировать свой характер и конструктивно решать проблемы", block: 3 },

  // Блок 4: Регуляция эмоций
  { id: 13, text: "Я способен контролировать свой характер, чтобы разумно справляться с трудностями", block: 4 },
  { id: 14, text: "Я довольно хорошо контролирую собственные эмоции", block: 4 },
  { id: 15, text: "Я всегда могу успокоиться, когда сильно злюсь", block: 4 },
  { id: 16, text: "Я отлично контролирую свои эмоции", block: 4 },
];

const BLOCK_NAMES: Record<number, string> = {
  1: "Самооценка эмоций",
  2: "Оценка эмоций других",
  3: "Использование эмоций",
  4: "Регуляция эмоций",
};

function EITestingQuestionnairePage() {
  const { teamId, memberId } = useParams<{ teamId: string; memberId: string }>();
  const location = useLocation();
  const navigate = useNavigate();

  const [participant, setParticipant] = useState<ParticipantWithEI | null>(null);
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
      if (answeredCount > 0 && answeredCount < 16) {
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
      const data = await testingApi.getParticipant(Number(memberId));
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
    const sum = Object.values(answers).reduce((acc, val) => acc + val, 0);
    return Math.round(((sum - 16) / 96) * 100);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (Object.keys(answers).length < 16) {
      alert('Пожалуйста, ответьте на все 16 вопросов перед отправкой.');
      return;
    }

    try {
      setSubmitting(true);
      const score = calculateScore();
      await testingApi.updateEIScore(Number(memberId), score);

      // Navigate to results page with participant info
      navigate('/testing/ei/result', {
        state: {
          participantName: participantName || participant?.name || 'Участник',
          score: score,
        },
      });
    } catch (err) {
      console.error('Failed to save EI score:', err);
      alert('Не удалось сохранить результаты. Проверьте подключение и попробуйте снова.');
      setSubmitting(false);
    }
  };

  const handleBack = () => {
    const answeredCount = Object.keys(answers).length;
    if (answeredCount > 0 && answeredCount < 16) {
      const confirmed = window.confirm(
        'У вас есть несохранённые ответы. Вы уверены, что хотите вернуться назад?'
      );
      if (!confirmed) {
        return;
      }
    }
    navigate(`/testing/ei/team/${teamId}`);
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
          <h1>Опросник эмоционального интеллекта</h1>
          <div className="error-message">{error || 'Участник не найден.'}</div>
          <button onClick={handleBack} className="btn-secondary">
            ← Назад
          </button>
        </div>
      </div>
    );
  }

  const answeredCount = Object.keys(answers).length;
  const isComplete = answeredCount === 16;
  const progressPercent = (answeredCount / 16) * 100;

  return (
    <div className="ei-testing-container">
      <div className="card questionnaire-container">
        <button onClick={handleBack} className="back-button">
          ← Назад
        </button>

        <h1>Опросник эмоционального интеллекта</h1>
        <p className="participant-subtitle">
          Участник: <strong>{participantName}</strong> ({participant.email})
        </p>

        <div className="instruction">
          Оцените, насколько каждое утверждение описывает вас. Отвечайте честно, здесь нет
          правильных или неправильных ответов.
        </div>

        {/* Progress Bar */}
        <div className="progress-bar">
          <div className="progress-fill" style={{ width: `${progressPercent}%` }} />
          <span className="progress-text">
            {answeredCount} / 16
          </span>
        </div>

        <form onSubmit={handleSubmit} className="questionnaire-form">
          {WLEIS_QUESTIONS.map((question, index) => {
            const isNewBlock = index === 0 || question.block !== WLEIS_QUESTIONS[index - 1].block;

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

export default EITestingQuestionnairePage;
