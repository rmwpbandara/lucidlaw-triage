"use client";

interface Props {
  value: string;
  onChange: (value: string) => void;
  onSubmit: () => void;
  loading: boolean;
}

export default function TriageForm({ value, onChange, onSubmit, loading }: Props) {
  const canSubmit = value.trim().length >= 3 && !loading;

  return (
    <div className="form">
      <label htmlFor="situation" className="form-label">
        Tell us what&apos;s going on
      </label>
      <textarea
        id="situation"
        className="textarea"
        placeholder={
          'In your own words \u2014 for example, "My landlord won\u2019t return my bond"\u2026'
        }
        value={value}
        onChange={(e) => onChange(e.target.value)}
        rows={5}
        maxLength={4000}
        disabled={loading}
      />
      <button
        type="button"
        className="btn-primary"
        onClick={onSubmit}
        disabled={!canSubmit}
      >
        {loading ? "Warming things up…" : "Get guidance"}
      </button>
    </div>
  );
}
