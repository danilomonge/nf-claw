import Image from "next/image";
import { asset, cn } from "@/lib/utils";

/**
 * The smallest rendition that stays sharp at 2× density. The 3000 px source logo weighs ~3 MB, and
 * with images unoptimized (static export) it was downloaded on every page for a 32 px mark.
 */
export function logoSrc(size: number): string {
  if (size <= 32) return "/brand/logo-64.png";
  if (size <= 64) return "/brand/logo-128.png";
  if (size <= 96) return "/brand/logo-192.png";
  return "/brand/logo-288.png";
}

export function Logo({
  size = 36,
  withText = false,
  className,
}: {
  size?: number;
  withText?: boolean;
  className?: string;
}) {
  return (
    <span className={cn("inline-flex items-center gap-2.5", className)}>
      <span
        className="relative inline-flex shrink-0 items-center justify-center overflow-hidden rounded-xl ring-1 ring-white/10"
        style={{ width: size, height: size }}
      >
        <Image
          src={asset(logoSrc(size))}
          alt={withText ? "" : "nf-claw"}
          width={size}
          height={size}
          priority
          className="h-full w-full object-cover"
        />
      </span>
      {withText && (
        <span className="font-mono text-[15px] font-semibold tracking-tight text-fog">
          nf<span className="text-claw-400">-</span>claw
        </span>
      )}
    </span>
  );
}
