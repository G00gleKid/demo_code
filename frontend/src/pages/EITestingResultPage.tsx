/**
 * EI Testing Module - Screen 4: Results
 *
 * Public page (no authentication required)
 * Displays completion message and EI score
 *
 * @route /testing/ei/result
 * @temporary Remove when EI integration from external source is implemented
 */

import { useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import './EITesting.css';

function EITestingResultPage() {
  const navigate = useNavigate();
  const location = useLocation();

  // Get data from navigation state
  const participantName = location.state?.participantName;
  const score = location.state?.score;

  // Redirect if no data (direct navigation)
  useEffect(() => {
    if (!participantName || score === undefined) {
      navigate('/testing/ei', { replace: true });
    }
  }, [participantName, score, navigate]);

  const handleTestAnother = () => {
    navigate('/testing/ei');
  };

  // Don't render if no data
  if (!participantName || score === undefined) {
    return null;
  }

  // Determine score category for visual styling
  const getScoreCategory = (score: number): string => {
    if (score >= 80) return 'excellent';
    if (score >= 60) return 'good';
    if (score >= 40) return 'average';
    return 'low';
  };

  const scoreCategory = getScoreCategory(score);

  return (
    <div className="ei-testing-container">
      <div className="card result-display">
        <div className="success-icon">✓</div>

        <h1>Тестирование завершено</h1>

        <p className="result-message">
          Результаты сохранены для участника <strong>{participantName}</strong>
        </p>

        <div className={`score-display score-${scoreCategory}`}>
          <div className="score-label">Ваш балл эмоционального интеллекта:</div>
          <div className="score-value">{score}</div>
          <div className="score-max">из 100</div>
        </div>

        <div className="score-interpretation">
          {score >= 80 && (
            <p>Отличный результат! Высокий уровень эмоционального интеллекта.</p>
          )}
          {score >= 60 && score < 80 && (
            <p>Хороший результат! Развитый эмоциональный интеллект.</p>
          )}
          {score >= 40 && score < 60 && (
            <p>Средний уровень эмоционального интеллекта.</p>
          )}
          {score < 40 && (
            <p>Есть потенциал для развития эмоционального интеллекта.</p>
          )}
        </div>

        <button onClick={handleTestAnother} className="btn-primary">
          Протестировать другого участника
        </button>
      </div>
    </div>
  );
}

export default EITestingResultPage;
