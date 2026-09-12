# Approaches that improve on Karpathy's LLM-wiki lint pattern

Research note for [issue #58](https://github.com/bmoo/dm-skills/issues/58),
part of the OKF v0.2 wiki-scaffold upgrade
([#56](https://github.com/bmoo/dm-skills/issues/56)). Written 2026-09-12.

**Question.** Karpathy's LLM-wiki gist describes a periodic lint pass over an
agent-maintained markdown wiki. What later write-ups, tools, and papers refine
that pass, and which of their techniques should the dm-skills campaign-wiki
groomer adopt? The groomer's first release auto-fixes links, frontmatter, and
indexes and *reports* contradictions, stale pages, orphans, promotion
candidates, and rebuild-test violations (map issue #56, standing decisions).

**Compared against.** The personal-wiki groomer at
`~/dev/personal/.claude/skills/lint/SKILL.md` (auto-fix checks AF1–AF5, flag
checks F1–F7) and dm-skills' verification vocabulary in `CONTEXT.md`
(mechanical check, completion criterion, fresh check).

**Method.** Primary sources fetched directly where possible (the gist's raw
text, tool READMEs and skill files, specs, arXiv abstracts and HTML). Where a
claim rests on a secondary write-up, the note says so (§7).

---

## 1. What the original actually says

Source: Karpathy, *llm-wiki.md*, gist created **2026-04-04** —
<https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f> (raw:
<https://gist.githubusercontent.com/karpathy/442a6bf555914893e9891c11519de94f/raw>).
The accompanying X post "LLM Knowledge Bases" is
<https://x.com/karpathy/status/2039805659525644595> (2026-04-03; not
fetchable). The ticket's "mid-2025" dating is off by a year.

Three layers, verbatim: raw sources "are immutable — the LLM reads from them
but never modifies them. This is your source of truth"; the wiki, which "the
LLM owns … entirely"; and the schema (`CLAUDE.md`/`AGENTS.md`) that "you and
the LLM co-evolve … over time."

The lint paragraph in full:

> Periodically, ask the LLM to health-check the wiki. Look for: contradictions
> between pages, stale claims that newer sources have superseded, orphan pages
> with no inbound links, important concepts mentioned but lacking their own
> page, missing cross-references, data gaps that could be filled with a web
> search. The LLM is good at suggesting new questions to investigate and new
> sources to look for. This keeps the wiki healthy as it grows.

Load-bearing details for this ticket:

- Six named findings: contradictions, superseded claims, orphans, missing
  pages for mentioned concepts, missing cross-references, data gaps.
- **Staleness is defined relative to sources, not the clock**: "stale claims
  that *newer sources* have superseded." No date or frontmatter policy; the
  only frontmatter mention is that Dataview can table it if present.
- **Silent on auto-fix versus flag.** The verbs are "health-check" and "look
  for". The only fix/flag language is at ingest: "noting where new data
  contradicts old claims … The contradictions have already been flagged."
- **No rebuild/regenerate statement.** Raw is the source of truth, but the
  gist never says the wiki is re-derivable from it; that phrasing belongs to
  derivatives.
- `index.md` is "content-oriented … each page listed with a link, a one-line
  summary"; `log.md` is "chronological … an append-only record" with a
  prefix convention `## [2026-04-02] ingest | Article Title`.
- Human stance: "You never (or rarely) write the wiki yourself" but "I prefer
  to ingest sources one at a time and stay involved — I read the summaries,
  check the updates, and guide the LLM."
- Graph: "Obsidian's graph view is the best way to see the shape of your wiki
  — what's connected to what, which pages are hubs, which are orphans." Scale
  claim: "~100 sources, ~hundreds of pages."

HN threads: <https://news.ycombinator.com/item?id=47640875>,
<https://news.ycombinator.com/item?id=47963913>. One commenter notes that
contradiction lint across N pages is N×N — the scoping problem every
successor has to solve. The often-cited field report — a 200K-line Go
codebase whose first compile surfaced ten real contradictions in existing docs
(Ivanchenko, <https://medium.com/@oleg.a.ivanchenko/i-built-an-llm-wiki-for-a-200k-line-go-codebase-heres-what-happened-e114e7a90560>)
— is verifiable only via secondary summaries (§7).

## 2. Successors and what each adds over the gist

| Successor | What it adds | Source |
|---|---|---|
| **Open Knowledge Format v0.2** (the scaffold's target) | Makes the staleness inputs first-class: `generated: {by, at}` marks "the content's last meaningful change. Consumers use it to tell a recent edit from a stale fact" (§5.2); `verified[]` "independent of `generated.at`" (§5.3); `status: draft\|stable\|deprecated` (§5.4); `stale_after` "an absolute instant … stale when `now >= stale_after` … not a relative TTL, keeps the staleness decision a plain comparison" (§5.5); `sources[].last_modified` "a recency signal, distinct from `generated.at`" (§6). Validation is minimal by design. | <https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md>; FAQ <https://okf.md/faq/> |
| "Don't store trust, derive it" (Boffo, 2026-08-15) | Trust tier computed at read time from OKF fields, never stored: no `verified` → unverified; machine verifiers → machine-confirmed; any `human:` → human-reviewed; `now >= stale_after` → stale, overriding all. "No score, no registry, nothing to keep in sync." | <https://dev.to/scaccogatto/dont-store-trust-derive-it-a-trust-model-for-agent-written-docs-515e> |
| **Hermes Agent `llm-wiki` skill** (Nous Research) | Eleven lint checks: orphans, broken wikilinks, every page in `index.md`, pages >~200 lines → split, required frontmatter incl. `sources`, tags in the `SCHEMA.md` taxonomy, **source drift via SHA256 of raw files**, `contested: true`/`contradictions: [page]` surfaced for review, **stale = page `updated` >90 days older than its newest source**, severity order "broken links > orphans > source drift > contested > stale > style", log rotation at 500 entries. Contradictions: "don't silently overwrite. Note both positions with dates, sources … flag for user review." Page-creation rule: "2+ sources OR is central to one source"; every page links ≥2 others. | <https://hermes-agent.nousresearch.com/docs/user-guide/skills/bundled/research/research-llm-wiki>; <https://github.com/NousResearch/hermes-agent/blob/main/skills/research/llm-wiki/SKILL.md> |
| SamurAIGPT/llm-wiki-agent | Contradictions "flagged at ingest time, not buried until query time"; **missing-entity rule "mentioned in 3+ pages but lacking their own page"**; sparse pages (<2 outbound); "hub stubs & fragile bridges"; a zero-LLM "Health" workflow separate from semantic "Lint". | <https://github.com/SamurAIGPT/llm-wiki-agent/blob/main/AGENTS.md> |
| atomicstrata/llm-wiki-compiler (`llmwiki`) | Source content hashing → pages `fresh`/`stale`/`orphaned`; `refresh --stale` recompiles only pages whose sources changed; generated pages "auto-held for review when confidence, contradiction, schema, or provenance rules trip"; fail-closed. | <https://github.com/atomicstrata/llm-wiki-compiler> |
| nvk/llm-wiki | Two-pass lint: deterministic `scripts/llm-wiki lint --fix` for structure vs agentic `/wiki:lint --deep` that proposes. | <https://github.com/nvk/llm-wiki> |
| praneybehl/llm-wiki-plugin | "Findings are presented as proposed edits — Claude doesn't rewrite your wiki silently"; re-read raw when updating a claim so "a misreading of one source" does not become "an authoritative-looking wiki page"; index sharding ~150 pages. | <https://github.com/praneybehl/llm-wiki-plugin> |
| win4r/llm-wiki-claude-skill | Script lint: orphans, broken/ambiguous wikilinks, unknown tags, empty `sources`, index completeness, >1200 words → split, `invalid_dates`, `low_outbound_links`, `stale_pages`, `case_mismatch_links`. Reported, not fixed. | <https://github.com/win4r/llm-wiki-claude-skill> |
| Astro-Han/karpathy-llm-wiki | Lint = "auto-fixes plus reported issues" for link form, index entries, stale cross-refs. **Deliberately declines** source-hash freshness, per-article review dates, confidence scores ("false precision with no calibration behind it"), and retract machinery: "at 50K–100K tokens of curated wiki, grep and read are more reliable." | <https://github.com/Astro-Han/karpathy-llm-wiki> |
| toolboxmd/karpathy-wiki | Tier-1 lint on every ingest; issues to `.ingest-issues.jsonl`; `doctor` "does not rewrite page bodies"; promotion decisions deferred to a human. | <https://github.com/toolboxmd/karpathy-wiki> |
| Obsidian plugin "Karpathy LLM Wiki" (green-dalii) | "Smart Fix All" shows counts then repairs in causal order (merge duplicates → dead links → link orphans → expand empties); `reviewed: true` pages protected from overwrite; "Create Stubs for Unresolvable Links" is a toggle so dead links can stay visible. | <https://github.com/green-dalii/obsidian-llm-wiki> |
| "LLM Wiki v2" (rohitg00) and "The Schema Is the Product" (cozypet) | Per-fact confidence, Ebbinghaus-style decay, supersession chains ("old version preserved but marked stale"), lint "should automatically fix what it can", contradictions resolved by "source recency, source authority, and the number of supporting observations." "The human stays in the loop for curation and direction. The bookkeeping is fully automated." | <https://gist.github.com/rohitg00/2067ab416f7bbe447c1977edaaa681e2>; <https://cozypet.github.io/llm-wiki-schema/> |
| "Gist Decoded: What I Added" (Ghelbur, 2026-04-29) | Write-back into entity pages; nightly/weekly agents; auto-reconciliation "the most recent, best-sourced, highest-confidence claim wins"; reversibility rule: every scheduled agent "logs its changes to a daily diff note and waits 24 hours before any change becomes permanent." | <https://theaioperator.io/p/i-rebuilt-karpathys-llm-wiki-heres> |
| "LLM Wiki Maintenance: Drift, Contradictions and Review" (Rost, 2026-07-20) | Five drift types (source, terminology, decision, citation, structure); `last_reviewed`/`review_after` with cadence by page type; explicit auto-vs-hold list; "Do not let the agent silently resolve contradictions by blending both claims into a vague compromise." | <https://dev.to/rosgluk/llm-wiki-maintenance-drift-contradictions-and-review-4bp1> |
| "What Karpathy's LLM Wiki Is Missing" (Penfield Labs) | Typed links (`@supersedes`, `@contradicts`, 24 relation types) so conflicts are queryable; autonomous linker with human approval. | <https://dev.to/penfieldlabs/what-karpathys-llm-wiki-is-missing-and-how-to-fix-it-1988> |
| **`~/dev/personal` lint skill** (reference groomer) | AF1–AF5: link migration/rewrite, category rebalancing, category creation, frontmatter backfill, index/log/validate. F1–F7: entity-scoped contradictions (25 entities/run, mtime-ranked), stale (mtime >120 days, or contradicted by a newer `log.md` entry), orphans, promotion candidates (150 words or 3 inbound anchor refs), ambiguous wikilinks, basename collisions, broken embeds. `okf-validate.py` separately reports `stale_after`. | `~/dev/personal/.claude/skills/lint/SKILL.md` |

Not found: anything named "wiki groomer"; a Backstage TechDocs or Diátaxis
freshness convention.

## 3. Techniques by axis

### 3.1 Contradiction detection across pages

- **Scope by shared entity, not by page pair.** N×N is the HN objection and
  the reason GraphRAG ships claim extraction *off by default* ("generally
  requires prompt tuning to be useful",
  <https://microsoft.github.io/graphrag/index/methods/>). GraphRAG's shape is
  the useful part: claims are "positive factual statements with an evaluated
  status and time-bounds" stored as rows `(subject_id, object_id, type,
  status ∈ {TRUE, FALSE, SUSPECTED}, start_date, end_date, source_text)`
  (<https://microsoft.github.io/graphrag/index/default_dataflow/>,
  <https://github.com/microsoft/graphrag/blob/main/graphrag/prompts/index/extract_claims.py>).
  The personal groomer's F1 is the cheap version: entity = a page two or more
  pages link to; compare only status, location, role/relationship,
  possession; cap 25 entities per run.
- **Pairwise is not enough, but it is enough for a wiki.** He et al.,
  "Foundations of Global Consistency Checking with Noisy LLM Oracles"
  (2026-01, <https://arxiv.org/html/2601.13600>) prove a fact set can be
  pairwise-consistent yet globally inconsistent and give an O(k log N)
  minimal-unsatisfiable-subset search. Worth knowing; overkill for hundreds
  of pages where the DM resolves conflicts by hand.
- **Hybrid NLI + LLM-judge over candidate pairs.** LegalWiz/ContraGen
  (<https://arxiv.org/html/2510.03418v2>): embedding similarity picks top-5
  candidate pairs, an NLI model and an LLM each score, combined with
  confidence-derived weights; six-type taxonomy (temporal, numerical,
  authority, process, policy reversal, specificity); ~90% accuracy. The
  taxonomy is reusable as report vocabulary even without the classifier.
- **Ask the grader to find and quote, not to answer through.** WikiContradict
  (NeurIPS 2024, <https://arxiv.org/abs/2406.13805>): given two contradictory
  passages "all models struggle … especially for implicit conflicts requiring
  reasoning"; explicitly prompting attention to contradiction raised one
  model from 10.4% to 43.8%. ContraDoc (<https://arxiv.org/abs/2311.09182>)
  and Tan et al. 2026 (<https://arxiv.org/abs/2601.02627>) agree that
  self-contradiction detection is "still unreliable" and benefits from
  evidence-extraction prompting. Every successor that reports contradictions
  quotes both sides verbatim — the gist, Hermes, F1's report format.
- **Tag, then discuss; never resolve in the tagger.** Wikipedia's maintenance
  templates are the mature human precedent: `{{Contradicts others|A|B}}`,
  `{{Self-contradictory}}`, `{{Contradict-inline}}`, `{{Inconsistent}}` file
  the article into a tracking category and tell the tagger to open a
  talk-page section (<https://en.wikipedia.org/wiki/Template:Contradicts_other>,
  <https://en.wikipedia.org/wiki/Template:Self-contradictory>). WikiContradict
  was built from those tags. Hermes's `contested: true` and Penfield's
  `@contradicts` link are the same mechanism in YAML and in link syntax.
- **Automatic resolution by recency/authority** (rohitg00, Ghelbur; Mem0's
  ADD/UPDATE/DELETE/NOOP, <https://arxiv.org/html/2504.19413v1>) is the
  memory-system answer, where the newest observation of a fact is by
  construction the best. A documented failure mode is silent deletion of a
  memory still needed
  (<https://dev.to/mukesh_13/mem0-auto-resolves-memory-conflicts-for-you-until-it-silently-deletes-one-you-still-need-4f4m>).
  In a campaign wiki the newer page is frequently *unplayed prep* and the
  older one *played history*; recency is the wrong tiebreaker.
- **Invalidate, don't delete** (Zep/Graphiti). Bi-temporal edges carry
  `t_valid`/`t_invalid`; "the system employs an LLM to compare new edges
  against semantically related existing edges to identify potential
  contradictions" and "invalidate[s] the affected edges by setting their
  t_invalid" (<https://arxiv.org/html/2501.13956>,
  <https://github.com/getzep/graphiti>). The markdown equivalent is
  `status: deprecated` plus a link to the superseding page — which OKF
  already provides.

### 3.2 Staleness keyed to metadata, not mtime

- **The gist keys staleness to sources**, not the clock. mtime is the personal
  groomer's convenience proxy (F2: "file mtime older than 120 days"), and its
  own preamble admits the split: "Recency comes from file modification time …
  page-declared staleness comes from `stale_after`, which `okf-validate.py`
  reports."
- **mtime is unreliable in an agent-written git repo**: a checkout, a bulk
  link migration (AF1), or index regeneration touches every file. The
  personal groomer's AF4 already reaches for `git log -1 --format=%aI`
  when it needs a real date.
- **Three distinct signals, three distinct findings**:
  1. *Declared expiry* — `now >= stale_after` (OKF §5.5). A plain comparison.
  2. *Unreviewed age* — `generated.at` or `verified.at` older than a policy
     window. Precedents: Google's `freshness: { owner, reviewed }` metadata
     that "will send email reminders when the document hasn't been touched
     in, for example, three months" (*SWE at Google* ch. 10,
     <https://abseil.io/resources/swe-book/html/ch10.html>); Giant Swarm's
     `frontmatter-validator` CI checks `NO_LAST_REVIEW_DATE`,
     `INVALID_LAST_REVIEW_DATE`, `REVIEW_TOO_LONG_AGO`, report-only, disabled
     per directory for legacy content
     (<https://github.com/giantswarm/frontmatter-validator>); Mintlify's "flag
     pages without updates in over 90 days"
     (<https://www.mintlify.com/docs/guides/maintenance>); docdecay's
     owner-email + `STALE_AGE_IN_DAYS` (<https://pypi.org/project/docdecay/>);
     Rost's per-type `review_after` cadence.
  3. *Superseded by a newer source* — Hermes's rule (page >90 days older than
     the newest source mentioning the same entities) plus SHA256 drift;
     llmwiki's content-hash `fresh`/`stale`.
- **What "source" means for a campaign wiki.** There is no `raw/` corpus; the
  sources of a node page are the *played session pages* that touched it, and
  the source of a session is play. So signal 3 becomes: a `stable` node page
  whose `generated.at` is older than a played session page that links to it.
  The personal groomer's F2 half-implements this already ("contradicted by a
  more recent `log.md` entry").
- **Derive the tier, don't store it** (Boffo). The groomer reports stale; it
  never writes a `stale: true` field that can itself go stale.

### 3.3 Link-graph health

- **Broken links: mechanical, offline, report-only.** `remark-validate-links`
  checks local files and headings in a git repo, offline, and "the tree is
  not modified" (<https://github.com/remarkjs/remark-validate-links>);
  `markdown-link-check` adds HTTP liveness
  (<https://github.com/tcort/markdown-link-check>). Neither detects orphans;
  that needs the inbound graph the personal groomer's F3 builds.
- **Orphan definitions vary; pick one and say it.** Obsidian's graph "Orphans"
  filter "toggles whether to show notes without any links" — no inbound *and*
  no outbound
  (<https://github.com/obsidianmd/obsidian-help/blob/master/en/Plugins/Graph%20view.md>).
  Foam: "no inbound nor outbound links"; placeholders are dangling links
  (<https://github.com/foambubble/foam>). Logseq: "without backlinks"
  (<https://github.com/logseq/logseq/issues/5382>). Wikipedia: "no links from
  other pages in the main article namespace"; the tag once required three
  inbound links, now "a single, relevant incoming link is sufficient … three
  or more … will help ensure the article is reachable"
  (<https://en.wikipedia.org/wiki/Wikipedia:Orphan>). The gist and every
  LLM-wiki successor use *no inbound*. Inbound-only is right for a wiki with
  a generated catalog: a page reachable only from `index.md` is discoverable
  but unintegrated, which is what is worth flagging.
- **The catalog is not a link.** Hermes and win4r check index membership as a
  separate finding; the scaffold's `wiki-index.py --check` already reports
  stale index files. Keeping index membership mechanical and orphanhood
  body-link-only means index regeneration cannot mask an orphan.
- **Sparse pages and fragile bridges.** SamurAIGPT and win4r flag pages with
  <2 outbound links and single-link bridges; Hermes requires ≥2 outbound.
  Cheap graph metrics, but for a campaign wiki a node with one outbound link
  is normal (a minor NPC → their faction), so the signal is weak.
- **Auto-fixing links.** The personal groomer's AF1 rewrites wikilink *form*,
  rewrites *paths* after moves, and *strips* unresolvable links to plain
  text. The last is destructive: an unresolved link is the gist's own
  "important concept mentioned but lacking its own page" finding, and the
  Obsidian plugin makes stub-creation-for-dead-links a toggle precisely so the
  signal stays visible. Successors that auto-fix links fix form and path,
  not targets.
- **Structure notes / MOCs** (Zettelkasten "three layers",
  <https://zettelkasten.de/posts/three-layers-structure-zettelkasten/>; Milo's
  "resist creating MOCs preemptively",
  <https://obsidian.rocks/maps-of-content-effortless-organization-for-notes/>)
  argue that hub pages are created on demand at a felt "squeeze point", not
  by a threshold — which supports the map's decision to leave category
  rebalancing out of the groomer.

### 3.4 Stub promotion thresholds

- The gist names the finding with no number. Successors converge on small
  integers: SamurAIGPT "mentioned in 3+ pages"; Hermes "2+ sources OR central
  to one source", never for "passing mentions"; toolboxmd defers the decision
  to a human. Split thresholds from the other side: Hermes ~200 lines, win4r
  1200 words, Wikipedia's article-size guide (>8,000 words "may need"
  dividing; <150 words for two months "consider merging",
  <https://en.wikipedia.org/wiki/Wikipedia:Article_size>).
- Wikipedia's split rule is notability, not size: the new topic must stand
  on its own (<https://en.wikipedia.org/wiki/Wikipedia:Splitting>,
  <https://en.wikipedia.org/wiki/Wikipedia:Stub>). Zettelkasten atomicity is
  the same idea — one knowledge building block per note, "a guiding compass,
  not a rigid law" (<https://zettelkasten.de/atomicity/guide/>).
- The scaffold's `wiki-schema.md` already fixes ~150 words, three referring
  pages, or the DM says so, and the personal groomer's F4 mechanises the
  first two as report-only ("the linter never auto-creates the page"). No
  successor auto-promotes stubs.
- The campaign rule no general successor has: "Session-bound content never
  earns its own node page, regardless of size." A promotion candidate must
  also pass the *life beyond the session* test — judgement, not counting.

### 3.5 Human-in-the-loop: flag versus auto-fix

Every mature tool draws the same line independently:

| Auto-apply | Flag only |
|---|---|
| Link *form* (wikilink → markdown path) and *path* after a rename | Link *target* when unresolved or ambiguous |
| Frontmatter backfill from evidence already on the page or in git | Any field that asserts a fact (`verified`, `stale_after`, `status`) |
| Files that are pure functions of frontmatter (`index.md`, catalog) | Prose |
| Log append | Contradiction resolution, promotion, deletion, renames |

Sources: Rost's explicit lists (auto: "broken links, formatting cleanup, typo
correction"; hold: "deletions, canonical page rewrites, security/pricing
claim changes, contradiction resolutions"); nvk's deterministic `--fix` vs
agentic proposals; praneybehl's "proposed edits"; the Obsidian plugin's
count-then-approve batch and `reviewed: true` protection; llmwiki's fail-closed
auto-hold; Ghelbur's 24-hour diff-note delay; `remark-validate-links` and
`frontmatter-validator` report-only by design; Wikipedia's tag-and-discuss
templates; the personal groomer's "collisions are always flagged, never
auto-fixed" and "never resolve" contradictions; OWASP's "require explicit
approval for high-impact or irreversible actions … separate decision-making
from execution"
(<https://cheatsheetseries.owasp.org/cheatsheets/AI_Agent_Security_Cheat_Sheet.html>).

dm-skills' vocabulary makes the line crisper than "auto vs flag": an auto-fix
is a **mechanical check** (`regex`/`parse`/`graph`) whose fix is a pure
function of the page set; a flag is a **judgement row** graded by a **fresh
check** against the schema's completion criteria. If the fix cannot be
written as a deterministic script, it is not an auto-fix.

### 3.6 Regeneration / rebuild discipline

- **Raw is immutable; the wiki is derived** (gist). Successors make the
  dependency explicit: Hermes hashes raw files; llmwiki recompiles only
  pages whose source hash changed; GraphRAG's `update` writes to a separate
  `update_output` so the original index is preserved
  (<https://microsoft.github.io/graphrag/cli/>); OKF offers
  `sources[].resource` and `last_modified`. Astro-Han declines all of it at
  small scale. The map has the `sources` family out of scope, and the
  campaign wiki has no `raw/` corpus, so hash-drift has no input here.
- **The scaffold's "rebuild test" is a different discipline** and the
  campaign wiki's real regeneration rule
  (`lib/wiki-scaffold/template/wiki-schema.md`, "The rebuild test"): content a
  session build would *produce* (rosters, XP budgets, boxed text) lives only
  on the unplayed session page; a node holds what a rebuild would *read*. No
  successor implements anything like it. Its corollary — "node pages never
  link into an unplayed session's page" — is the one part that is a graph
  check: an inbound link from `nodes/**` to a `sessions/**` page with
  `status: draft` is mechanically detectable. Whether prose on a node page
  *is* rebuild output is a judgement row.
- **Idempotence.** A lint run applied twice must produce no second diff. The
  personal groomer gets this by regenerating indexes from frontmatter rather
  than editing them, and by running `okf-validate.py` last so "a lint run
  must never leave the bundle non-conformant." `wiki-index.py --check` gives
  the same property as a CI gate. Boffo's derived-trust rule is the same
  principle applied to metadata.

## 4. Gap analysis against the personal groomer

| Personal groomer | Successor technique | Verdict for the campaign groomer |
|---|---|---|
| F2 stale = mtime >120 days | OKF `stale_after` + `generated.at`; Google/Giant Swarm review windows; Hermes newer-source rule | **Replace.** mtime is wrong in an agent-written git repo. |
| F1 ranks entities by mtime | rank by `generated.at` of referring pages | **Replace** the ranking key; keep the entity-scoped shape, four fields, 25-entity cap. |
| AF1 strips unresolvable links to plain text | gist's "missing concept" finding; Obsidian plugin's toggle | **Change to flag.** An unresolved link is a missing-page signal, not garbage. |
| AF2/AF3 category rebalancing and creation | Zettelkasten/MOC "on demand" argument | **Drop**, per the map's standing decision. |
| F4 promotion (150 w / 3 inbound) | same thresholds in `wiki-schema.md`; SamurAIGPT 3+ mentions | **Keep**; add the session-bound exclusion as a criterion the fresh check grades. |
| F3 inbound-only orphans with exemptions | Hermes index-membership as separate finding | **Keep**; add index membership as a separate mechanical finding. |
| No rebuild-test check | scaffold's own link rule | **Add** the node → unplayed-session graph check. |
| Contradiction resolution never automated | rohitg00/Ghelbur auto-resolve | **Keep flag-only.** |
| Contradiction survives only in the report | Hermes `contested`/`contradictions:`; Wikipedia tags | **Defer.** The kernel-plus-`stale_after` target has no such field; the report is the marker until the DM writes `status: deprecated` on the loser. |
| F5–F7 (ambiguous wikilinks, basename collisions, broken embeds) | universal | **Keep** as mechanical flags. |

## 5. Recommendations

**Adopt in the first release:**

1. **Three staleness findings, none keyed to mtime.** (a) `now >=
   stale_after` — mechanical, already in the `okf-validate.py` lineage. (b) A
   `status: stable` node page whose `generated.at` (or newest `verified.at`)
   is older than a configurable review window; default it to a season of
   play, not 120 days, and let the schema exempt page types the way Giant
   Swarm exempts legacy directories. (c) A node page whose `generated.at` is
   older than a *played* session page that links to it. Report each under its
   own name so the DM knows which to act on.
2. **Entity-scoped, quoted contradictions**, F1's shape (entity = a page two
   or more pages link to; status, location, role/relationship, possession;
   verbatim claim pairs), ranked by `generated.at` and capped per run. Prompt
   the grader to *find and quote*, never to reconcile. Never resolve.
3. **Link auto-fix limited to form and path** (wikilink → markdown,
   URL-encoding, path rewrite after a rename the DM made). **Unresolvable
   links are flagged** as missing-page candidates, not stripped.
4. **Orphans = no inbound body link**, exempting reserved files, seed inboxes,
   and `sessions/**` (a session is reachable from the log and nodes are
   forbidden to link into unplayed ones). Report index membership as a
   separate mechanical finding.
5. **Promotion candidates** at the schema's thresholds (150 words, three
   referring pages), report-only, with the session-bound exclusion stated as
   the completion criterion the fresh check grades.
6. **Rebuild-test violation** as a graph check: any link from `nodes/**` into
   a `sessions/**` page carrying `status: draft`. Prose-level rebuild output
   on node pages stays a judgement row.
7. **Auto-fix means a deterministic script.** Frontmatter backfill uses only
   evidence on the page or in git (`title` from H1, `generated.at` from `git
   log -1 --format=%aI`, `generated.by` from the schema's actor rule). The
   groomer never invents `status`, `stale_after`, or `verified`.
8. **Idempotence gate**: run the scaffold checker last; a run that leaves the
   bundle non-conformant fails. Append one line to `log.md`.

**Recommend against:**

- **Auto-resolving contradictions by recency or authority** (rohitg00,
  Ghelbur, Mem0-style UPDATE/DELETE). In a campaign wiki the newest page is
  frequently unplayed prep; recency is anti-correlated with truth until the
  session is played.
- **Per-claim confidence scores or forgetting curves** (rohitg00, cozypet).
  Astro-Han's objection holds here: "false precision with no calibration
  behind it." OKF's `verified` already encodes the one trust distinction that
  matters (DM-confirmed or not) and the map has it out of scope.
- **Content-hash source drift** (Hermes, llmwiki). No `raw/` corpus, and the
  `sources` family is out of scope; recommendation 1(c) is the
  domain-appropriate equivalent.
- **Unsolicited synthesis pages, write-back, and scheduled write passes**
  (Ghelbur). The groomer reports; the DM and the writing skills author.
- **Global-consistency MUS search and NLI classifiers** (He et al.,
  LegalWiz). Correct in theory; unnecessary below a thousand pages with a
  human resolving each conflict.
- **Sparse-page / fragile-bridge metrics** (SamurAIGPT, win4r). Weak signal in
  a campaign wiki where one outbound link per minor page is normal.
- **Category rebalancing** (personal AF2/AF3). Excluded by the map; the
  taxonomy is the schema's.
- **Stripping unresolved links** (personal AF1). Destroys a signal the gist
  names as a finding.

## 6. Open question for the spec

Whether the groomer should print, for each contradiction, a ready-to-paste
`status: deprecated` frontmatter line for the page the DM chooses to retire.
It keeps resolution human while making the mechanical follow-up one edit. The
kernel target supports it today; a `contested` field would not.

## 7. What could not be verified

- Karpathy's X post text (x.com and mirrors blocked); its content is relayed
  by the gist and secondary write-ups.
- Ivanchenko's Go-codebase write-up (Medium 403, archive blocked); the "ten
  contradictions" figure comes from
  <https://denser.ai/blog/llm-wiki-karpathy-knowledge-base/>.
- OKF v0.2's release date ("July 2026") is from the FAQ, not the spec.
- No source found for a "wiki groomer", a Backstage TechDocs freshness
  feature, or a Diátaxis freshness convention.
- No successor was found that implements a rebuild test in the scaffold's
  sense; that discipline appears to be original to dm-skills.
