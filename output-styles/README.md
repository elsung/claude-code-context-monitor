# Output styles

Drop-in [Claude Code output styles](https://code.claude.com/docs/en/output-styles)
that change **how Claude communicates with you** — its tone and formatting — without
changing how carefully it works.

| Style (`name:`) | What it does |
|---|---|
| **Plain & Clear** | Leads with the point, translates jargon on first use, explains the *why*, keeps it scannable. A good everyday default. |
| **ELI5** | Explain like I'm 5 — tiny words, everyday analogies, very short. |
| **Explain Like I'm 12** | Real terms introduced gently; more depth than ELI5, still very clear. |
| **Busy CEO** | Bottom line up front, bite-sized, decision-ready; details on tap, never a wall. |
| **Aircraft Manual (STE100)** | ASD-STE100 Simplified Technical English — one instruction per sentence, active voice, zero ambiguity. |

## Install

Copy the ones you want into your user-level styles directory:

```bash
mkdir -p ~/.claude/output-styles
cp output-styles/*.md ~/.claude/output-styles/
```

Then **restart Claude Code** (it reads style files at startup) and pick one from
`/config` → *Output style*. The active style appears in the status line as a
`🎨 <name>` badge (see the top-level README).

## ⚠️ Safety: output styles also affect headless `claude -p`

An output style is injected into the system prompt, and **it applies to non-interactive
runs too** — `claude -p "…"` and the Agent SDK, not just the interactive TUI. This is
easy to verify: set a style that says *"begin every reply with BANANA"*, then run
`claude -p "say hello"` — the output starts with `BANANA`.

That matters if you use Claude Code as a **generation engine** (a pipeline that shells
out to `claude -p` to produce work product). If an `outputStyle` is set in any settings
file such a call reads — `~/.claude/settings.json`, or a project
`.claude/settings.local.json` in the directory the call runs from — **it will reshape
that generated output.** An "Aircraft Manual" style could rewrite a screenplay into
one-instruction-per-line prose.

**Safe pattern — scope the style to interactive sessions only:**

- Do **not** put `outputStyle` in any `settings.json` a headless call reads.
- Set it per-launch instead, so it rides only that one interactive process:

  ```bash
  claude --settings '{"outputStyle":"Plain & Clear"}'
  ```

  A tiny shell wrapper makes this ergonomic and keeps generation calls untouched:

  ```bash
  cc() { command claude --settings "{\"outputStyle\":\"${CC_STYLE:-Plain & Clear}\"}" "$@"; }
  # cc            → styled interactive session
  # CC_STYLE=ELI5 cc → a different style, this session only
  ```

Your headless generation calls, being separate processes that don't pass that flag,
stay clean.
