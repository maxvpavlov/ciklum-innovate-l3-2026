#!/usr/bin/env bash
# Move the course checkpoint tags (3 November 2026): from lesson-03 on the runtime is tuned for the course
# model on Groq. The system prompt spells out the tool procedure and the answer format, the given tool
# definitions describe every argument with an example, the final answer is the first JSON object in the
# reply, and HTTPProvider sends reasoning_effort from MODEL_REASONING_EFFORT and resends a request the
# endpoint refused with 400 tool_use_failed at most twice (then provider_tool_call_invalid). The two
# real-model tests in test_lesson03.py were extended, so the counts stay 1, 7, 12, 17, 19, 21, 29, 31, 37,
# 41, 47, 52, 55 and the other numbers are unchanged. The previous checkpoints are kept as v6/* tags first
# (v1/*..v5/* hold the earlier rebuilds), so this is reversible and idempotent.
# Run from a clone that has fetched main.
set -euo pipefail
git fetch origin main
git fetch --force origin "+refs/tags/*:refs/tags/*"
declare -A NEW=(
  [lesson-00]=827c1c8af99138d63156727645fd8044aa1db9c3
  [lesson-01]=7133fdcc650f04f22cacf233ff87679131b0e1b5
  [lesson-02]=7bbf4afb75ac73529462e7075c0ebc6ea962fa29
  [lesson-03]=b1c0f805b5e93c8bb59b455714104ba51d784c77
  [lesson-04]=62f1d583693c8c5c46975bbe7ecd582614ac9247
  [lesson-05]=57a168bb28c6ecfcc664ae41a40677d3386d58e0
  [lesson-06]=49b66df555272c4234805d7a195bdd7d53c53478
  [lesson-07]=e4c40a9b22825fd4ac376d6da1a62c2b4b749a84
  [lesson-08]=c13cb309ac24a31746553783c794bcfd6db30348
  [lesson-09]=8148776cc6db777f221658e0c1b045e9b0f3ad85
  [lesson-10]=980fac0585e9def0df1abf72176462bb2de5587b
  [lesson-11]=69be6dc3dad1f763d0ea459ce2df3186ac5b2b6d
  [lesson-12]=b0333df8ce0a79d9d8b05299bdeb850353ffb2ba
  [course-complete]=bf3b75d4a2bcb67f6a044aef56560017054bc3bd
)
for tag in "${!NEW[@]}"; do
  if ! git rev-parse -q --verify "refs/tags/v6/$tag" >/dev/null; then
    [ "$(git rev-parse "$tag^{commit}")" = "${NEW[$tag]}" ] || git tag "v6/$tag" "$tag"
  fi
  git tag -f "$tag" "${NEW[$tag]}"
done
backups=$(for tag in "${!NEW[@]}"; do git rev-parse -q --verify "refs/tags/v6/$tag" >/dev/null && printf 'refs/tags/v6/%s ' "$tag"; done)
[ -z "$backups" ] || git push origin $backups
git push --force origin $(printf 'refs/tags/%s ' "${!NEW[@]}")
