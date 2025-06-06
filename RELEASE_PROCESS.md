# GitHub Release Process

This (vaguely) follows the guidance of [Python Package Template](https://github.com/allenai/python-package-template)

## Steps

1. Run the release script:

    ```bash
    TAG=<Version number for the release (do not include "v" prefix)>
    ./scripts/write_release_notes.sh $TAG
    ./scripts/release.sh $TAG
    ```

    This will
    1. Update CHANGELOG.md
    2. Create a new tag in git
    3. Generate release notes
    4. Create a release in git
    5. Build and deploy launcher and workflows

## Fixing a failed release

If for some reason the GitHub Actions release workflow failed with an error that needs to be fixed, you'll have to
delete both the tag and corresponding release from GitHub. After you've pushed a fix, delete the tag from your local
clone with.

```{bash}
git tag -l | xargs git tag -d && git fetch -t
```

Then repeat the steps above.
