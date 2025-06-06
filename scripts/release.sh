#!/bin/bash -e
# Usage: ./scripts/release.sh <VERSION>
# where VERSION is the version number to release

TAG=$1

read -p "Creating new release for v$TAG. Do you want to continue? [Y/n] " prompt

if [[ $prompt == "y" || $prompt == "Y" || $prompt == "yes" || $prompt == "Yes" ]]; then
    REPO_URL=$(git config --local --get remote.origin.url)
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

    python3 scripts/prepare_changelog.py $REPO_URL $TAG
    git add CHANGELOG.md
    git commit -m "Bump version to $TAG for release" || true && git push
    echo "Creating new git tag $TAG"
    git tag "v$TAG" -m "v$TAG" -a
    git push --tags

    python3 scripts/release_notes.py $TAG > RELEASE_NOTES-${TAG}.md
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
