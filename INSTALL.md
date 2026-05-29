# Claude Code Context Monitor - Installation

This adds a status line to the bottom of Claude Code that shows:
- Model name (color-coded by context usage)
- Current directory
- Context usage as a color-coded progress bar with percentage
- Session cost, duration, and lines changed

## Installation

### Step 1: Copy the script

```bash
mkdir -p ~/.claude/scripts
cp context-monitor.py ~/.claude/scripts/context-monitor.py
```

### Step 2: Add the status line config

Run this in your terminal:

```bash
python3 -c "
import json, os
path = os.path.expanduser('~/.claude/settings.local.json')
data = json.load(open(path)) if os.path.exists(path) else {}
data['statusLine'] = {'type': 'command', 'command': 'python3 .claude/scripts/context-monitor.py'}
with open(path, 'w') as f: json.dump(data, f, indent=2)
print('Done!')
"
```

### Step 3: Restart Claude Code

Quit and reopen Claude Code. The status bar should appear at the bottom.

## What you'll see

| Icon | Meaning |
|------|---------|
| Green bar | Under 50% context used |
| Yellow bar | 50-75% context used |
| Orange bar | 75-90% context used |
| Red bar | 90-95% context used |
| Flashing red | 95%+ context used (critical) |

## Troubleshooting

- Make sure `python3` is available on your PATH
- The script reads from Claude Code's transcript file, so it needs a running session to show data
- If you see "???" for context, that's normal on the first message before any usage data exists
