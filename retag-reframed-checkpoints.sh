#!/usr/bin/env bash
# Move the course checkpoint tags to the reference with the platform shell (24 October 2026):
# lesson-02..lesson-12 and course-complete gain a given run API and console from Session 02.
# lesson-00 and lesson-01 are unchanged. The previous checkpoints are kept as v2/* tags first
# (the September 2026 originals are already v1/*), so this is reversible and idempotent.
# Run from a clone that has fetched claude/clever-tesla-bnbyzh (or main after merging it).
set -euo pipefail
git fetch origin claude/clever-tesla-bnbyzh
git fetch --force origin "+refs/tags/*:refs/tags/*"
declare -A NEW=(
  [lesson-02]=2d0a675a349a9e8f5650b634e7b901178bf248e0
  [lesson-03]=60fbebf300176b6e57204a385cb2acb95aa5466b
  [lesson-04]=94b139360df490f825530faddc0bb32bc8cc8715
  [lesson-05]=cb80e96b0e378df5346ce212582c7c6ea3e9a3ea
  [lesson-06]=e4c54a70f106a48bc907892e29e4c18ce036e100
  [lesson-07]=e79c003be56cc64b85bd3b7d1922123c3883617e
  [lesson-08]=675ee7e9cdfbc3084cb0b1161c710b344e1554ac
  [lesson-09]=13af6c24898c4f88f57f893ab7d4eaecf8c69fb6
  [lesson-10]=77a5859ccf7573ec01326616c283c1d7d3200ea0
  [lesson-11]=2616483c4a94099c54428a110411b3a8d8432364
  [lesson-12]=8e8242846e80e2a5e2c0c1fc4df3c075a4619665
  [course-complete]=60230786d1559337f696180bed74c4af4288f509
)
for tag in "${!NEW[@]}"; do
  if ! git rev-parse -q --verify "refs/tags/v2/$tag" >/dev/null; then
    [ "$(git rev-parse "$tag^{commit}")" = "${NEW[$tag]}" ] || git tag "v2/$tag" "$tag"
  fi
  git tag -f "$tag" "${NEW[$tag]}"
done
backups=$(for tag in "${!NEW[@]}"; do git rev-parse -q --verify "refs/tags/v2/$tag" >/dev/null && printf 'refs/tags/v2/%s ' "$tag"; done)
[ -z "$backups" ] || git push origin $backups
git push --force origin $(printf 'refs/tags/%s ' "${!NEW[@]}")
