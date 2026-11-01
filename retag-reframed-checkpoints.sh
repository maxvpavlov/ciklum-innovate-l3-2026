#!/usr/bin/env bash
# Move the course checkpoint tags (1 November 2026): from lesson-03 on the runtime is hardened for a real
# model (a bare-JSON instruction, a fenced answer accepted, named provider failures) and every model event
# records the model, its host and the call time, which the console's run page shows. Two new tests in
# test_lesson03.py, so the counts are 1, 7, 12, 17, 19, 21, 29, 31, 37, 41, 47, 52, 55; other numbers are
# unchanged. The previous checkpoints are kept as v5/* tags first (v1/*..v4/* hold the earlier rebuilds),
# so this is reversible and idempotent.
# Run from a clone that has fetched claude/clever-tesla-bnbyzh (or main after merging it).
set -euo pipefail
git fetch origin claude/clever-tesla-bnbyzh
git fetch --force origin "+refs/tags/*:refs/tags/*"
declare -A NEW=(
  [lesson-00]=827c1c8af99138d63156727645fd8044aa1db9c3
  [lesson-01]=7133fdcc650f04f22cacf233ff87679131b0e1b5
  [lesson-02]=7bbf4afb75ac73529462e7075c0ebc6ea962fa29
  [lesson-03]=35b3d32883dc4f087ce6e7bd05e684c93656bbc9
  [lesson-04]=080692190d1d8c4a7e6503154c0b8b7e58de4fc5
  [lesson-05]=8b56a930db1709b710725ea1b6062a3495920204
  [lesson-06]=c38ed9f31bb95f807228ba2d6d07ee88b67ff26d
  [lesson-07]=1f65387cf7c87efe8180ceb5b3f6803831cec7eb
  [lesson-08]=841cd77c0f7c2921523cd279eaf36e7013ac2fb7
  [lesson-09]=9e46a86675d83875f7fe94cb41d37ea8bb3216c7
  [lesson-10]=b410772d65d6f3cf041c2f81d17b1b5ef697a702
  [lesson-11]=637c1c27f4fb6adc92105416bd214c5180e016df
  [lesson-12]=2c253d69c26432b7b54692212a84fba18920dfe9
  [course-complete]=fb33101fffb60c380c5100a7bc55b63d6c0177e7
)
for tag in "${!NEW[@]}"; do
  if ! git rev-parse -q --verify "refs/tags/v5/$tag" >/dev/null; then
    [ "$(git rev-parse "$tag^{commit}")" = "${NEW[$tag]}" ] || git tag "v5/$tag" "$tag"
  fi
  git tag -f "$tag" "${NEW[$tag]}"
done
backups=$(for tag in "${!NEW[@]}"; do git rev-parse -q --verify "refs/tags/v5/$tag" >/dev/null && printf 'refs/tags/v5/%s ' "$tag"; done)
[ -z "$backups" ] || git push origin $backups
git push --force origin $(printf 'refs/tags/%s ' "${!NEW[@]}")
