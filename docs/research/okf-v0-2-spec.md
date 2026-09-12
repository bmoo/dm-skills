# What OKF v0.2 requires of the kernel, index, log, and links

Research memo for issue #57 (part of #56, upgrading the campaign wiki scaffold
to OKF v0.2). Read from the spec itself on 2026-09-12:
`https://raw.githubusercontent.com/GoogleCloudPlatform/knowledge-catalog/main/okf/SPEC.md`
(1006 lines, header "**Version 0.2**"). Section numbers below are the spec's
own. Secondary sources, read only to find divergences: `~/dev/personal/CLAUDE.md`
("Open Knowledge Format" and "Link conventions" sections),
`~/dev/personal/docs/frontmatter-research.md`, and
`~/dev/personal/scripts/okf-validate.py` (the reference implementation the
personal repo runs).

## Section map (the ticket's numbering is off in one place)

The ticket cites "§9 conformance". In the spec, **§9 is Log files and
conformance is §11**. The full map, so the schema ticket cites correctly:

| Spec § | Subject |
|---|---|
| §2 | Terminology (bundle, concept, concept ID, link, actor, trust tier) |
| §3, §3.1 | Bundle structure; reserved filenames |
| §4.1 | Frontmatter: the required and recommended kernel |
| §4.2 | Body; conventional headings |
| §5 | Timestamp format; §5.1 `sources`; §5.2 `generated`/`verified`; §5.3 trust tiers; §5.4 `status`; §5.5 `stale_after` |
| §6.1 | Links between concepts; §6.2 path-valued fields; §6.3 `references/` |
| §7 | Actor convention |
| §8 | Index files |
| §9 | Log files |
| §10 | Attested Computation (not relevant to a campaign wiki) |
| §11 | Conformance |
| §12 | Versioning and `okf_version` |
| §13 | Changes from v0.1 |

## 1. The kernel: what MUST, what SHOULD (§4.1)

**Required — exactly one key.** `type`: "A short string identifying the kind
of concept." "`type` is the only always-required key; a concept carrying just
`type` is fully conformant (§11)." Type values "are **not** registered
centrally. Producers SHOULD pick values that are descriptive and
self-explanatory; consumers MUST tolerate unknown types gracefully." The spec's
own example values are Title Case with spaces (`BigQuery Table`, `Playbook`,
`Attested Computation`); the spec imposes no case or spelling rule.

**Recommended (no RFC keyword attached; the spec's heading is literally
"Recommended:").**

- `title`: "Human-readable display name. If omitted, consumers MAY derive a
  title from the filename."
- `description`: "A single sentence summarizing the concept. Used by
  `index.md` generators, search snippets, and previews."
- `resource`: "A URI that uniquely identifies the underlying asset the concept
  describes. Absent for concepts that describe abstract ideas."
- `tags`: "A YAML list of short strings for cross-cutting categorization."

**Optional families (§5): "All are optional. Their absence carries meaning:
an unverified concept is distinguishable from a verified one, but is never
rejected (§11)."**

- `generated: { by, at }` (§5.2). `generated.by` is "REQUIRED within
  `generated`. An actor (§7)." `generated.at` is "An ISO 8601 datetime marking
  the content's last meaningful change." So `generated` is optional, but if
  present it MUST carry `by`; `at` is described, not keyworded.
- `verified` (§5.2): "A list of verification events, each with `by` (an actor)
  and `at` (an ISO 8601 datetime)." "A single verifier MAY be written as one
  `{ by, at }` mapping without the list dash. Consumers MUST treat a bare
  mapping as a one-element list." Trust tier (§5.3): no key ⇒ unverified;
  only non-`human:` actors ⇒ machine-confirmed; any `human:<id>` ⇒
  human-reviewed. "Trust tiers are advisory signals, not access control."
- `status` (§5.4): `draft | stable | deprecated`. "Absent `status` ⇒
  `stable`." `deprecated` is "kept for links and history; no longer current."
  No other values are defined, and the key name is now spec-owned.
- `stale_after` (§5.5): "Optional. An absolute instant. A concept is stale when
  `now >= stale_after`." Deliberately not a relative TTL.
