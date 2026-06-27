"use client";

import { CATEGORY_LABELS, URGENCY_CONFIG, type TriageResult } from "@/lib/types";

interface Props {
  result: TriageResult;
}

export default function ResultCard({ result }: Props) {
  const categoryLabel = CATEGORY_LABELS[result.category] ?? result.category;
  const urgency = URGENCY_CONFIG[result.urgency];
  const confidencePct = Math.round(result.confidence * 100);

  return (
    <section className="result" aria-live="polite">
      <div className="result-head">
        <div>
          <p className="result-eyebrow">This looks like</p>
          <h2 className="result-category">{categoryLabel}</h2>
          <p className="result-jurisdiction">{result.jurisdiction}</p>
        </div>
        <span className="badge" style={{ backgroundColor: urgency.color }}>
          {urgency.label}
        </span>
      </div>

      <p className="result-summary">{result.summary}</p>

      <div className="next-step">
        <p className="next-step-label">A good next step</p>
        <p className="next-step-text">{result.suggested_next_step}</p>
      </div>

      {result.needs_clarification && result.clarifying_question && (
        <div className="clarify">
          <p>{result.clarifying_question}</p>
        </div>
      )}

      {result.escalate_to_professional && (
        <div className="escalate">
          <p>
            Because of what&apos;s involved, it&apos;s worth speaking with a professional soon.
            We can connect you with someone who can help.
          </p>
        </div>
      )}

      <div className="confidence">
        <div className="confidence-row">
          <span>How sure we are</span>
          <span>{confidencePct}%</span>
        </div>
        <div className="confidence-track">
          <div className="confidence-fill" style={{ width: `${confidencePct}%` }} />
        </div>
      </div>

      <p className="disclaimer">
        This is general information to help you get started, not legal advice.
      </p>
    </section>
  );
}
