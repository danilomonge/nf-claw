import type { Metadata } from "next";
import { getPipelines } from "@/lib/data";
import { toSummary } from "@/lib/derive";
import { SectionHeading } from "@/components/ui/section-heading";
import { PipelineIndex } from "@/components/pipeline/pipeline-index";

export const metadata: Metadata = {
  title: "Pipelines",
  description: "Every nf-core pipeline in the nf-claw library.",
};

export default function PipelinesIndexPage() {
  const pipelines = getPipelines().map(toSummary);

  return (
    <div className="container-site pb-8 pt-28 md:pt-32">
      <SectionHeading
        as="h1"
        eyebrow="The collection"
        title="All pipelines"
        description={`${pipelines.length} nf-core pipelines, each pinned to a release and documented from source. Search by name or tool, or narrow to a research domain.`}
      />
      <PipelineIndex pipelines={pipelines} />
    </div>
  );
}