- `sources` (§5.1): a list; per entry `resource` is "REQUIRED within an
  entry" and may be "an absolute URL, a bundle-relative path, or a path into a
  `references/` subdirectory" **or** "a population or scope descriptor it
  cannot [follow]". `id` is "Optional... SHOULD be present when the body cites
  the source." Per-claim attribution is a markdown footnote whose label is a
  `sources[].id`; "consumers resolve attribution through the matching entry,
  not by parsing the footnote prose."

**Extensions (§4.1):** "Producers MAY include any additional keys. Consumers
SHOULD preserve unknown keys when round-tripping and MUST NOT reject documents
with unrecognized fields." Campaign-specific keys (`first_seen`, `session_number`,
`party_level`, `aliases`, `date`) are therefore safe.

**Encoding (§4):** "Every concept is a UTF-8 markdown file" with a YAML block
"delimited by `---` on its own line at the start of the file and a closing
`---` on its own line."

**Body (§4.2):** "There are no required body sections." Conventional headings
that "SHOULD be used when applicable": `# Schema`, `# Examples`,
`# Computation`. Every body and index example in the spec uses **H1** (`#`)
for section headings. "Per-claim attribution to external sources uses markdown
footnotes keyed to `sources` entries rather than a body citations list."

## 2. Timestamp and actor formats (§5, §7)

**Timestamps (§5, one sentence, applies to every timestamp-valued key):**
"Every timestamp-valued key in OKF is an ISO 8601 datetime with an explicit
UTC offset, for example `2026-06-30T14:00:00Z`." The spec's examples use `Z`
throughout; a numeric offset (`-07:00`) is equally an "explicit UTC offset".
Date-only values (`2026-06-01`) are not permitted in frontmatter. The one
date-only form in the whole spec is the **log heading** (§9, below).

**Actors (§7):** "Fields that record an identity (`generated.by`,
`verified[].by`) use a single actor convention:"

- `<producer>/<version>` "for agents and tools, for example
  `reference_agent/gemini-2.5-pro`."
- `human:<id>` "for a person, for example `human:ahormati`."
- `process:<id>` "for an automated process, for example
  `process:finance-nightly`."

"Consumers that classify trust (§5.3) key off the `human:` prefix, so
producers MUST use it for hand-authored or human-confirmed content." Note the
§4.4 example writes `generated: { by: human:ahormati, ... }`, so a human may be
the *generator*, not only a verifier. `sources[].author` also uses the actor
convention (§5.1) and the spec's Appendix uses a fourth shape there,
`team:finance-fpa`, which §7 does not define; treat `author` as looser than
`by`.

## 3. Reserved files: exact shapes (§3.1, §8, §9, §12)

**§3.1:** `index.md` and `log.md` "have defined meaning at any level of the
hierarchy and MUST NOT be used for concept documents. All other `.md` files are
concept documents." §3's tree marks both "Optional." §11's first conformance
rule applies to "every non-reserved `.md` file", so reserved files are exempt
from the frontmatter rule.

### `index.md` (§8), quoted in full where it matters

"An `index.md` file MAY appear in any directory, including the bundle root."
Purpose: "progressive disclosure".

"Index files contain no frontmatter, with one exception: a bundle-root
`index.md` MAY carry an `okf_version` key (§12). The body uses one or more
sections, each grouping concepts under a heading:"

```markdown
# Section / Group Heading

* [Title 1](relative-url-1) - short description of item 1
* [Title 2](relative-url-2) - short description of item 2

# Another Section

* [Subdirectory](subdir/) - short description of the subdirectory
```

"Entries SHOULD include the description from the linked concept's
frontmatter. Producers MAY generate `index.md` automatically; consumers MAY
synthesize one on the fly when none is present."

Read literally: sections under headings (level not mandated; example is H1),
`*` bullets, `[Title](url) - description` with a spaced hyphen, subdirectory
entries link to `subdir/`, and the example URLs are **relative**
(`relative-url-1`), not the `/`-form §6.1 recommends for concept links.

### Where `okf_version` is declared (§12)

