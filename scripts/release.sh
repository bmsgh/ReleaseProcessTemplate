#!/bin/bash -e
# Usage: ./scripts/release.sh <VERSION>
# where VERSION is the version number to release

# Validate input arguments
if [ $# -ne 1 ]; then
    echo "ERROR: Missing required argument!"
    echo "Usage: ./scripts/release.sh <VERSION>"
    echo "  VERSION: Version number to release (e.g., 2.1.2)"
    exit 1
fi

TAG=$1

# Validate TAG is not empty
if [ -z "$TAG" ] || [ -z "$(echo "$TAG" | tr -d '[:space:]')" ]; then
    echo "ERROR: VERSION cannot be empty!"
    echo "Usage: ./scripts/release.sh <VERSION>"
    echo "  VERSION: Version number to release (e.g., 2.1.2)"
    exit 1
fi

echo "Checking for RELEASE_NOTES-${TAG}.md..."
if [ ! -f "RELEASE_NOTES-${TAG}.md" ]; then
    echo "ERROR: RELEASE_NOTES-${TAG}.md does not exist!"
    echo "Please run './scripts/write_release_notes.sh ${TAG}' first to generate the release notes."
    exit 1
fi
echo "✓ RELEASE_NOTES-${TAG}.md found"

read -p "Creating new release for v$TAG. Do you want to continue? [Y/n] " prompt

if [[ $prompt == "y" || $prompt == "Y" || $prompt == "yes" || $prompt == "Yes" ]]; then
    REPO_URL=$(git config --local --get remote.origin.url | sed 's|\(https://\).*@|\1|')
    REPO_URL=${REPO_URL%".git"}

    if [ $OSTYPE == "darwin22" ]; then
        sed -i '' "s/__version__ = \".*\"/__version__ = \"$TAG\"/" launcher/src/pipeline_config.py
    elif [ $OSTYPE == "linux-gnu" ]; then
        sed -i "s/__version__ = \".*\"/__version__ = \"$TAG\"/" launcher/src/pipeline_config.py
    else
        echo "Unknown OSTYPE"
	exit 1
    fi

    git add launcher/src/pipeline_config.py
    git add CHANGELOG.md
    git commit -m "Bump version to $TAG for release" || true && git push
    echo "Creating new git tag $TAG"
    git tag "v$TAG" -m "v$TAG" -a
    git push --tags

    gh release create \
      --title v$TAG \
      --notes-file RELEASE_NOTES-${TAG}.md \
      --draft \
      --prerelease \
      --repo ${REPO_URL}.git \
      v${TAG}

    make VERSION=${TAG} build-launcher
    make VERSION=${TAG} sevenbridges-push-launcher
    make VERSION=${TAG} arvados-push-launcher
    make VERSION=${TAG} sevenbridges-push-workflows
    make VERSION=${TAG} arvados-push-workflows
else
    echo "Cancelled"
    exit 1
fi
