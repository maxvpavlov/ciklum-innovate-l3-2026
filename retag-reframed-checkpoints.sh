#!/usr/bin/env bash
# Move the course checkpoint tags (7 November 2026): from lesson-04 on, the console keeps what the viewer
# chose or typed in a form when a view refreshes, and skips a refresh while a form control is in use, so
# INC-002 and INC-003 can be chosen in the Runs view (it refreshed every 2 s and reset the dropdown). Only
# agentic_platform/console/app.js changed; the Lesson 04 kit gives it again. Counts stay 1, 7, 12, 17,
# 19, 21, 29, 31, 37, 41, 47, 52, 55 and the capstone numbers are unchanged. The previous checkpoints are
# kept as v8/* tags first (v1/*..v8/* hold the earlier rebuilds), so this is reversible and idempotent.
# Run from a clone that has fetched main.
set -euo pipefail
git fetch origin main
git fetch --force origin "+refs/tags/*:refs/tags/*"
declare -A NEW=(
  [lesson-00]=827c1c8af99138d63156727645fd8044aa1db9c3
  [lesson-01]=7133fdcc650f04f22cacf233ff87679131b0e1b5
  [lesson-02]=7bbf4afb75ac73529462e7075c0ebc6ea962fa29
  [lesson-03]=3a81f99826b6ffd92f4d938aee7acc487e41022d
  [lesson-04]=1f615deeaa5c1730c1226b98be41909ea5679e93
  [lesson-05]=3b12fff863b3174f5c78005ed9b78398eec4c599
  [lesson-06]=83174e30682280c8d0f5f3aa2bdffb7893b8b83a
  [lesson-07]=db6361fad4ca37da5b2a1a1e5dd90cd0de3a388c
  [lesson-08]=e217a3eb712a75ae12e99121363dde9ffed9ae5d
  [lesson-09]=ae96a5b9301a6e3b1b3b1943e94d38d6b49a5937
  [lesson-10]=ad45ef49ab6ad7bf04c83804942a1da0ca6c044b
  [lesson-11]=887d6228c3444c0d94b21483ac4d97962fcfe80c
  [lesson-12]=8bf3c4373df4ed4cf94569ade7c4c579b3668f4d
  [course-complete]=fa199892c248e63c63c2be47898289fe90485ce7
)
for tag in "${!NEW[@]}"; do
  if ! git rev-parse -q --verify "refs/tags/v8/$tag" >/dev/null; then
    [ "$(git rev-parse "$tag^{commit}")" = "${NEW[$tag]}" ] || git tag "v8/$tag" "$tag"
  fi
  git tag -f "$tag" "${NEW[$tag]}"
done
backups=$(for tag in "${!NEW[@]}"; do git rev-parse -q --verify "refs/tags/v8/$tag" >/dev/null && printf 'refs/tags/v8/%s ' "$tag"; done)
[ -z "$backups" ] || git push origin $backups
git push --force origin $(printf 'refs/tags/%s ' "${!NEW[@]}")
