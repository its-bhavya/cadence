const STEPS = [
  'Extracting Frames',
  'Detecting Pose',
  'Counting Reps',
  'Classifying Exercise',
  'Generating Instructions',
]

function Progress({ currentStep }) {
  return (
    <div className="progress-stepper">
      {STEPS.map((label, i) => {
        const stepNum = i + 1
        let status = 'pending'
        if (stepNum < currentStep) status = 'complete'
        else if (stepNum === currentStep) status = 'active'

        return (
          <div key={i} className={`progress-step progress-step--${status}`}>
            <div className="progress-step__indicator">
              {status === 'complete' && <span className="checkmark">&#10003;</span>}
              {status === 'active' && <span className="spinner" />}
              {status === 'pending' && <span className="dot" />}
            </div>
            {i < STEPS.length - 1 && (
              <div className={`progress-step__line ${stepNum < currentStep ? 'progress-step__line--filled' : ''}`} />
            )}
            <span className="progress-step__label">{label}</span>
          </div>
        )
      })}

      <style>{`
        .progress-stepper {
          display: flex;
          flex-direction: column;
          gap: 0;
          width: 100%;
          max-width: 300px;
        }

        .progress-step {
          display: grid;
          grid-template-columns: 28px 1fr;
          grid-template-rows: 28px auto;
          column-gap: 12px;
        }

        .progress-step__indicator {
          grid-column: 1;
          grid-row: 1;
          width: 28px;
          height: 28px;
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 14px;
          flex-shrink: 0;
        }

        .progress-step--complete .progress-step__indicator {
          background: #1a1a1a;
          color: #fff;
        }

        .progress-step--active .progress-step__indicator {
          background: #fff;
          border: 2px solid #1a1a1a;
        }

        .progress-step--pending .progress-step__indicator {
          background: #eee;
        }

        .progress-step__label {
          grid-column: 2;
          grid-row: 1;
          align-self: center;
          font-size: 0.95rem;
          color: #888;
        }

        .progress-step--complete .progress-step__label {
          color: #1a1a1a;
          font-weight: 500;
        }

        .progress-step--active .progress-step__label {
          color: #1a1a1a;
          font-weight: 600;
        }

        .progress-step__line {
          grid-column: 1;
          grid-row: 2;
          width: 2px;
          height: 24px;
          background: #ddd;
          justify-self: center;
        }

        .progress-step__line--filled {
          background: #1a1a1a;
        }

        .checkmark {
          font-size: 14px;
          line-height: 1;
        }

        .dot {
          width: 8px;
          height: 8px;
          border-radius: 50%;
          background: #bbb;
        }

        .spinner {
          width: 14px;
          height: 14px;
          border: 2px solid #ddd;
          border-top-color: #1a1a1a;
          border-radius: 50%;
          animation: spin 0.8s linear infinite;
        }

        @keyframes spin {
          to { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  )
}

export default Progress
