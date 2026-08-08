#!/bin/bash
# save_version.sh — Save a versioned snapshot of the project.
# Usage: ./save_version.sh "<description>"
#
# Creates a git commit + tag with format: vN-<sanitized-description>
# Increments the version number automatically.
set -e

cd /home/z/my-project/cafe-miniapp

DESC="${1:-untitled-change}"
# Sanitize description for tag name (lowercase, replace spaces with -)
TAG_DESC=$(echo "$DESC" | tr '[:upper:]' '[:lower:]' | tr ' ' '-' | tr -dc 'a-z0-9-')

# Find latest version tag
LATEST_TAG=$(git tag --list 'v*' --sort=-v:refname | head -1)
if [ -z "$LATEST_TAG" ]; then
  NEW_VERSION="v1"
else
  # Extract number from vN
  LATEST_NUM=$(echo "$LATEST_TAG" | sed 's/v\([0-9]*\).*/\1/')
  NEW_NUM=$((LATEST_NUM + 1))
  NEW_VERSION="v${NEW_NUM}"
fi

NEW_TAG="${NEW_VERSION}-${TAG_DESC}"

# Stage all changes (including new files)
git add -A

# Check if there's anything to commit
if git diff --cached --quiet; then
  echo "No changes to commit."
  exit 0
fi

# Commit + tag
git commit -m "${NEW_VERSION}: ${DESC}" --no-verify 2>&1 | tail -5
git tag -a "$NEW_TAG" -m "$DESC" 2>&1

echo ""
echo "✓ Saved version: $NEW_TAG"
echo "  Description: $DESC"
echo ""
echo "All versions:"
git tag --list 'v*' --sort=-v:refname | head -10
