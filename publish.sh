#!/bin/sh
# Publish BDAY to https://github.com/bariscetinbc/BDAY
# Run this from this folder after the person signs in to GitHub.
set -e
cd "$(dirname "$0")" || exit 1

if ! command -v gh >/dev/null 2>&1; then
  echo "GitHub CLI is not installed. Install it from https://cli.github.com/ and run this again."
  exit 1
fi

if ! gh auth status >/dev/null 2>&1; then
  echo "Signing in to GitHub. Follow the instructions shown below."
  gh auth login
fi

owner_repo="bariscetinbc/BDAY"

if gh repo view "$owner_repo" >/dev/null 2>&1; then
  echo "Repository already exists; pushing the current code."
  git remote remove origin 2>/dev/null || true
  git remote add origin "https://github.com/$owner_repo.git"
  git push -u origin main
else
  echo "Creating $owner_repo and pushing the current code."
  git remote remove origin 2>/dev/null || true
  gh repo create "$owner_repo" --public --source=. --remote=origin --push
fi

echo "Published: https://github.com/$owner_repo"