"Bundles MAY declare the version they target with `okf_version: "0.2"` in a
bundle-root `index.md` frontmatter block (the only place frontmatter is
permitted in an `index.md`). Consumers that do not understand the declared
version SHOULD attempt best-effort consumption rather than refusing the
bundle." The value is a quoted string. Declaring it is MAY, not MUST; a
non-root `index.md` with frontmatter violates §8.

### `log.md` (§9), quoted in full

"A `log.md` file MAY appear at any level of the hierarchy to record the history
of changes to that scope. The format is a flat list of date-grouped entries,
newest first:"

```markdown
# Directory Update Log

## 2026-05-22
* **Update**: Added a BigQuery table reference for [Customer Metrics](/tables/customer-metrics.md).
* **Creation**: Established the [Dataplex Playbook](/playbooks/dataplex.md).

## 2026-05-15
* **Initialization**: Created foundational directory structure.
```

"Date headings MUST use ISO 8601 `YYYY-MM-DD` form. Log entries are prose; the
leading bold word (`**Update**`, `**Creation**`, `**Deprecation**`) is a
convention, not a requirement."

So the only MUST is the heading date form. "Newest first" and "flat list of
date-grouped entries" are stated as *the format* and fall under conformance
rule 3 ("follows the structure in §9"). The example has an H1 title above the
date H2s; nothing says it is required. The spec says nothing about frontmatter
on `log.md` either way (it is exempt from rule 1 as a reserved file; §8's
"no frontmatter" sentence is about index files only).

## 4. Links (§2, §3, §6)

**Bundle and bundle root.** §2: "Knowledge Bundle (or bundle): A
self-contained, hierarchical collection of knowledge documents. The unit of
distribution." §3: "A bundle is a directory tree of markdown files" and a
bundle "MAY be distributed as ... A subdirectory within a larger repository."
The term "bundle root" is used (§3 tree `path/to/bundle/`, §8, §12) but never
separately defined; it is the top of that tree, which need not be the repo
root. **Concept ID (§2)** is "The path of the concept's file within the bundle,
with the `.md` suffix removed."

**§6.1 Links between concepts.** "Concepts MAY link to other concepts using
standard markdown links. Two forms are supported:"

- "**Absolute (bundle-relative):** begins with `/`, interpreted relative to the
  bundle root. This is the **recommended** form because it is stable when
  documents are moved within their subdirectory."
  `See the [customers table](/tables/customers.md) for the join key.`
- "**Relative:** a standard markdown relative path."
  `See the [neighboring concept](./other.md).`

"A link from concept A to concept B asserts a *relationship*. The specific kind
... is conveyed by the surrounding prose, not by the link itself." "Consumers
MUST tolerate broken links: a link whose target does not exist in the bundle is
not malformed; it may simply represent not-yet-written knowledge."

Every link example keeps the `.md` extension. The recommendation is SHOULD-
strength prose ("recommended"), not a MUST; relative links are fully
conformant. Practical consequence for a scaffold: a `/`-form link is resolved
against the *bundle* root, which GitHub and Obsidian will read as the *repo* or
*vault* root, so `/`-form links only render correctly when the bundle root is
the repo root.

**§6.2 Path-valued fields.** `resource`, `sources[].resource`, `computation`,
`executor.resource`, `attester.resource` each accept "an absolute URL", "a
bundle-relative path beginning with `/`", or "a relative path". A
`sources[].resource` may instead be a scope descriptor. No resolution
requirement is stated for any of them.

**§6.3** `references/` is "a naming convention, not a requirement."

**Not specified anywhere in the spec:** image embeds, heading anchors
(`#fragment`), wikilinks, percent-encoding of spaces, link text conventions,
or whether links may target non-`.md` files. Anything the scaffold says about
these is local convention with no OKF standing either way.

## 5. Conformance: the error/warning split (§11)

"A bundle is **conformant** with OKF v0.2 if:

1. Every non-reserved `.md` file in the tree contains a parseable YAML
   frontmatter block.
2. Every frontmatter block contains a non-empty `type` field.
3. Every reserved filename (`index.md`, `log.md`) follows the structure in §8
   and §9 respectively when present."

Those three are the only hard failures. Then: "When the trust, lifecycle,
provenance, or computation families are present, producers SHOULD follow §5
through §10, and consumers:

