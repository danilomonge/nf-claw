"use client";

import { useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { Check, Copy } from "lucide-react";

function CodeBlock({ children }: { children: string }) {
  const [copied, setCopied] = useState(false);
  const copy = async () => {
    try {
      await navigator.clipboard.writeText(children);
      setCopied(true);
      setTimeout(() => setCopied(false), 1500);
    } catch {
      /* noop */
    }
  };
  return (
    <div className="group relative my-5 overflow-hidden rounded-2xl border border-white/[0.08] bg-ink-950/80">
      <button
        onClick={copy}
        className="absolute right-3 top-3 z-10 inline-flex items-center gap-1.5 rounded-lg border border-white/10 bg-ink-900/80 px-2 py-1 text-xs text-fog-dim opacity-0 transition group-hover:opacity-100 hover:text-fog"
      >
        {copied ? <Check className="h-3.5 w-3.5 text-claw-400" /> : <Copy className="h-3.5 w-3.5" />}
        {copied ? "Copied" : "Copy"}
      </button>
      <pre className="overflow-x-auto px-4 py-4 font-mono text-[13px] leading-relaxed text-fog-muted">
        <code>{children}</code>
      </pre>
    </div>
  );
}

export function Markdown({ content }: { content: string }) {
  return (
    <div className="text-fog-muted [overflow-wrap:anywhere]">
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        components={{
          h1: ({ children }) => (
            <h1 className="mb-6 mt-2 text-balance text-4xl font-semibold tracking-tight text-fog">
              {children}
            </h1>
          ),
          h2: ({ children }) => (
            <h2 className="mb-4 mt-12 border-b border-white/[0.07] pb-3 text-2xl font-semibold tracking-tight text-fog">
              {children}
            </h2>
          ),
          h3: ({ children }) => (
            <h3 className="mb-3 mt-8 text-xl font-semibold text-fog">{children}</h3>
          ),
          h4: ({ children }) => (
            <h4 className="mb-2 mt-6 text-base font-semibold text-fog">{children}</h4>
          ),
          p: ({ children }) => <p className="my-4 leading-relaxed text-fog-muted">{children}</p>,
          a: ({ href, children }) => (
            <a
              href={href}
              target={href?.startsWith("http") ? "_blank" : undefined}
              rel="noreferrer"
              className="font-medium text-claw-300 underline-offset-4 transition hover:text-claw-200 hover:underline"
            >
              {children}
            </a>
          ),
          ul: ({ children }) => (
            <ul className="my-4 space-y-2 pl-5 marker:text-claw-400/60 [list-style:disc]">
              {children}
            </ul>
          ),
          ol: ({ children }) => (
            <ol className="my-4 space-y-2 pl-5 marker:text-fog-dim [list-style:decimal]">
              {children}
            </ol>
          ),
          li: ({ children }) => <li className="leading-relaxed text-fog-muted">{children}</li>,
          blockquote: ({ children }) => (
            <blockquote className="my-5 border-l-2 border-claw-400/40 bg-white/[0.02] py-1 pl-5 text-fog-muted">
              {children}
            </blockquote>
          ),
          hr: () => <div className="my-10 hairline" />,
          strong: ({ children }) => <strong className="font-semibold text-fog">{children}</strong>,
          table: ({ children }) => (
            <div className="my-6 overflow-x-auto rounded-2xl border border-white/[0.07]">
              <table className="w-full text-sm">{children}</table>
            </div>
          ),
          thead: ({ children }) => <thead className="bg-white/[0.03]">{children}</thead>,
          th: ({ children }) => (
            <th className="border-b border-white/[0.07] px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-fog-dim">
              {children}
            </th>
          ),
          td: ({ children }) => (
            <td className="border-b border-white/[0.04] px-4 py-3 align-top text-fog-muted">
              {children}
            </td>
          ),
          code: (props) => {
            const { children, className } = props as {
              children?: React.ReactNode;
              className?: string;
            };
            const isBlock =
              /language-/.test(className ?? "") || String(children).includes("\n");
            if (isBlock) {
              return <CodeBlock>{String(children).replace(/\n$/, "")}</CodeBlock>;
            }
            return (
              <code className="rounded-md border border-white/[0.06] bg-white/[0.05] px-1.5 py-0.5 font-mono text-[0.85em] text-cream">
                {children}
              </code>
            );
          },
          pre: ({ children }) => <>{children}</>,
        }}
      >
        {content}
      </ReactMarkdown>
    </div>
  );
}
