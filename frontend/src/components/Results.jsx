function Results({ data }) {
  const {
    exercise_name,
    confidence,
    rep_count,
    muscles_worked,
    skeleton_video_url,
    instructions,
    form_feedback,
  } = data

  const confidenceColor = {
    high: '#16a34a',
    medium: '#ca8a04',
    low: '#dc2626',
  }[confidence] || '#888'

  return (
    <div className="results">
      {/* Header */}
      <section className="results__header">
        <div className="results__title-row">
          <h2 className="results__name">{exercise_name}</h2>
          <span
            className="results__badge"
            style={{ background: confidenceColor }}
          >
            {confidence}
          </span>
        </div>
        <p className="results__reps">{rep_count} reps</p>
        <div className="results__muscles">
          {muscles_worked.map((m, i) => (
            <span key={i} className="results__tag">{m}</span>
          ))}
        </div>
      </section>

      {/* Skeleton Video */}
      {skeleton_video_url && (
        <section className="results__video-section">
          <h3>Pose Overlay</h3>
          <video
            className="results__video"
            src={`/api${skeleton_video_url}`}
            autoPlay
            muted
            loop
            controls
          />
        </section>
      )}

      {/* Instructions */}
      {instructions && instructions.length > 0 && (
        <section className="results__instructions">
          <h3>Instructions</h3>
          <ol className="results__steps">
            {instructions.map((step, i) => (
              <li key={i} className="results__step">
                <span className="results__phase">{step.phase}</span>
                <p className="results__instruction">{step.instruction}</p>
                <p className="results__form-cue">{step.form_cue}</p>
                <p className="results__breathing">{step.breathing}</p>
              </li>
            ))}
          </ol>
        </section>
      )}

      {/* Form Feedback */}
      {form_feedback && form_feedback.length > 0 && (
        <section className="results__feedback">
          <h3>Form Feedback</h3>
          <ul className="results__feedback-list">
            {form_feedback.map((item, i) => (
              <li key={i} className="results__feedback-item">
                <div className="results__feedback-header">
                  <strong>{item.issue}</strong>
                  <span
                    className="results__detect-badge"
                    style={{
                      background: item.detectable_from_pose ? '#dbeafe' : '#f3f4f6',
                      color: item.detectable_from_pose ? '#1d4ed8' : '#6b7280',
                    }}
                  >
                    {item.detectable_from_pose ? 'Pose Detected' : 'General Advice'}
                  </span>
                </div>
                <p className="results__correction">{item.correction}</p>
              </li>
            ))}
          </ul>
        </section>
      )}

      <style>{`
        .results {
          width: 100%;
          max-width: 720px;
          display: flex;
          flex-direction: column;
          gap: 0;
        }

        .results h3 {
          font-size: 1.1rem;
          font-weight: 600;
          margin: 0 0 14px;
          color: #1a1a1a;
        }

        /* Sections get card treatment with visual separation */
        .results__header,
        .results__video-section,
        .results__instructions,
        .results__feedback {
          background: #fff;
          border: 1px solid #e5e5e5;
          border-radius: 12px;
          padding: 24px;
          margin-bottom: 16px;
        }

        /* Header */
        .results__header {
          display: flex;
          flex-direction: column;
          gap: 10px;
        }

        .results__title-row {
          display: flex;
          align-items: center;
          gap: 12px;
          flex-wrap: wrap;
        }

        .results__name {
          font-size: 1.8rem;
          font-weight: 700;
          margin: 0;
          color: #1a1a1a;
          letter-spacing: -0.02em;
        }

        .results__badge {
          padding: 3px 12px;
          border-radius: 20px;
          color: #fff;
          font-size: 0.78rem;
          font-weight: 600;
          text-transform: uppercase;
          letter-spacing: 0.5px;
        }

        .results__reps {
          font-size: 1.15rem;
          color: #555;
          margin: 0;
        }

        .results__muscles {
          display: flex;
          flex-wrap: wrap;
          gap: 6px;
          margin-top: 4px;
        }

        .results__tag {
          padding: 4px 12px;
          border-radius: 6px;
          background: #f3f4f6;
          color: #374151;
          font-size: 0.85rem;
          font-weight: 500;
        }

        /* Video */
        .results__video-section {
          display: flex;
          flex-direction: column;
        }

        .results__video {
          width: 100%;
          border-radius: 8px;
          background: #000;
        }

        /* Instructions */
        .results__steps {
          list-style: none;
          counter-reset: step;
          padding: 0;
          margin: 0;
          display: flex;
          flex-direction: column;
          gap: 20px;
        }

        .results__step {
          counter-increment: step;
          padding-left: 36px;
          position: relative;
          line-height: 1.6;
        }

        .results__step::before {
          content: counter(step);
          position: absolute;
          left: 0;
          top: 1px;
          width: 24px;
          height: 24px;
          border-radius: 50%;
          background: #1a1a1a;
          color: #fff;
          font-size: 0.75rem;
          font-weight: 600;
          display: flex;
          align-items: center;
          justify-content: center;
        }

        .results__phase {
          font-size: 0.75rem;
          font-weight: 600;
          text-transform: uppercase;
          letter-spacing: 0.8px;
          color: #999;
        }

        .results__instruction {
          margin: 2px 0 4px;
          color: #1a1a1a;
        }

        .results__form-cue {
          margin: 0;
          font-style: italic;
          color: #555;
          font-size: 0.9rem;
        }

        .results__breathing {
          margin: 2px 0 0;
          color: #999;
          font-size: 0.85rem;
        }

        /* Form Feedback */
        .results__feedback-list {
          list-style: none;
          padding: 0;
          margin: 0;
          display: flex;
          flex-direction: column;
          gap: 14px;
        }

        .results__feedback-item {
          line-height: 1.6;
          padding: 12px 16px;
          background: #fafafa;
          border-radius: 8px;
          border: 1px solid #eee;
        }

        .results__feedback-header {
          display: flex;
          align-items: center;
          gap: 8px;
          flex-wrap: wrap;
        }

        .results__detect-badge {
          padding: 2px 8px;
          border-radius: 4px;
          font-size: 0.75rem;
          font-weight: 500;
          white-space: nowrap;
        }

        .results__correction {
          margin: 6px 0 0;
          color: #555;
          font-size: 0.9rem;
        }
      `}</style>
    </div>
  )
}

export default Results
