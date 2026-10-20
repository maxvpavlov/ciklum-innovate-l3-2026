#!/usr/bin/env bash
# Move the course checkpoint tags to the reframed reference (September 2026), whose fictional
# tenants are Astro and Locomotive (October 2026). lesson-00 is unchanged.
# The previous checkpoints are kept as v1/* tags first, so this is reversible.
# Run from a clone that has fetched claude/clever-tesla-bnbyzh (or main after merging it).
set -euo pipefail
git fetch origin claude/clever-tesla-bnbyzh
git fetch --force origin "+refs/tags/*:refs/tags/*"
declare -A NEW=(
  [lesson-01]=7133fdcc650f04f22cacf233ff87679131b0e1b5
  [lesson-02]=384c2fbc3c4e2b6cff2ffd9199fbb8986aee6006
  [lesson-03]=fa7ce4e7f8cb31aca8984c5c58b9c220f5e205c8
  [lesson-04]=23528169388d6aab7ff53eb5117366654ad59882
  [lesson-05]=ac763f639fedaa0e19114a939a6b38b2c73940a4
  [lesson-06]=299316a992bb867bb800a5c955eb74db898dbe82
  [lesson-07]=974fd16b89d258df7aab9212e75899e72725f406
  [lesson-08]=21a8a6e3145dc5ec58f4e82c43cb404c392a6a4a
  [lesson-09]=ffd4ea982f99ed16f274d81eece4b69c287af809
  [lesson-10]=9158dfad56bd231c8a24ff007bee5e3843f206bf
  [lesson-11]=b0c78fad257708bcd97a96452a5d0a53d851f496
  [lesson-12]=40bd536b036f0f3a711239283656555b0c12affe
  [course-complete]=683b2fdc371af41a11d54025ebb14856b0e52eaf
)
for tag in "${!NEW[@]}"; do
  git rev-parse -q --verify "refs/tags/v1/$tag" >/dev/null || git tag "v1/$tag" "$tag"
  git tag -f "$tag" "${NEW[$tag]}"
done
git push origin $(printf 'refs/tags/v1/%s ' "${!NEW[@]}")
git push --force origin $(printf 'refs/tags/%s ' "${!NEW[@]}")
