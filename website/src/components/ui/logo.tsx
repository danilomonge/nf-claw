import Image from "next/image";
import { asset, cn } from "@/lib/utils";

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
          src={asset("/nf-claw-logo.png")}
          alt="nf-claw"
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
