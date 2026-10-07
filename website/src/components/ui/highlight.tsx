import { splitMatch } from "@/lib/utils";

/** `text` with every case-insensitive occurrence of `query` marked. */
export function Highlight({ text, query }: { text: string; query: string }) {
  return (
    <>
      {splitMatch(text, query).map((part, i) =>
        part.hit ? (
          <mark key={i} className="rounded-[3px] bg-claw-400/20 px-px text-claw-100">
            {part.text}
          </mark>
        ) : (
          <span key={i}>{part.text}</span>
        ),
      )}
    </>
  );
}
