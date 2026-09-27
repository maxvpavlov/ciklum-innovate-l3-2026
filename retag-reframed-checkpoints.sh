#!/usr/bin/env bash
# Move the course checkpoint tags to the reframed reference (September 2026).
# The previous checkpoints are kept as v1/* tags first, so this is reversible.
# Run from a clone that has fetched claude/clever-tesla-bnbyzh (or main after merging it).
set -euo pipefail
git fetch origin claude/clever-tesla-bnbyzh
git fetch --force origin "+refs/tags/*:refs/tags/*"
declare -A NEW=(
  [lesson-06]=e0d49922f260995ea6d44aee2ab4e09defc42a4a
  [lesson-07]=7713de091489299a0d988b210028953b777275fe
  [lesson-08]=059921a6ce73bbeeb9fb4c0dd9547268deccf4f7
  [lesson-09]=99cfe82595c3c5a5aa330fb6fbf8921c3b76bdf3
  [lesson-10]=0e0a5bacbe7a57576a97af612f01475435df183b
  [lesson-11]=fa17a36d8e7da93f13bf5baa5222d75377a0181d
  [lesson-12]=00c1e41b9408b77b4abccb5dfc95ecda8441bec2
  [course-complete]=5950bd7ba7b3cfdfe34537bd3a85efe70e24fd96
)
for tag in "${!NEW[@]}"; do
  git rev-parse -q --verify "refs/tags/v1/$tag" >/dev/null || git tag "v1/$tag" "$tag"
  git tag -f "$tag" "${NEW[$tag]}"
done
git push origin $(printf 'refs/tags/v1/%s ' "${!NEW[@]}")
git push --force origin $(printf 'refs/tags/%s ' "${!NEW[@]}")
