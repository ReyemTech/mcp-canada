#!/usr/bin/env bash
set -euo pipefail

# The Linux read-only sandbox uses unprivileged user namespaces on hosted runners.
if [ "$(sysctl -n kernel.unprivileged_userns_clone 2>/dev/null || true)" = '0' ]; then
  sudo sysctl -w kernel.unprivileged_userns_clone=1
fi
if [ "$(sysctl -n kernel.apparmor_restrict_unprivileged_userns 2>/dev/null || true)" = '1' ]; then
  sudo sysctl -w kernel.apparmor_restrict_unprivileged_userns=0
fi

sudo useradd --create-home --shell /bin/bash pr-reviewer
# Hosted runners can restrict a parent even when the checkout itself is readable.
# Grant traversal only; do not expose listings or grant writes to runner homes.
for target in "$GITHUB_WORKSPACE" "$RUNNER_TEMP"; do
  parent="$target"
  while [ "$parent" != / ]; do
    stat -c '%a %n' "$parent"
    sudo chmod a+x "$parent"
    parent="$(dirname "$parent")"
  done
done
chmod -R a+rX "$GITHUB_WORKSPACE"
sudo install -d -o "$(id -un)" -g pr-reviewer -m 0770 "$RUNNER_TEMP/pr-review"
sudo -H -u pr-reviewer git config --global --add safe.directory "$GITHUB_WORKSPACE"
