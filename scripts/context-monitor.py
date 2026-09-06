#!/usr/bin/env python3
"""
Claude Code Context Monitor
Real-time context usage monitoring with visual indicators and session analytics
"""

import json
import sys
import os
import re


def humanize_tokens(n):
    """412000 -> '412K', 1000000 -> '1M', 1500000 -> '1.5M'."""
    n = int(n)
    if n >= 1_000_000:
        v = n / 1_000_000
        return f"{v:.0f}M" if v == int(v) else f"{v:.1f}M"
    if n >= 1_000:
        return f"{round(n / 1000)}K"
    return str(n)


def parse_context_from_window(data):
    """Preferred source: the ``context_window`` object Claude Code passes in the
    status-line JSON. It is authoritative and model-aware — ``context_window_size``
    is the SELECTED model's real window (1,000,000 on a 1M model, 200,000 default),
    so nothing here is hard-coded to 200k."""
    cw = data.get("context_window") or {}
    size = cw.get("context_window_size")
    # total_input_tokens == input + cache_creation + cache_read (matches used_percentage).
    tokens = cw.get("total_input_tokens")
    percent = cw.get("used_percentage")

    if percent is None and tokens and size:
        percent = (tokens / size) * 100
    if percent is None:
        return None

    return {
        "percent": max(0, min(100, percent)),
        "tokens": tokens,
        "window": size,
        "method": "window",
    }


def parse_context_from_transcript(transcript_path, window=200000):
    """Fallback for older Claude Code schemas that don't send ``context_window``.

    ``window`` is the model's real context size when the caller knows it; it only
    falls back to 200000 as a last resort (which would understate a 1M model)."""
    if not transcript_path or not os.path.exists(transcript_path):
        return None

    window = window or 200000
    try:
        with open(transcript_path, 'r', encoding='utf-8', errors='replace') as f:
            lines = f.readlines()

        # Check last 15 lines for context information
        recent_lines = lines[-15:] if len(lines) > 15 else lines

        for line in reversed(recent_lines):
            try:
                data = json.loads(line.strip())

                # Method 1: Parse usage tokens from assistant messages
                if data.get('type') == 'assistant':
                    message = data.get('message', {})
                    usage = message.get('usage', {})

                    if usage:
                        input_tokens = usage.get('input_tokens', 0)
                        cache_read = usage.get('cache_read_input_tokens', 0)
                        cache_creation = usage.get('cache_creation_input_tokens', 0)

                        # Estimate context usage against the model's real window.
                        total_tokens = input_tokens + cache_read + cache_creation
                        if total_tokens > 0:
                            percent_used = min(100, (total_tokens / window) * 100)
                            return {
                                'percent': percent_used,
                                'tokens': total_tokens,
                                'window': window,
                                'method': 'usage'
                            }

                # Method 2: Parse system context warnings
                elif data.get('type') == 'system_message':
                    content = data.get('content', '')

                    # "Context left until auto-compact: X%"
                    match = re.search(r'Context left until auto-compact: (\d+)%', content)
                    if match:
                        percent_left = int(match.group(1))
                        return {
                            'percent': 100 - percent_left,
                            'warning': 'auto-compact',
                            'method': 'system'
                        }

                    # "Context low (X% remaining)"
                    match = re.search(r'Context low \((\d+)% remaining\)', content)
                    if match:
                        percent_left = int(match.group(1))
                        return {
                            'percent': 100 - percent_left,
                            'warning': 'low',
                            'method': 'system'
                        }

            except (json.JSONDecodeError, KeyError, ValueError):
                continue

        return None

    except (FileNotFoundError, PermissionError):
        return None


def get_context_display(context_info):
    """Generate context display with visual indicators."""
    if not context_info:
        return "🔵 ???"

    percent = context_info.get('percent', 0)
    warning = context_info.get('warning')

    # Color and icon based on usage level
    if percent >= 95:
        icon, color = "🚨", "\033[31;1m"  # Blinking red
        alert = "CRIT"
    elif percent >= 90:
        icon, color = "🔴", "\033[31m"    # Red
        alert = "HIGH"
    elif percent >= 75:
        icon, color = "🟠", "\033[91m"   # Light red
        alert = ""
    elif percent >= 50:
        icon, color = "🟡", "\033[33m"   # Yellow
        alert = ""
    else:
        icon, color = "🟢", "\033[32m"   # Green
        alert = ""

    # Create progress bar
    segments = 8
    filled = int((percent / 100) * segments)
    bar = "█" * filled + "▁" * (segments - filled)

    # Special warnings
    if warning == 'auto-compact':
        alert = "AUTO-COMPACT!"
    elif warning == 'low':
        alert = "LOW!"

    reset = "\033[0m"
    alert_str = f" {alert}" if alert else ""

    # Absolute usage (e.g. '412K/1M') when the counts are present.
    tokens = context_info.get('tokens')
    window = context_info.get('window')
    tokens_str = ""
    if tokens and window:
        tokens_str = f" \033[90m·\033[0m {humanize_tokens(tokens)}/{humanize_tokens(window)}"

    return f"{icon}{color}{bar}{reset} {percent:.0f}%{tokens_str}{alert_str}"

