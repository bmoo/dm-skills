# Renderer support for bundle-root-relative links

Resolves [issue #59](https://github.com/bmoo/dm-skills/issues/59), part of the
OKF v0.2 upgrade ([#56](https://github.com/bmoo/dm-skills/issues/56)).

OKF v0.2 §6.1 recommends markdown links of the form `[text](/nodes/npcs/x.md)`:
a leading slash, resolved against the bundle root. The decision to conform is
already made. This note establishes, per renderer, whether such a link resolves,
to where, and — where it breaks — the cheapest publish-time rewrite.

Researched 2026-09-12 against Obsidian 1.13.7, GitHub's docs as of that date,
pandoc 3.11, and the sd-campaign `publish.sh` at its then-current HEAD.

## Verdicts at a glance

| Renderer | Bundle root | `[text](/nodes/npcs/x.md)` resolves to | Verdict |
|---|---|---|---|
| Obsidian (markdown link) | vault root | `<vault>/nodes/npcs/x.md` (exact match only) | Works, if the vault is opened at the bundle root; rename/move rewrites drop the slash |
| GitHub file view | repo root (sd-campaign) | `/<owner>/<repo>/blob/<branch>/nodes/npcs/x.md` | Works |
| GitHub file view | `wiki/` (wiki-sd) | `/<owner>/<repo>/blob/<branch>/nodes/npcs/x.md` — outside `wiki/`, 404 | Breaks; needs a rewrite or a relocated bundle root |
| sd-campaign site build (pandoc + `links.lua`) | repo root = site root | `<a href="/nodes/npcs/x.html">` | Works (reproduced) |

## 1. Obsidian

### What the docs say

- The internal-links help page states that "Folder paths start at the vault root
  and use forward slashes (`/`)", with the markdown example
  `[Three laws of motion](Projects/Three%20laws%20of%20motion.md)` — no leading
  slash. It says nothing about a leading `/`.
  Source: <https://obsidian.md/help/links>.
- Settings → Files and links → **New link format** offers *Shortest path when
  possible*, *Relative path to file*, *Absolute path in vault* ("Uses the full
  path from the vault root"). **Use Wikilinks** off makes Obsidian generate
  markdown links instead. **Show all file types** only affects which files are
  linkable, not resolution.
  Source: <https://github.com/obsidianmd/obsidian-help/blob/master/en/User%20interface/Settings.md>.
- *Absolute path in vault* + markdown links generates `[Note](L1folder/L2folder/note.md)`
  — **no leading slash**. Obsidian staff (moderator WhiteNoise) declined to add
  one: "The reason why this is not added is to support nested vaults and it's
  not universally clear if `/` means the root of vault or the root of the
  filesystem".
  Source: <https://forum.obsidian.md/t/start-absolute-path-path-from-vault-folder-with-a-leading-slash/32501/8>;
  same policy for pasted images at
  <https://forum.obsidian.md/t/obsidian-does-not-use-compatible-markdown-links-for-pasted-images/50422>.
- Users in that thread report that when Obsidian updates links on rename/move it
  "will strip this leading '/' character".
  Source: <https://forum.obsidian.md/t/start-absolute-path-path-from-vault-folder-with-a-leading-slash/32501>.

### What the resolver actually does (read from the shipped app)

The public API `MetadataCache.getFirstLinkpathDest(linkpath, sourcePath)` is
documented only as "Get the best match for a linkpath"
(<https://docs.obsidian.md/Reference/TypeScript+API/MetadataCache/getFirstLinkpathDest>).
The algorithm was read from the installed bundle
`~/Library/Application Support/obsidian/obsidian-1.13.7.asar`
(`getLinkpathDest`, lightly de-minified):

```js
getLinkpathDest = function (linkpath, sourcePath) {
  // 1. candidates = files whose basename matches (try "<linkpath>.md" too)
  var n = linkpath.toLowerCase(), base = basename(n), r = uniqueFileLookup.get(base) ...;
  if (!r) return [];
  if (base === n && r.length === 1) return r.slice();          // bare unique name
  var o = dirname(sourcePath).toLowerCase();
  if (n.startsWith("./") || n.startsWith("../")) { /* resolve against o, exact match */ }
  n.startsWith("/") && (n = n.substr(1));                       // <-- leading slash stripped
  for (...) if (file.path.toLowerCase() === n) return [file];   // exact vault-root path
  if (linkpath.startsWith("/")) return [];                      // <-- no fuzzy fallback for "/..."
  /* otherwise: suffix match (path.endsWith(n)), same-directory candidates first */
}
```

So for a markdown link `[x](/nodes/npcs/x.md)`:

- The `/` is stripped and `nodes/npcs/x.md` is matched **exactly** against vault
  paths (`TFile.path`, which is always vault-root-relative with no leading slash —
  see <https://docs.obsidian.md/Reference/TypeScript+API/MetadataCache/resolvedLinks>).
- If that exact path exists, the link resolves — from any source file, regardless
  of folder. This is the behaviour OKF §6.1 wants.
- If it does not exist, the link is unresolved. Leading-slash links get **none**
  of the lenient suffix-matching that slash-less links get, so a typo or a vault
  opened one level too high is a hard miss.
- The vault root must therefore be the bundle root. For sd-campaign that is the
  repo root. For wiki-sd the vault must be opened at `wiki/`; opened at the repo
  root, every `/nodes/...` link fails (exact match against `wiki/nodes/...`).

Two behavioural caveats survive even where it works:

- Obsidian will never *generate* this form, and its rename/move link updating
  rewrites `[x](/nodes/npcs/x.md)` to `[x](nodes/npcs/x.md)` (forum reports
  above). Any lint that requires the slash will fire after every in-Obsidian
  rename. Slash-less `nodes/npcs/x.md` also resolves (exact vault-root match
  first, then suffix match), so accepting both forms on read is cheap.
- Resolution is case-insensitive and by exact path; percent-encoding in the
  target is decoded before lookup.

## 2. GitHub file renderer

### Documented

"GitHub will automatically transform your relative link or image path based on
whatever branch you're currently on, so that the link or path always works. The
path of the link will be relative to the current file. **Links starting with `/`
will be relative to the repository root.** You can use all relative link
operands, such as `./` and `../`."
Source: <https://docs.github.com/en/get-started/writing-on-github/getting-started-with-writing-and-formatting-on-github/basic-writing-and-formatting-syntax#relative-links-and-image-paths-in-readme-files>
(repeated verbatim in
<https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-readmes>).

The rewrite was introduced in 2013
(<https://github.blog/2013-01-31-relative-links-in-markup-files/>). The filter
itself is not open source (github/markup only converts to HTML; html-pipeline no
longer carries a GitHub relative-link filter), so the exact URL shape comes from
user reports: `[x](/)` renders to `https://github.com/<user>/<repo>/blob/<branch>`
(<https://github.com/github/markup/issues/957>,
<https://github.com/github/markup/issues/1502>). A `/`-link is therefore
`/<owner>/<repo>/blob/<branch>/<path>`, never `github.com/<path>`.

### sd-campaign (bundle root = repo root)

`[text](/nodes/npcs/x.md)` anywhere in the repo renders to
`/<owner>/sd-campaign/blob/<branch>/nodes/npcs/x.md`. **Works**, identically
from every file depth. Documented behaviour; no rewrite needed.

### wiki-sd (bundle root = `wiki/`)

`[text](/nodes/npcs/x.md)` in `wiki/npcs/y.md` renders to
`/<owner>/wiki-sd/blob/<branch>/nodes/npcs/x.md` — outside `wiki/`, so a 404.
GitHub offers no way to re-root `/` at a subdirectory. **Breaks.** This follows
directly from the documented sentence; GitHub's docs do not discuss
subdirectory-rooted bundles.

Cheapest fix: GitHub is not a publish target with a build step, so the rewrite
has to happen either in the checked-in files or by relocating the bundle root.

- **Relocate**: move `wiki/*` to the repo root (the sd-campaign layout).
  `campaign.toml` already declares `wiki_root = "wiki"`, so consumers of that
  contract read one value; the git history moves with `git mv`. Zero ongoing cost.
- **Rewrite in place**: if `wiki/` must stay, the committed files must carry
  file-relative links (`../nodes/npcs/x.md`) and the OKF form can only live in a
  generated mirror. That contradicts "conform to the spec in the source", so it
  is the fallback, not the recommendation.

Community caveat, unrelated to the slash: relative links in the root README as
rendered on the repo *homepage* have been reported broken when the link sits
inside a blockquote (<https://github.com/orgs/community/discussions/67750>, no
staff reply). Links in plain paragraphs are fine.

## 3. sd-campaign site build

### Generator

`~/dev/sd-campaign/publish.sh` renders every `*.md` under
`nodes reference story players sessions docs`, plus `README.md`, `log.md` and the
root `index.md`, with:

```
pandoc "$src" --from gfm+yaml_metadata_block --to html5 --standalone \
  --template site-src/template.html --lua-filter site-src/links.lua ...
```

into `site/<same relative path>.html` (`index.md` → `catalog.html`). `site/` is
zipped from inside the directory and served at the root of
`campaign.bradmoore.org` by Amplify manual deploy, so **the bundle root, the
repo root and the site root are the same directory**. The only link-touching
rule in `site-src/links.lua` is:

```lua
function Link(el)
  if not el.target:match("^https?://") then
    el.target = el.target:gsub("%.md#", ".html#"):gsub("%.md$", ".html")
  end
  return el
end
```

It changes the extension and leaves the path shape alone.

### Reproduced

Throwaway test (pandoc 3.11, run from a scratch directory in this worktree, not
in sd-campaign), input:

```
Root [x](/nodes/npcs/x.md) anchor [y](/nodes/npcs/x.md#sec) rel [z](../npcs/x.md) img ![m](/Media/m.png)
```

Output of `pandoc in.md --from gfm+yaml_metadata_block --to html5 --lua-filter ~/dev/sd-campaign/site-src/links.lua`:

```html
<p>Root <a href="/nodes/npcs/x.html">x</a> anchor <a
href="/nodes/npcs/x.html#sec">y</a> rel <a href="../npcs/x.html">z</a>
img <img src="/Media/m.png" alt="m" /></p>
```

`/nodes/npcs/x.html` is a root-absolute URL, and `site/nodes/npcs/x.html` exists
at the site root. **Works**, with anchors preserved. The site already relies on
root-absolute URLs for its own chrome: `site-src/nav.html` links
`/sessions/index.html`, `/catalog.html`; `template.html` links `/favicon.ico`;
`feature-session.py` builds `/sessions/<file>.html`. No rewrite needed.

Two notes for the migration plans rather than blockers:

- `file://` preview breaks root-absolute links (they resolve to the filesystem
  root). `site-src/render-check.sh` already documents this and serves `site/`
  over a throwaway localhost HTTP server for that reason; keep previewing that
  way.
- Today's content uses no leading-slash links at all (a grep of the content
  roots found zero `](/...)` targets; the dominant forms are `../../`, `../npcs/`,
  `../locations/`, and bare sibling names). The build will handle both forms
  during a mixed period, since the filter is shape-agnostic.

## Cheapest publish-time rewrite, where one is needed

Only the GitHub-in-a-subdirectory case fails, and GitHub has no publish step.
For a hypothetical future generator that *does* need to re-root, the rewrite is
one line in the same shape as the existing pandoc filter: in `Link` (and `Image`),
`if el.target:sub(1,1) == "/" then el.target = base .. el.target end`, where
`base` is the served prefix of the bundle root (`""` for sd-campaign). Nothing in
the current sd-campaign build needs it.

## Bottom line

- Leading-slash links are safe for sd-campaign in all three of its renderers
  (Obsidian vault at the repo root, GitHub, the published site).
- They are safe for wiki-sd in Obsidian only if the vault is opened at `wiki/`,
  and they are broken on GitHub unless the bundle moves to the repo root.
- Obsidian will strip the slash on rename; readers of the bundle should accept
  `nodes/npcs/x.md` as well as `/nodes/npcs/x.md` so a rename does not become a
  lint failure.
