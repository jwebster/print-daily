#!/usr/bin/env python3
"""Generate launchd plist with correct paths for this installation."""

import os
import sys
from pathlib import Path

PLIST_TEMPLATE = '''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.print-daily</string>
    <key>ProgramArguments</key>
    <array>
        <string>{python_path}</string>
        <string>{script_path}</string>
    </array>
    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key>
        <integer>6</integer>
        <key>Minute</key>
        <integer>30</integer>
    </dict>
    <key>WorkingDirectory</key>
    <string>{working_dir}</string>
    <key>StandardOutPath</key>
    <string>{working_dir}/logs/stdout.log</string>
    <key>StandardErrorPath</key>
    <string>{working_dir}/logs/stderr.log</string>
    <key>RunAtLoad</key>
    <false/>
</dict>
</plist>
'''

def main():
    project_dir = Path(__file__).parent.absolute()
    python_path = sys.executable
    script_path = project_dir / "generate_daily.py"

    # Create logs directory
    logs_dir = project_dir / "logs"
    logs_dir.mkdir(exist_ok=True)

    plist_content = PLIST_TEMPLATE.format(
        python_path=python_path,
        script_path=script_path,
        working_dir=project_dir,
    )

    output_path = Path.home() / "Library/LaunchAgents/com.print-daily.plist"
    output_path.write_text(plist_content)
    print(f"Created: {output_path}")
    print(f"Run: launchctl load {output_path}")

if __name__ == "__main__":
    main()