- MUST treat a bare `verified` mapping as a one-element list (§5.2).
- MUST NOT reject a concept for missing any optional family (§5.3).
- SHOULD derive trust tiers and staleness only from the fields specified here,
  and SHOULD surface, not silently drop, a failing attestation (§10.5)."

"Consumers SHOULD treat all other constraints as soft guidance. In particular,
consumers MUST NOT reject a bundle because of: Missing optional frontmatter
fields. Unknown `type` values. Unknown additional frontmatter keys. Broken
cross-links. Missing `index.md` files."

So a checker that mirrors the spec has exactly three error classes (no
frontmatter, empty `type`, malformed reserved file) and everything else
(timestamp offsets, actor shapes, `status` enum, broken links, missing
recommended fields, legacy `timestamp`) is at most a warning.

## 6. Versioning rules (§12)

Versions are `<major>.<minor>`. Minor bump = "backward-compatible additions
(new optional fields, new conventional section headings)". Major bump "may
make breaking changes (renaming required fields, changing reserved
filenames)." v0.2 calls itself a minor bump "except for two deliberate
breaking changes" (§13).

## 7. v0.1 → v0.2 (§13)

**§13.1 Breaking:**

- "`timestamp` is superseded by `generated.at`. A concept's last content
  change is now recorded as `generated: { by, at }` (§5.2). Consumers MAY fall
  back to a legacy `timestamp` when `generated` is absent."
- "The body `# Citations` list is superseded by `sources`. Provenance moves to
  frontmatter (§5.1). Consumers SHOULD read `sources` and MAY still parse a
  legacy `# Citations` body list for v0.1 documents."

**§13.2 Additive:** `sources` with `author`/`usage_count`/`last_modified` and
the `usage_window` sibling; `generated`, `verified`; `status`, `stale_after`;
the `Attested Computation` type and its keys; the `# Computation` heading; the
actor convention. "Everything else (bundle structure, reserved filenames, the
required `type`, recommended `title`/`description`/`resource`/`tags`,
cross-linking, index files, log files, permissive conformance) is carried
forward unchanged."

Appendix A shows the v0.1 form writing `timestamp: '2026-05-28T22:53:05+00:00'`
(quoted, offset form), so the offset requirement predates v0.2's `generated`.

## 8. Divergences between the spec and the personal repo's restatement

Each item: what the personal repo says, what the spec says, and whether the
gap is a *local rule stricter than spec* (fine, but not "OKF requires") or a
*misreading*.

1. **Link form (CLAUDE.md "One deliberate divergence").** Uses relative links;
   spec recommends the `/` bundle-relative form (§6.1). Documented as
   deliberate, and correct that relative remains conformant. Stricter-local,
   already acknowledged.
2. **`verified` "is a list, even with one entry" (CLAUDE.md).** Spec §5.2: a
   single verifier "MAY be written as one `{ by, at }` mapping". The same
   CLAUDE.md example block then writes the bare mapping form
   (`verified: { by: human:brad, at: ... }`), contradicting its own rule; and
   `frontmatter-research.md` says "`{ by: human:brad, at }` or a list". Local
   rule, internally inconsistent; the validator accepts both.
3. **"Keep [types] lowercase" (CLAUDE.md).** Spec imposes no case rule and
   its own examples are Title Case with spaces (§4.1). Local style, not OKF.
4. **"Every `sources[].id` is cited somewhere in the body ... the validator
   checks both directions" (CLAUDE.md; validator warns on uncited ids).** Spec
   §5.1 only says `id` "SHOULD be present when the body cites the source"; it
   never requires that every id be cited. Stricter-local.
5. **"A `resource` may be ... a path (relative or bundle-relative, and it must
   resolve)" (CLAUDE.md; validator warns on non-resolving paths).** Spec §6.2
   states no resolution requirement for path-valued fields, and §6.1 makes
   broken *links* explicitly tolerated. Stricter-local.
