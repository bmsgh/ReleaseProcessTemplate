'''
Prepares CHANGELOG.md

On inital run, if no changelog is present, a CHANGELOG.md file is created with an empty Unreleased section and [v$TAG] section.
On subsequent runs, Unreleased is updated to [v$TAG] and a new Unreleased section is created.

This script does NOT add anything to the Unreleased or version section, it only converts the Unreleased section to [v$TAG].  
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

#from my_package.version import VERSION
REPO=sys.argv[1]
VERSION=sys.argv[2]

def main():
    changelog = Path("CHANGELOG.md")

    if not changelog.exists():
        with changelog.open(mode='w') as f:
            f.write(f"## Changelog\n\n## Unreleased\n")

    with changelog.open() as f:
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

    with changelog.open("w") as f:
        f.writelines(lines)


if __name__ == "__main__":
    main()
