import type { Metadata } from "next";
import { DocsHub } from "@/components/home/docs-hub";
import { getDocs } from "@/lib/data";

export const metadata: Metadata = {
  title: "Documentation",
  description: "Documentation generated automatically from the repository.",
};

export default function DocsIndexPage() {
  return (
    <div className="pt-20">
      <DocsHub docs={getDocs()} />
    </div>
  );
}
