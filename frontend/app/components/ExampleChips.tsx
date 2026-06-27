"use client";

import { EXAMPLES } from "@/lib/types";

interface Props {
  onPick: (text: string) => void;
  disabled?: boolean;
}

/** Short, friendly labels for the example chips. */
const CHIP_LABELS = [
  "Bond not returned",
  "Made redundant",
  "Faulty laptop",
  "Separating, kids",
  "Driveway blocked",
];

export default function ExampleChips({ onPick, disabled }: Props) {
  return (
    <div className="chips" role="group" aria-label="Example situations">
      <span className="chips-label">Try an example:</span>
      {EXAMPLES.map((text, i) => (
        <button
          key={i}
          type="button"
          className="chip"
          onClick={() => onPick(text)}
          disabled={disabled}
        >
          {CHIP_LABELS[i]}
        </button>
      ))}
    </div>
  );
}