def get_directory_display(workspace_data):
    """Get directory display name."""
    current_dir = workspace_data.get('current_dir', '')
    project_dir = workspace_data.get('project_dir', '')

    if current_dir and project_dir:
        if current_dir.startswith(project_dir):
            rel_path = current_dir[len(project_dir):].lstrip('/')
            return rel_path or os.path.basename(project_dir)
        else:
            return os.path.basename(current_dir)
    elif project_dir:
        return os.path.basename(project_dir)
    elif current_dir:
        return os.path.basename(current_dir)
    else:
        return "unknown"

def get_session_metrics(cost_data):
    """Get session metrics display."""
    if not cost_data:
        return ""

    metrics = []

    # Cost
    cost_usd = cost_data.get('total_cost_usd', 0)
    if cost_usd > 0:
        if cost_usd >= 0.10:
            cost_color = "\033[31m"  # Red for expensive
        elif cost_usd >= 0.05:
            cost_color = "\033[33m"  # Yellow for moderate
        else:
            cost_color = "\033[32m"  # Green for cheap

        cost_str = f"{cost_usd*100:.0f}¢" if cost_usd < 0.01 else f"${cost_usd:.3f}"
        metrics.append(f"{cost_color}💰 {cost_str}\033[0m")

    # Duration
    duration_ms = cost_data.get('total_duration_ms', 0)
    if duration_ms > 0:
        minutes = duration_ms / 60000
        if minutes >= 30:
            duration_color = "\033[33m"  # Yellow for long sessions
        else:
            duration_color = "\033[32m"  # Green

        if minutes < 1:
            duration_str = f"{duration_ms//1000}s"
        else:
            duration_str = f"{minutes:.0f}m"

        metrics.append(f"{duration_color}⏱ {duration_str}\033[0m")

    # Lines changed
    lines_added = cost_data.get('total_lines_added', 0)
    lines_removed = cost_data.get('total_lines_removed', 0)
    if lines_added > 0 or lines_removed > 0:
        net_lines = lines_added - lines_removed

        if net_lines > 0:
            lines_color = "\033[32m"  # Green for additions
        elif net_lines < 0:
            lines_color = "\033[31m"  # Red for deletions
        else:
            lines_color = "\033[33m"  # Yellow for neutral

        sign = "+" if net_lines >= 0 else ""
        metrics.append(f"{lines_color}📝 {sign}{net_lines}\033[0m")

    return f" \033[90m|\033[0m {' '.join(metrics)}" if metrics else ""

def main():
    try:
        # Read JSON input from Claude Code
        data = json.load(sys.stdin)

        # Extract information
        model_name = data.get('model', {}).get('display_name', 'Claude')
        workspace = data.get('workspace', {})
        transcript_path = data.get('transcript_path', '')
        cost_data = data.get('cost', {})

        # Parse context usage — prefer Claude Code's authoritative, model-aware
        # context_window object; fall back to transcript parsing (older schemas),
        # passing the real window size so the estimate isn't pinned to 200k.
        context_info = parse_context_from_window(data)
        if not context_info:
            window = (data.get('context_window') or {}).get('context_window_size') or 200000
            context_info = parse_context_from_transcript(transcript_path, window)

        # Build status components
        context_display = get_context_display(context_info)
        directory = get_directory_display(workspace)
        session_metrics = get_session_metrics(cost_data)

        # Model display with context-aware coloring
        if context_info:
            percent = context_info.get('percent', 0)
            if percent >= 90:
                model_color = "\033[31m"  # Red
            elif percent >= 75:
                model_color = "\033[33m"  # Yellow
            else:
                model_color = "\033[32m"  # Green

            model_display = f"{model_color}[{model_name}]\033[0m"
        else:
            model_display = f"\033[94m[{model_name}]\033[0m"

        # Combine all components
        status_line = f"{model_display} \033[93m📁 {directory}\033[0m 🧠 {context_display}{session_metrics}"

        print(status_line)

    except Exception as e:
        # Fallback display on any error
        print(f"\033[94m[Claude]\033[0m \033[93m📁 {os.path.basename(os.getcwd())}\033[0m 🧠 \033[31m[Error: {str(e)[:20]}]\033[0m")

if __name__ == "__main__":
    main()
