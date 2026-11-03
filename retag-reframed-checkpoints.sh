#!/usr/bin/env bash
# Move the course checkpoint tags (3 November 2026, second rebuild): from lesson-03 on, a model request
# that fails (rate limit, outage, timeout, a refused tool call) is still recorded as a model event with
# its model, host, elapsed time and failure code, so the console's run page shows a failed live run as a
# live run. One assertion was added to a real-model test in test_lesson03.py, so the counts stay 1, 7,
# 12, 17, 19, 21, 29, 31, 37, 41, 47, 52, 55 and the capstone numbers are unchanged. The previous
# checkpoints are kept as v7/* tags first (v1/*..v6/* hold the earlier rebuilds), so this is reversible
# and idempotent.
# Run from a clone that has fetched main.
set -euo pipefail
git fetch origin main
git fetch --force origin "+refs/tags/*:refs/tags/*"
declare -A NEW=(
  [lesson-00]=827c1c8af99138d63156727645fd8044aa1db9c3
  [lesson-01]=7133fdcc650f04f22cacf233ff87679131b0e1b5
  [lesson-02]=7bbf4afb75ac73529462e7075c0ebc6ea962fa29
  [lesson-03]=3a81f99826b6ffd92f4d938aee7acc487e41022d
  [lesson-04]=894ce9cf9cb3d4b6673d47f2a60b2c53613a08a8
  [lesson-05]=f87520b24e673044c763601958c2ede454f1d22d
  [lesson-06]=d3838203a8be01d121c31488e9661fdf8ba742b1
  [lesson-07]=248bb9ca6ee05628c514b7902bd2092b6aed2071
  [lesson-08]=09c1dfe6a678f6858aeedee835ce1c8d8fbd37fe
  [lesson-09]=be8a59145dedfad3aaeff749ad5237da853ff34a
  [lesson-10]=37625176e0cab2d6525c34a660f5dbcf5850f66a
  [lesson-11]=9684c6bd1faa8fd87b16e64918e2d8bc77b11373
  [lesson-12]=7eba00ae60906c931a74de8273ad89bed338836b
  [course-complete]=06b73958a61c7bb2130311c2ad0bbd91be67b068
)
for tag in "${!NEW[@]}"; do
  if ! git rev-parse -q --verify "refs/tags/v7/$tag" >/dev/null; then
    [ "$(git rev-parse "$tag^{commit}")" = "${NEW[$tag]}" ] || git tag "v7/$tag" "$tag"
  fi
  git tag -f "$tag" "${NEW[$tag]}"
done
backups=$(for tag in "${!NEW[@]}"; do git rev-parse -q --verify "refs/tags/v7/$tag" >/dev/null && printf 'refs/tags/v7/%s ' "$tag"; done)
[ -z "$backups" ] || git push origin $backups
git push --force origin $(printf 'refs/tags/%s ' "${!NEW[@]}")
