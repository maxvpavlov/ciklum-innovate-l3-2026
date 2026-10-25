#!/usr/bin/env bash
# Move the course checkpoint tags (25 October 2026): from lesson-02 on the checkpoints keep the agent
# runtime in agent_runtime/, the platform in agentic_platform/ and the course scaffolding in course/,
# and the given platform shell starts on a Lesson 01 runtime (before ToolExecutor exists), so learners
# can run it as soon as they move their project in Lesson 02. lesson-00 and lesson-01 stay on incident/.
# Same tests, same numbers. The previous checkpoints are kept as v4/* tags first (v1/*..v3/* hold the
# earlier rebuilds), so this is reversible and idempotent.
# Run from a clone that has fetched claude/clever-tesla-bnbyzh (or main after merging it).
set -euo pipefail
git fetch origin claude/clever-tesla-bnbyzh
git fetch --force origin "+refs/tags/*:refs/tags/*"
declare -A NEW=(
  [lesson-00]=827c1c8af99138d63156727645fd8044aa1db9c3
  [lesson-01]=7133fdcc650f04f22cacf233ff87679131b0e1b5
  [lesson-02]=7bbf4afb75ac73529462e7075c0ebc6ea962fa29
  [lesson-03]=8095b508c686546f78310901e9486864050bb7cd
  [lesson-04]=81df531778dde3155afcef126ad06749e7d30288
  [lesson-05]=3e467a320208e3267598c3ef0b8e115b583e123a
  [lesson-06]=48d171cc5b1db50646972286b85a0584003443d7
  [lesson-07]=00ebb9ddd5b65920d2f9c6036dea3c33007e5965
  [lesson-08]=36ee7ea35048794d71addd4f3bb2b28ca4e5b922
  [lesson-09]=ac6669a7ac559765c5fd058371fce25677fe5159
  [lesson-10]=c2087009a226d172a126624cc1287bda93765b3d
  [lesson-11]=166bbfe5e7345141467761437b02dcf64b166bfd
  [lesson-12]=bf699c7a02a1b4576c15f8d796b5b0f4d37e5039
  [course-complete]=4ed2c2a2b61d41e0d434ba8c73797065006fea77
)
for tag in "${!NEW[@]}"; do
  if ! git rev-parse -q --verify "refs/tags/v4/$tag" >/dev/null; then
    [ "$(git rev-parse "$tag^{commit}")" = "${NEW[$tag]}" ] || git tag "v4/$tag" "$tag"
  fi
  git tag -f "$tag" "${NEW[$tag]}"
done
backups=$(for tag in "${!NEW[@]}"; do git rev-parse -q --verify "refs/tags/v4/$tag" >/dev/null && printf 'refs/tags/v4/%s ' "$tag"; done)
[ -z "$backups" ] || git push origin $backups
git push --force origin $(printf 'refs/tags/%s ' "${!NEW[@]}")
