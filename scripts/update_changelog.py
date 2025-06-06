#!/usr/bin/env python3
"""
Updates CHANGELOG.md with content from RELEASE_NOTES file.
"""

import re
import sys
from pathlib import Path

def update_changelog(tag, release_notes_file):
    """Update CHANGELOG.md with content from release notes file"""

    # Read the release notes content (skip "## What's new" header)
    with open(release_notes_file, 'r') as f:
        lines = f.readlines()

    # Skip the first line ("## What's new") and get the rest
    release_content = ''.join(lines[1:]).strip()

    # Read CHANGELOG.md
    changelog_path = Path('CHANGELOG.md')
    with open(changelog_path, 'r') as f:
        content = f.read()

    # Find the version section and replace it with release notes content
    version_pattern = rf'(## \[v{re.escape(tag)}\][^\n]*\n)(\n*)(.*?)(?=\n## \[v|\n## \[|\Z)'

    def replace_version_section(match):
        header = match.group(1)
        return header + '\n' + release_content + '\n\n'

    updated_content = re.sub(version_pattern, replace_version_section, content, flags=re.DOTALL)

    # Write back to CHANGELOG.md
    with open(changelog_path, 'w') as f:
        f.write(updated_content)

    print(f"✓ Updated CHANGELOG.md with content from {release_notes_file}")

def main():
    if len(sys.argv) != 3:
        print("Usage: python3 update_changelog.py <TAG> <RELEASE_NOTES_FILE>")
        sys.exit(1)

    tag = sys.argv[1]
    release_notes_file = sys.argv[2]

    if not Path(release_notes_file).exists():
        print(f"ERROR: Release notes file {release_notes_file} does not exist!")
        sys.exit(1)

    update_changelog(tag, release_notes_file)

if __name__ == "__main__":
    main()