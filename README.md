# Claude Code Context Monitor

A status line script for [Claude Code](https://claude.ai/code) that shows real-time context usage, session cost, duration, and more at the bottom of your terminal.

![Status line example](https://img.shields.io/badge/context-▓▓▓▓░░░░_50%25-yellow)

## What it shows

- Model name (color shifts green → yellow → red as context fills up)
- Current working directory
- Context usage as a color-coded progress bar with percentage **and absolute tokens used out of the model's real context window** (e.g. `412K/1M`)
- Model-aware window sizing — reads the selected model's actual context window from Claude Code (1M models show `/1M`, 200K models show `/200K`); nothing is hard-coded to 200k
- Session cost, duration, and net lines changed
- **Active output style** — a `🎨 <name>` badge when a non-default [output style](output-styles/) is in effect (hidden on the default, so normal sessions stay clean)

## Output styles

This repo also ships a set of ready-to-use [output styles](output-styles/) (Plain & Clear, ELI5, Busy CEO, Aircraft-Manual STE100, and more) that change how Claude *talks to you*. See [output-styles/README.md](output-styles/) for what each does, how to install them, and an important safety note: **output styles also affect headless `claude -p`**, so scope them to interactive sessions if you use Claude Code as a generation engine.

## Quick install

Give Claude Code this prompt:

> Read INSTALL.md in this folder and follow the steps to set up the context monitor.

Or do it manually — it's just copying one Python file and adding a JSON config line. See [INSTALL.md](INSTALL.md).

## Credits

Made with Claude. May include or reference code from other projects — honestly can't remember the original sources at this point.

## License

MIT — free to use, modify, distribute. No attribution needed. See [LICENSE](LICENSE).