6. **Attested Computation shape (CLAUDE.md): "either a `computation` path, a
   body `# Computation` fence, or an `executor: { resource, receipt }` plus
   `attester`".** Misreading. Spec §10.3: the computation is provided "in one
   of two ways" (inline fence or `computation` path); `executor` and
   `attester` are separate fields describing how to run and check it, not a
   third alternative. The validator encodes the misreading
   (`elif not has_fence and "executor" not in fields`). Irrelevant to a
   campaign wiki, but wrong as a restatement.
7. **`log.md` "must not carry frontmatter" (validator errors; CLAUDE.md says
   both reserved files "carry no frontmatter").** Spec says this only of
   `index.md` (§8, §12); it is silent on `log.md` frontmatter. Stricter-local,
   and the validator makes it a hard *error*, which §11 rule 3 only arguably
   supports.
8. **Index must have at least one heading and one entry (validator errors).**
   §8 describes "one or more sections, each ... under a heading"; an
   entry-less index for an empty directory is not addressed. Stricter-local as
   an error class.
9. **Log labels.** CLAUDE.md fixes `Creation | Update | Removal | Lint`; the
   spec's examples are `Update`, `Creation`, `Deprecation`, `Initialization`
   and it says the bold word "is a convention, not a requirement" (§9). No
   conflict, but the label set is local and the validator's "entry lacks a
   `**Label**:` prefix" is a warning about a non-rule.
10. **`frontmatter-research.md` is stale against the validator it describes.**
    It says the validator "currently warns on anything that isn't `"0.1"`" and
    recommends it "prefer `generated.at` with a `timestamp` fallback"; the
    shipped validator targets `"0.2"` and instead *warns on* any legacy
    `timestamp` (§13.1) with no fallback. The spec's fallback is a consumer
    MAY, so neither reading is a spec violation, but the doc no longer
    describes the tool.
11. **Actor string drift between the two docs.** CLAUDE.md pins
    `claude-code/fable-5.1` (and says to name the model that actually wrote
    it); `frontmatter-research.md` pins `claude-code/opus-5`. Both are valid
    `<producer>/<version>` shapes (§7); pick one policy.
12. **"Every timestamp needs an explicit UTC offset ... never a bare
    `2026-06-01`" (CLAUDE.md).** Correct for frontmatter (§5); note the log
    heading is the spec's own date-only form (§9), so the rule is scoped to
    frontmatter keys.
13. **`date` and `aliases` keys.** Both are producer extensions under §4.1;
    the docs are right that they are safe. `date` is written date-only in the
    personal vault, which is fine because it is not an OKF timestamp-valued
    key.

Nothing in the personal restatement contradicts a spec MUST. The pattern is
that the personal repo's rules are uniformly *stricter* than OKF, and the
docs sometimes attribute local strictness to the spec.

## 9. Context for the schema ticket: where the dm-skills scaffold stands today

`lib/wiki-scaffold/template/wiki-schema.md` (and its copy under
`examples/emberwick-vale/`) currently:

- Reserves `index.md`/`log.md` at every level with no frontmatter on indexes:
  matches §3.1/§8. It does not declare `okf_version` anywhere.
- Recommends `timestamp:` (ISO 8601): the v0.1 key retired by §13.1; the
  v0.2 replacement is `generated: { by, at }` with a REQUIRED actor `by`.
- Uses `status:` with vocabulary `stub | active | canon | retired`: `status`
  is now a spec-owned key whose only defined values are
  `draft | stable | deprecated` (§5.4). Keeping campaign lifecycle under a
  different key name (a producer extension per §4.1) avoids the collision.
- Log shape `## YYYY-MM-DD` / `* **Event-type**: summary`, newest first:
  matches §9; the H1 title in the spec's example is not required.
- Requires `type` to match the directory: a local rule the spec neither
  requires nor forbids (§4.1 types are unregistered).

## Sources

- OKF v0.2 specification, raw:
  `https://raw.githubusercontent.com/GoogleCloudPlatform/knowledge-catalog/main/okf/SPEC.md`
- `~/dev/personal/CLAUDE.md`, sections "Link conventions" and "Open Knowledge
  Format"
- `~/dev/personal/docs/frontmatter-research.md`
- `~/dev/personal/scripts/okf-validate.py`
- `lib/wiki-scaffold/template/wiki-schema.md` in this repo
