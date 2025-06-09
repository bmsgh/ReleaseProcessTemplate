'''
Prepares CHANGELOG.md

On inital run, if no changelog is present, a CHANGELOG.md file is created with an
empty Unreleased section and [v$TAG] section.
On subsequent runs, Unreleased is updated to [v$TAG] and a new Unreleased section is created.

This script does NOT add anything to the Unreleased or version section, it only converts
the Unreleased section to [v$TAG].
It is currently up to the user to populate the Unreleased section with informative information.

It is option to use the following subsections, but beneficial for readability.

### Added
### Changed
### Fixed
### Removed

'''
from datetime import datetime
from pathlib import Path
import sys

def main():
    """ Check inputs and prepare the CHANGELOG.md file. """
    # Check for required arguments
    if len(sys.argv) != 3:
        print("ERROR: Missing required arguments!")
        print("Usage: python3 prepare_changelog.py <REPO_URL> <VERSION>")
        print("  REPO_URL: Repository URL (e.g., https://github.com/user/repo)")
        print("  VERSION:  Version number (e.g., 2.1.2)")
        sys.exit(1)

    REPO = sys.argv[1]
    VERSION = sys.argv[2]

    # Validate inputs
    if not REPO.strip():
        print("ERROR: REPO_URL cannot be empty!")
        sys.exit(1)

    if not VERSION.strip():
        print("ERROR: VERSION cannot be empty!")
        sys.exit(1)

    prepare_changelog(REPO, VERSION)

def prepare_changelog(REPO, VERSION):
    """Prepare CHANGELOG.md by creating or updating it with the given repository URL and version."""
    changelog = Path("CHANGELOG.md")

    if not changelog.exists():
        with changelog.open(mode='w', encoding="utf-8") as f:
            f.write("## Changelog\n\n## Unreleased\n")

    with changelog.open(encoding="utf-8") as f:
        lines = f.readlines()

    insert_index: int = -1
    for i in range(len(lines)):
        line = lines[i]
        if line.startswith("## Unreleased"):
            insert_index = i + 1
        elif line.startswith(f"## [v{VERSION}]"):
            print("CHANGELOG already up-to-date")
            return
        elif line.startswith("## [v"):
            break

    if insert_index < 0:
        raise RuntimeError("Couldn't find 'Unreleased' section")

    lines.insert(insert_index, "\n")
    lines.insert(
        insert_index + 1,
        f"## [v{VERSION}]({REPO}/releases/tag/v{VERSION}) - "
        f"{datetime.now().strftime('%Y-%m-%d')}\n",
    )

    with changelog.open("w", encoding = "utf-8") as f:
        f.writelines(lines)


if __name__ == "__main__":
    main()
