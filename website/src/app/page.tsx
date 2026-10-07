import { Hero } from "@/components/home/hero";
import { Manifesto } from "@/components/home/manifesto";
import { PipelineUniverse } from "@/components/home/pipeline-universe";
import { LiveStatus } from "@/components/home/activity";
import { SkillsExplorer } from "@/components/home/skills-explorer";
import { ReleaseTimeline, type TimelineItem } from "@/components/home/release-timeline";
import { DocsHub } from "@/components/home/docs-hub";
import { SectionHeading } from "@/components/ui/section-heading";
import {
  getPipelines,
  getRepoMeta,
  getCommits,
  getWorkflows,
  getTimeline,
  getDocs,
  getLiveRuns,
} from "@/lib/data";
import { toSummary, toSkill, categorize, colorForCategory } from "@/lib/derive";

export default async function HomePage() {
  const pipelines = getPipelines();
  const meta = getRepoMeta();
  const summaries = pipelines.map(toSummary);
  const skills = pipelines.map(toSkill);
  // Fetch more commits than ever fit on screen: the Update history panel crops
  // and fades the list to the exact height of the automation column beside it.
  const commits = getCommits(40);
  const workflows = getWorkflows();
  const docs = getDocs();
  const liveRuns = await getLiveRuns();

  // latest release across pinned pipelines
  const dated = [...pipelines]
    .filter((p) => p.releaseDate)
    .sort((a, b) => +new Date(b.releaseDate!) - +new Date(a.releaseDate!));
  const newest = dated[0] ?? pipelines[0];
  const latest = newest
    ? { name: newest.name, pipeline: newest.pipeline, version: newest.version, date: newest.releaseDate }
    : null;

  const catByName = new Map(pipelines.map((p) => [p.name, categorize(p)]));
  const timeline: TimelineItem[] = getTimeline().map((e) => ({
    id: e.id,
    kind: e.kind,
    title: e.title,
    subtitle: e.subtitle,
    date: e.date,
    version: e.version,
    pipeline: e.pipeline,
    accent: e.pipeline ? colorForCategory(catByName.get(e.pipeline) ?? "Other") : "#39D353",
  }));

  return (
    <>
      <Hero meta={meta} latest={latest} />

      <Manifesto pipelines={summaries} />

      <section id="pipelines" className="section container-site">
        <SectionHeading
          eyebrow="The collection"
          title="Pipeline universe"
          description="Every nf-core pipeline in the library, grouped by research domain. Search by name or tool, filter by domain, inspect any pipeline and compare up to four side by side — all driven by the repository."
        />
        <PipelineUniverse pipelines={summaries} />
      </section>

      <section id="skills" className="section container-site">
        <SectionHeading
          eyebrow="What an agent reads"
          title="Skills explorer"
          description="Each pipeline ships one generated skill — the exact run command, inputs, required parameters and the complete reference. Search across skills and every parameter they expose, then drill in."
        />
        <SkillsExplorer skills={skills} />
      </section>

      <LiveStatus
        commits={commits}
        workflows={workflows}
        liveRuns={liveRuns}
        lastUpdate={meta.stats.latestUpdate}
        repo={meta.remote}
      />

      <section id="releases" className="section container-site">
        <SectionHeading
          eyebrow="Versioned history"
          title="Release timeline"
          description="Each pipeline is pinned to a specific nf-core release. This timeline tracks those pinned versions and the library's own milestones — newest first."
        />
        <ReleaseTimeline items={timeline} />
      </section>

      <DocsHub docs={docs} />
    </>
  );
}
