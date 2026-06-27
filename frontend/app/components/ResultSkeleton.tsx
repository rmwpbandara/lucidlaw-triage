/** Placeholder shown while the triage request is in flight. */
export default function ResultSkeleton() {
  return (
    <section className="result skeleton-card" aria-hidden="true">
      <div className="sk sk-eyebrow" />
      <div className="sk sk-title" />
      <div className="sk sk-line" />
      <div className="sk sk-line short" />
      <div className="sk sk-box" />
    </section>
  );
}
