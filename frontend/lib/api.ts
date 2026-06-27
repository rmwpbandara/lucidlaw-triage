/** Typed client for the LucidLaw triage backend. */

import type { TriageResult } from "./types";

const BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

/** Free backend tiers can take a while to wake; allow a generous timeout. */
const TIMEOUT_MS = 45_000;

export class ApiError extends Error {}

export async function triage(description: string): Promise<TriageResult> {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), TIMEOUT_MS);

  try {
    const res = await fetch(`${BASE_URL}/api/triage`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ description }),
      signal: controller.signal,
    });

    if (!res.ok) {
      let detail = `Request failed (${res.status})`;
      try {
        const body = await res.json();
        if (body?.detail) detail = body.detail;
      } catch {
        /* keep the default message */
      }
      throw new ApiError(detail);
    }

    return (await res.json()) as TriageResult;
  } catch (err) {
    if (err instanceof ApiError) throw err;
    if (err instanceof DOMException && err.name === "AbortError") {
      throw new ApiError("That took too long. The server may be waking up — please try again.");
    }
    throw new ApiError("We couldn't reach the service. Please check your connection and try again.");
  } finally {
    clearTimeout(timer);
  }
}
