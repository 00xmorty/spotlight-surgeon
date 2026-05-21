#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCRIPT="$ROOT_DIR/spotlight-surgeon"

fail() {
  echo "FAIL: $*" >&2
  exit 1
}

assert_contains() {
  local haystack="$1"
  local needle="$2"
  if [[ "$haystack" != *"$needle"* ]]; then
    echo "Output was:" >&2
    echo "$haystack" >&2
    fail "expected output to contain: $needle"
  fi
}

[[ -x "$SCRIPT" ]] || fail "script must exist and be executable"

help_output="$($SCRIPT help)"
assert_contains "$help_output" "Spotlight Surgeon"
assert_contains "$help_output" "doctor"
assert_contains "$help_output" "--dry-run"

version_output="$($SCRIPT --version)"
assert_contains "$version_output" "0.1.0"

status_output="$($SCRIPT status --dry-run)"
assert_contains "$status_output" "DRY RUN"
assert_contains "$status_output" "mdutil -s /"

apps_output="$($SCRIPT apps --dry-run)"
assert_contains "$apps_output" "DRY RUN"
assert_contains "$apps_output" "lsregister"

fix_output="$($SCRIPT fix --dry-run)"
assert_contains "$fix_output" "DRY RUN"
assert_contains "$fix_output" "mdutil -E /"

verify_output="$($SCRIPT verify Safari --dry-run)"
assert_contains "$verify_output" "DRY RUN"
assert_contains "$verify_output" "Safari"
assert_contains "$verify_output" "mdfind"

multiword_output="$($SCRIPT verify "Google Chrome" --dry-run)"
assert_contains "$multiword_output" "Google Chrome"

unknown_output="$($SCRIPT unknown 2>&1 || true)"
assert_contains "$unknown_output" "Unknown command"

echo "ok - spotlight-surgeon smoke tests passed"
