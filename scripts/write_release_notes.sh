#!/bin/bash -e
# Usage: ./scripts/write_release_notes.sh <VERSION>
# where VERSION is the version number to release

# Validate input arguments
if [ $# -ne 1 ]; then
    echo "ERROR: Missing required argument!"
    echo "Usage: ./scripts/write_release_notes.sh <VERSION>"
    echo "  VERSION: Version number to release (e.g., 2.1.2)"
    exit 1
fi

TAG=$1

# Validate TAG is not empty
if [ -z "$TAG" ] || [ -z "$(echo "$TAG" | tr -d '[:space:]')" ]; then
    echo "ERROR: VERSION cannot be empty!"
    echo "Usage: ./scripts/write_release_notes.sh <VERSION>"
    echo "  VERSION: Version number to release (e.g., 2.1.2)"
    exit 1
fi

echo "Preparing release notes for version: $TAG"

REPO_URL=$(git config --local --get remote.origin.url | sed 's|\(https://\).*@|\1|')
REPO_URL=${REPO_URL%".git"}

echo "Preparing CHANGELOG.md for version ${TAG}..."
python3 scripts/prepare_changelog.py $REPO_URL $TAG

echo "Generating RELEASE_NOTES-${TAG}.md..."
python3 scripts/release_notes.py $TAG > RELEASE_NOTES-${TAG}.md

echo "Updating CHANGELOG.md with release notes content..."
python3 scripts/update_changelog.py $TAG RELEASE_NOTES-${TAG}.md

echo "✓ RELEASE_NOTES-${TAG}.md generated"
echo ""
echo "Files created/updated:"
echo "  - CHANGELOG.md (populated with v${TAG} release notes)"
echo "  - RELEASE_NOTES-${TAG}.md (created for GitHub release)"
