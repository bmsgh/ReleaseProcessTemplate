# encoding: utf-8

"""
Prepares markdown release notes for GitHub releases.
"""

import os
import re
import sys
from typing import List, Optional, Tuple

if "TAG" in os.environ:
    TAG = os.environ["TAG"]
else:
    TAG = sys.argv[1]

ADDED_HEADER = "### Added 🎉"
CHANGED_HEADER = "### Changed ⚠️"
FIXED_HEADER = "### Fixed ✅"
REMOVED_HEADER = "### Removed 👋"


def get_change_log_notes() -> str:
    in_current_section = False
    current_section_notes: List[str] = []
    with open("CHANGELOG.md") as changelog:
        for line in changelog:
            if line.startswith("## Unreleased"):
                continue
            if line.startswith(f"## [v{TAG}]"):
                in_current_section = True
                continue
            if in_current_section:
                if line.startswith("### Added"):
                    line = ADDED_HEADER + "\n"
                elif line.startswith("### Changed"):
                    line = CHANGED_HEADER + "\n"
                elif line.startswith("### Fixed"):
                    line = FIXED_HEADER + "\n"
                elif line.startswith("### Removed"):
                    line = REMOVED_HEADER + "\n"
                current_section_notes.append(line)
    assert current_section_notes, f"Expected to find notes in section '## [v{TAG}]'"
    return "## What's new\n\n" + "".join(current_section_notes).strip() + "\n"

def parse_version(version_str: str) -> Tuple[Tuple[int, int, int], Optional[str]]:
    """
    Parse a version string into ((major, minor, patch), prerelease).
    Returns: ((major, minor, patch), prerelease_string_or_None)

    Examples:
    - 'v2.1.0' -> ((2, 1, 0), None)
    - 'v2.1.0-alpha1' -> ((2, 1, 0), 'alpha1')
    - 'v2.1.0-beta.2' -> ((2, 1, 0), 'beta.2')
    """
    # Remove 'v' prefix if present
    clean_version = version_str.lstrip('v')

    # Split on '-' to separate version from prerelease
    if '-' in clean_version:
        version_part, prerelease_part = clean_version.split('-', 1)
    else:
        version_part, prerelease_part = clean_version, None

    # Parse version numbers
    parts = version_part.split('.')
    major = int(parts[0]) if len(parts) > 0 else 0
    minor = int(parts[1]) if len(parts) > 1 else 0
    patch = int(parts[2]) if len(parts) > 2 else 0

    return (major, minor, patch), prerelease_part


def compare_versions(v1: str, v2: str) -> int:
    """
    Compare two version strings following semantic versioning rules.
    Returns: -1 if v1 < v2, 0 if v1 == v2, 1 if v1 > v2

    Pre-release versions are considered less than their corresponding release versions.
    """
    (major1, minor1, patch1), pre1 = parse_version(v1)
    (major2, minor2, patch2), pre2 = parse_version(v2)

    # Compare version numbers first
    if (major1, minor1, patch1) != (major2, minor2, patch2):
        if major1 != major2:
            return -1 if major1 < major2 else 1
        if minor1 != minor2:
            return -1 if minor1 < minor2 else 1
        if patch1 != patch2:
            return -1 if patch1 < patch2 else 1

    # Version numbers are equal, compare pre-release
    if pre1 is None and pre2 is None:
        return 0  # Both are releases, equal
    elif pre1 is None and pre2 is not None:
        return 1  # Release > pre-release
    elif pre1 is not None and pre2 is None:
        return -1  # Pre-release < release
    else:
        # Both are pre-releases, compare lexicographically
        if pre1 < pre2:
            return -1
        elif pre1 > pre2:
            return 1
        else:
            return 0


def get_commit_history() -> str:
    current_version = f"v{TAG}"
    _, current_prerelease = parse_version(current_version)

    # Pull all tags.
    os.popen("git fetch --tags")

    # Get all tags sorted by version, latest first.
    all_tags = os.popen("git tag -l --sort=-version:refname 'v*'").read().split("\n")

    # Out of `all_tags`, find the latest previous version so that we can collect all
    # commits between that version and the new version we're about to publish.
    # Note that we ignore pre-releases unless the new version is also a pre-release.
    last_tag: Optional[str] = None
    for tag in all_tags:
        if not tag.strip():  # could be blank line
            continue

        _, tag_prerelease = parse_version(tag)

        # Skip pre-releases if the current version is not a pre-release
        if current_prerelease is None and tag_prerelease is not None:
            continue

        # Check if this tag is less than the current version
        if compare_versions(tag, current_version) < 0:
            last_tag = tag
            break

    if last_tag is not None:
        commits = os.popen(f"git log {last_tag}..v{TAG} --oneline --first-parent").read()
    else:
        commits = os.popen("git log --oneline --first-parent").read()
    return "## Commits\n\n" + commits


def main():
    print(get_change_log_notes())
    print(get_commit_history())


if __name__ == "__main__":
    main()
