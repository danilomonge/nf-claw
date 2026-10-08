// Geometry for the pipeline constellation: every domain gets a wedge of the disc sized to its
// pipeline count, and its pipelines fill that wedge in rings from the rim inward. The layout always
// fits the view box — however many pipelines there are, the ring spacing shrinks to fit — and it is
// fully deterministic (no randomness, rounded coordinates), so server and client render the same SVG.

export interface Node {
  name: string;
  category: string;
  x: number;
  y: number;
  r: number;
  angle: number;
}

export interface Wedge {
  category: string;
  start: number;
  end: number;
  count: number;
  /** Where the wedge's label sits, just outside the rim. */
  label: { x: number; y: number; anchor: "start" | "middle" | "end" };
  path: string;
}

export interface Constellation {
  width: number;
  height: number;
  cx: number;
  cy: number;
  rInner: number;
  rOuter: number;
  /** Horizontal stretch of the disc. */
  sx: number;
  nodes: Node[];
  wedges: Wedge[];
}

const round = (v: number) => Math.round(v * 100) / 100;

/** A tiny stable hash → [0, 1), used for gentle per-node jitter that is identical on every render. */
function unit(seed: string): number {
  let h = 2166136261;
  for (let i = 0; i < seed.length; i++) {
    h ^= seed.charCodeAt(i);
    h = Math.imul(h, 16777619);
  }
  return ((h >>> 0) % 10000) / 10000;
}

/** Node radius from the parameter count: area grows with the count, within a legible range. */
export function nodeRadius(parameterCount: number): number {
  return round(Math.min(10, Math.max(4.5, 3 + Math.sqrt(Math.max(0, parameterCount)) * 0.5)));
}

export function layoutConstellation(
  items: { name: string; category: string; parameterCount: number }[],
  categoryOrder: string[],
  { width = 800, height = 560 } = {},
): Constellation {
  const cx = width / 2;
  const cy = height / 2;
  const rOuter = Math.min(cx, cy) - 44;
  const rInner = 64;
  // The disc is stretched horizontally to use the wide view box, leaving ~100 units at each side
  // for the wedge labels.
  const sx = Math.max(1, Math.min(1.3, (cx - 100) / (rOuter + 22)));

  const groups = categoryOrder
    .map((category) => ({
      category,
      items: items.filter((i) => i.category === category).sort((a, b) => a.name.localeCompare(b.name)),
    }))
    .filter((g) => g.items.length);
  const total = groups.reduce((n, g) => n + g.items.length, 0) || 1;

  const gap = groups.length > 1 ? 0.07 : 0;
  const usable = Math.PI * 2 - gap * groups.length;
  const nodes: Node[] = [];
  const wedges: Wedge[] = [];
  let angle = -Math.PI / 2 + gap / 2;

  for (const g of groups) {
    const span = (usable * g.items.length) / total;
    const start = angle;
    const end = angle + span;

    // Fill rings from the rim inward; tighten the spacing until the wedge holds every node.
    let rings: { r: number; count: number }[] = [];
    for (let step = 30; step >= 8; step -= 1) {
      rings = [];
      let left = g.items.length;
      for (let r = rOuter; left > 0 && r >= rInner + 6; r -= step) {
        const cap = Math.max(1, Math.floor((span * r) / step));
        const count = Math.min(cap, left);
        rings.push({ r, count });
        left -= count;
      }
      if (left === 0) break;
    }

    let k = 0;
    for (const ring of rings) {
      for (let j = 0; j < ring.count; j++) {
        const item = g.items[k++];
        const jitterA = (unit(item.name) - 0.5) * Math.min(0.06, span / (ring.count + 1) / 3);
        const jitterR = (unit(item.name + "r") - 0.5) * 6;
        const a = start + ((j + 0.5) / ring.count) * span + jitterA;
        const r = ring.r + jitterR;
        nodes.push({
          name: item.name,
          category: g.category,
          x: round(cx + r * Math.cos(a) * sx),
          y: round(cy + r * Math.sin(a)),
          r: nodeRadius(item.parameterCount),
          angle: round(a),
        });
      }
    }

    const mid = (start + end) / 2;
    const lr = rOuter + 22;
    const cos = Math.cos(mid);
    wedges.push({
      category: g.category,
      start: round(start),
      end: round(end),
      count: g.items.length,
      label: {
        x: round(cx + lr * cos * sx),
        y: round(cy + lr * Math.sin(mid) + 4),
        anchor: cos > 0.25 ? "start" : cos < -0.25 ? "end" : "middle",
      },
      path: wedgePath(cx, cy, rInner, rOuter + 10, start, end, sx),
    });
    angle = end + gap;
  }

  return { width, height, cx, cy, rInner, rOuter, sx: round(sx), nodes, wedges };
}

/** An annular sector, stretched by `sx` horizontally (drawn as polylines so the stretch stays exact). */
function wedgePath(cx: number, cy: number, r0: number, r1: number, a0: number, a1: number, sx: number): string {
  const steps = Math.max(4, Math.ceil(((a1 - a0) / (Math.PI * 2)) * 72));
  const pt = (r: number, a: number) => `${round(cx + r * Math.cos(a) * sx)} ${round(cy + r * Math.sin(a))}`;
  const outer: string[] = [];
  const inner: string[] = [];
  for (let i = 0; i <= steps; i++) {
    const a = a0 + ((a1 - a0) * i) / steps;
    outer.push(pt(r1, a));
    inner.push(pt(r0, a1 - ((a1 - a0) * i) / steps));
  }
  return `M ${outer.join(" L ")} L ${inner.join(" L ")} Z`;
}
