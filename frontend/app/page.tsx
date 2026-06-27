"use client";

import { useState } from "react";

import ExampleChips from "./components/ExampleChips";
import ResultCard from "./components/ResultCard";
import ResultSkeleton from "./components/ResultSkeleton";
import TriageForm from "./components/TriageForm";
import { ApiError, triage } from "@/lib/api";
import type { TriageResult } from "@/lib/types";

export default function Home() {
  const [description, setDescription] = useState("");
  const [result, setResult] = useState<TriageResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function handleSubmit() {
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const data = await triage(description);
      setResult(data);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Something went wrong. Please try again.");
    } finally {
      setLoading(false);
    }
  }

  function handlePickExample(text: string) {
    setDescription(text);
    setResult(null);
    setError(null);
  }

  return (
    <main className="page">
      <header className="hero">
        <div className="brand">
          <span className="brand-mark">✦</span>
          <span className="brand-name">LucidLaw</span>
        </div>
        <h1 className="hero-title">Your law. Made easy.</h1>
        <p className="hero-sub">
          Describe what&apos;s going on in plain language. We&apos;ll help you understand your
          situation and point you to a clear first step.
        </p>
        <ul className="hero-trust">
          <li>Private &amp; confidential</li>
          <li>Plain language, no jargon</li>
          <li>For everyday Australians</li>
        </ul>
      </header>

      <ExampleChips onPick={handlePickExample} disabled={loading} />

      <TriageForm
        value={description}
        onChange={setDescription}
        onSubmit={handleSubmit}
        loading={loading}
      />

      {error && (
        <div className="error" role="alert">
          {error}
        </div>
      )}

      {loading && <ResultSkeleton />}

      {result && <ResultCard result={result} />}

      <footer className="page-footer">
        General information only — not legal advice. · A LucidLaw triage prototype.
      </footer>
    </main>
  );
}
