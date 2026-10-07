import { getPipelines } from "@/lib/data";
import type { ParamIndex } from "@/lib/derive";

// Every parameter of every pipeline, as a static file the skills explorer fetches on the first
// search. Embedded in the home page instead, it made that page ~2.9 MB of HTML.
export const dynamic = "force-static";

export function GET() {
  const index: ParamIndex = Object.fromEntries(
    getPipelines().map((p) => [
      p.name,
      p.groups.flatMap((g) => g.parameters.map((x) => [x.name, g.name, x.description] as [string, string, string])),
    ]),
  );
  return Response.json(index);
}
