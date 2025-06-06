# encoding: utf-8

"""
Prepares markdown release notes for GitHub releases and updates CHANGELOG.md.
"""

import os
import re
import sys
from pathlib import Path
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
    """Extract manual release notes from CHANGELOG.md for the current version."""
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
                if line.startswith("## ["):  # Hit next version section
                    break
                if line.startswith("### Added"):
                    line = ADDED_HEADER + "\n"
                elif line.startswith("### Changed"):
                    line = CHANGED_HEADER + "\n"
                elif line.startswith("### Fixed"):
                    line = FIXED_HEADER + "\n"
                elif line.startswith("### Removed"):
                    line = REMOVED_HEADER + "\n"
                current_section_notes.append(line)
    if current_section_notes:
        return "## What's new\n\n" + "".join(current_section_notes).strip()
    return ""

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


def get_merged_pull_requests() -> str:
    """Get merged pull requests between the last tag and current version."""
    current_version = f"v{TAG}"
    _, current_prerelease = parse_version(current_version)

    # Pull all tags.
    os.popen("git fetch --tags")

    # Get all tags sorted by version, latest first.
    all_tags = os.popen("git tag -l --sort=-version:refname 'v*'").read().split("\n")

    # Find the latest previous version
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

    # Get merge commits (pull requests) between tags
    if last_tag is not None:
        merge_commits = os.popen(f"git log {last_tag}..v{TAG} --merges --pretty=format:'%s' --first-parent").read()
    else:
        merge_commits = os.popen("git log --merges --pretty=format:'%s' --first-parent").read()
    
    if not merge_commits.strip():
        return ""
    
    # Parse merge commits to extract PR information
    pr_lines = []
    for line in merge_commits.split('\n'):
        if line.strip():
            # Try to extract PR info from merge commit message
            # Format: "Merge pull request #123 from user/branch"
            pr_match = re.search(r'Merge pull request #(\d+) from ([^/]+)/', line)
            if pr_match:
                pr_number = pr_match.group(1)
                author = pr_match.group(2)
                
                # Get PR title from GitHub API or git log
                pr_title = get_pr_title(pr_number)
                if pr_title:
                    # Get repository URL for the link
                    repo_url = get_repo_url()
                    pr_lines.append(f"* {pr_title} by @{author} in {repo_url}/pull/{pr_number}")
    
    if pr_lines:
        return "## What's Changed\n" + "\n".join(pr_lines) + "\n"
    return ""


def get_pr_title(pr_number: str) -> Optional[str]:
    """Get PR title from git log or return a placeholder."""
    # Try to get the PR title from the commit that was merged
    try:
        # Get the merge commit and find the actual PR commit
        merge_commit = os.popen(f"git log --merges --grep='#{pr_number}' --pretty=format:'%H' -1").read().strip()
        if merge_commit:
            # Get the second parent (the PR commit)
            pr_commit = os.popen(f"git log {merge_commit}^2 --pretty=format:'%s' -1").read().strip()
            if pr_commit:
                return pr_commit
    except:
        pass
    
    return f"Pull request #{pr_number}"


def get_repo_url() -> str:
    """Get the repository URL from git config."""
    repo_url = os.popen("git config --local --get remote.origin.url").read().strip()
    # Convert SSH to HTTPS if needed
    if repo_url.startswith("git@github.com:"):
        repo_url = repo_url.replace("git@github.com:", "https://github.com/")
    # Remove .git suffix
    if repo_url.endswith(".git"):
        repo_url = repo_url[:-4]
    return repo_url


def update_changelog(release_content: str) -> None:
    """Update CHANGELOG.md directly with the release content."""
    changelog_path = Path('CHANGELOG.md')
    with open(changelog_path, 'r') as f:
        content = f.read()

    # Find the version section and replace it with release notes content
    version_pattern = rf'(## \[v{re.escape(TAG)}\][^\n]*\n)(\n*)(.*?)(?=\n## \[v|\n## \[|\Z)'

    def replace_version_section(match):
        header = match.group(1)
        return header + '\n' + release_content.strip() + '\n\n'

    updated_content = re.sub(version_pattern, replace_version_section, content, flags=re.DOTALL)

    # Write back to CHANGELOG.md
    with open(changelog_path, 'w') as f:
        f.write(updated_content)

    print(f"✓ Updated CHANGELOG.md with release notes for v{TAG}")


def main():
    """Generate release notes and update CHANGELOG.md."""
    # Get manual notes from changelog
    manual_notes = get_change_log_notes()
    
    # Get merged pull requests
    pr_notes = get_merged_pull_requests()
    
    # Combine all content for release notes
    release_content_parts = []
    if manual_notes:
        release_content_parts.append(manual_notes)
    if pr_notes:
        release_content_parts.append(pr_notes)
    
    if release_content_parts:
        release_content = "\n\n".join(release_content_parts)
        # Output complete release notes to stdout (for RELEASE_NOTES-{TAG}.md file)
        print(release_content)
        # Also update CHANGELOG.md directly
        update_changelog(release_content)
    else:
        print("No release notes generated - no manual notes or merged pull requests found.")


if __name__ == "__main__":
    main()
