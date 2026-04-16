#!/usr/bin/env bash
set -euo pipefail

# Publish tg skill to ClawdHub
# Usage:
#   ./scripts/publish-skill.sh              # Use version from package.json
#   ./scripts/publish-skill.sh 0.2.0        # Specify version
#   ./scripts/publish-skill.sh patch        # Bump patch (0.1.0 -> 0.1.1)
#   ./scripts/publish-skill.sh minor        # Bump minor (0.1.0 -> 0.2.0)
#   ./scripts/publish-skill.sh major        # Bump major (0.1.0 -> 1.0.0)

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_DIR"

# Read current version from package.json
CURRENT_VERSION=$(node -p "require('./package.json').version")

# Determine target version
if [[ $# -eq 0 ]]; then
    VERSION="$CURRENT_VERSION"
elif [[ "$1" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    VERSION="$1"
elif [[ "$1" == "patch" || "$1" == "minor" || "$1" == "major" ]]; then
    IFS='.' read -r major minor patch <<< "$CURRENT_VERSION"
    case "$1" in
        patch) VERSION="$major.$minor.$((patch + 1))" ;;
        minor) VERSION="$major.$((minor + 1)).0" ;;
        major) VERSION="$((major + 1)).0.0" ;;
    esac
else
    echo "Usage: $0 [version|patch|minor|major]"
    echo "  version: semver like 0.2.0"
    echo "  patch:   bump patch version"
    echo "  minor:   bump minor version"
    echo "  major:   bump major version"
    exit 1
fi

# Get changelog from git (commits since last tag, or last 5 commits)
LAST_TAG=$(git describe --tags --abbrev=0 2>/dev/null || echo "")
if [[ -n "$LAST_TAG" ]]; then
    CHANGELOG=$(git log "$LAST_TAG"..HEAD --oneline --no-decorate | head -10 | sed 's/^/- /')
else
    CHANGELOG=$(git log -5 --oneline --no-decorate | sed 's/^/- /')
fi

if [[ -z "$CHANGELOG" ]]; then
    CHANGELOG="Version $VERSION"
fi

echo "Publishing tg skill v$VERSION"
echo "Changelog:"
echo "$CHANGELOG"
echo ""

# Update package.json version if different
if [[ "$VERSION" != "$CURRENT_VERSION" ]]; then
    echo "Updating package.json version: $CURRENT_VERSION -> $VERSION"
    npm pkg set version="$VERSION"
fi

# Publish to ClawdHub
# Note: --workdir is required to override clawdbot default workspace
TAGS="latest,telegram,messaging,chat,cli"

clawdhub --workdir "$PROJECT_DIR" publish . \
    --slug tg \
    --name "Telegram CLI" \
    --version "$VERSION" \
    --tags "$TAGS" \
    --changelog "$CHANGELOG"

echo ""
echo "Published tg@$VERSION to ClawdHub"
