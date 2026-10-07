#!/usr/bin/env bash
# Validate the plugin and package it as dist/crm-brain.plugin
# Usage: ./scripts/build.sh
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PLUGIN="$ROOT/plugins/crm-brain"
fail=0

echo "== manifest"
python3 - "$PLUGIN" <<'PY'
import json, re, sys
p = sys.argv[1]
d = json.load(open(f"{p}/.claude-plugin/plugin.json"))
assert re.fullmatch(r"[a-z0-9-]+", d["name"]), "name must be kebab-case"
assert re.fullmatch(r"\d+\.\d+\.\d+", d["version"]), "version must be semver"
m = json.load(open(f"{p}/../../.claude-plugin/marketplace.json"))
names = [x["name"] for x in m["plugins"]]
assert d["name"] in names, "marketplace entry name must equal plugin.json name"
print("ok", d["name"], d["version"])
PY

echo "== skills"
python3 - "$PLUGIN" <<'PY' || fail=1
import glob, os, re, sys, yaml
bad = 0
for f in sorted(glob.glob(f"{sys.argv[1]}/skills/*/SKILL.md")):
    folder = os.path.basename(os.path.dirname(f))
    fm = yaml.safe_load(open(f).read().split("---")[1])
    desc = fm["description"]
    problems = []
    if fm["name"] != folder:
        problems.append(f"name '{fm['name']}' != folder '{folder}'")
    # Validators reject descriptions over 1024 characters
    if len(desc) > 1024:
        problems.append(f"description is {len(desc)} chars (max 1024)")
    # Validators read anything in angle brackets as an XML tag and reject the plugin
    if re.search(r"<[^>]*>", desc):
        problems.append("angle brackets in description, use [square] brackets")
    status = "ok " if not problems else "BAD"
    print(f"{status} {len(desc):4d}  {folder}  {'; '.join(problems)}")
    bad += bool(problems)
sys.exit(1 if bad else 0)
PY

[ "$fail" -eq 0 ] || { echo "Validation failed"; exit 1; }

mkdir -p "$ROOT/dist"
rm -f "$ROOT/dist/crm-brain.plugin"
(cd "$PLUGIN" && zip -rq "$ROOT/dist/crm-brain.plugin" . -x "*.DS_Store")
(cd "$ROOT" && zip -q "$ROOT/dist/crm-brain.plugin" LICENSE)
echo "== built dist/crm-brain.plugin"
