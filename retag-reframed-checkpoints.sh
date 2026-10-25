#!/usr/bin/env bash
# Move the course checkpoint tags to the restructured reference (25 October 2026): every checkpoint,
# lesson-00..lesson-12 and course-complete, now keeps the agent runtime in agent_runtime/, the platform
# in agentic_platform/ and the course scaffolding in course/ instead of one incident/ package. Same
# tests, same numbers. The previous checkpoints are kept as v3/* tags first (v1/* and v2/* hold the
# earlier rebuilds), so this is reversible and idempotent.
# Run from a clone that has fetched claude/clever-tesla-bnbyzh (or main after merging it).
set -euo pipefail
git fetch origin claude/clever-tesla-bnbyzh
git fetch --force origin "+refs/tags/*:refs/tags/*"
declare -A NEW=(
  [lesson-00]=2e852ab76821e8eccc416affbcfb31805fb0d76e
  [lesson-01]=9847de9ec7ed5e32f5671a1b485be1672cc0b029
  [lesson-02]=4d533bc82ccfefc9c233009dc8c760fd0fa4e76e
  [lesson-03]=094df54c92e050453f93af9403f81089dc5e8227
  [lesson-04]=157768ea57f6ec198efc4ddc472feb7b7846400a
  [lesson-05]=f3cc0ccf77af913271ddf8f9ebd0ee4f69b4d31b
  [lesson-06]=60c24e5927f060494be9e29ca8312ef4038dec1c
  [lesson-07]=1c95964bac56f5d8a580687bab0431f1bacc2efa
  [lesson-08]=c899d657a8aca7718ce5e39272babb77ca41fceb
  [lesson-09]=1fa582c3e3ea864cba9197f65f6be101346820c0
  [lesson-10]=24ce4dfd55b55eff9fcbc04b12eb9e2287ffab61
  [lesson-11]=e0f01f84907adafa965f83c713c485aacfa679db
  [lesson-12]=b867df96f0e393b5890ee6578cf2ed8661f6194b
  [course-complete]=e2c28f1b000214604e945cbb7e1b66676b4cedff
)
for tag in "${!NEW[@]}"; do
  if ! git rev-parse -q --verify "refs/tags/v3/$tag" >/dev/null; then
    [ "$(git rev-parse "$tag^{commit}")" = "${NEW[$tag]}" ] || git tag "v3/$tag" "$tag"
  fi
  git tag -f "$tag" "${NEW[$tag]}"
done
backups=$(for tag in "${!NEW[@]}"; do git rev-parse -q --verify "refs/tags/v3/$tag" >/dev/null && printf 'refs/tags/v3/%s ' "$tag"; done)
[ -z "$backups" ] || git push origin $backups
git push --force origin $(printf 'refs/tags/%s ' "${!NEW[@]}")
