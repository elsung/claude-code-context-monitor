# Claude Code Context Monitor

A status line script for [Claude Code](https://claude.ai/code) that shows real-time context usage, session cost, duration, and more at the bottom of your terminal.

![Status line example](https://img.shields.io/badge/context-▓▓▓▓░░░░_50%25-yellow)

## What it shows

- Model name (color shifts green → yellow → red as context fills up)
- Current working directory
- Context usage as a color-coded progress bar with percentage
- Session cost, duration, and net lines changed

## Quick install

Give Claude Code this prompt:

> Read INSTALL.md in this folder and follow the steps to set up the context monitor.

Or do it manually — it's just copying one Python file and adding a JSON config line. See [INSTALL.md](INSTALL.md).

## Credits

Made with Claude. May include or reference code from other projects — honestly can't remember the original sources at this point.

## License

MIT — free to use, modify, distribute. No attribution needed. See [LICENSE](LICENSE).
