/** Shared types and presentation constants for the triage UI. */

export type Urgency = "low" | "medium" | "high";

export interface TriageResult {
  category: string;
  jurisdiction: string;
  confidence: number;
  urgency: Urgency;
  summary: string;
  suggested_next_step: string;
  escalate_to_professional: boolean;
  needs_clarification: boolean;
  clarifying_question: string | null;
}

/** Friendly, non-technical labels for each category code. */
export const CATEGORY_LABELS: Record<string, string> = {
  tenancy_and_housing: "Tenancy & housing",
  employment: "Work & employment",
  consumer_rights: "Shopping & consumer rights",
  family_law: "Family & relationships",
};

/** Colour and label for each urgency level. */
export const URGENCY_CONFIG: Record<Urgency, { label: string; color: string }> = {
  low: { label: "Low urgency", color: "#3a8a6b" },
  medium: { label: "Medium urgency", color: "#b8862f" },
  high: { label: "Time-sensitive", color: "#c0492b" },
};

/** The five example situations (the brief's required test inputs). */
export const EXAMPLES: string[] = [
  "My landlord in Adelaide is refusing to return my bond even though I left the place clean. It's been 6 weeks.",
  "I was made redundant last week with no notice and they haven't paid out my leave. I've worked there for four years.",
  "I bought a laptop three months ago and the screen has completely failed. The store is refusing to refund or replace it.",
  "My partner and I are separating. We have two kids and we can't agree on where they'll live.",
  "Someone keeps parking in my driveway and I can't get them to stop.",
];
