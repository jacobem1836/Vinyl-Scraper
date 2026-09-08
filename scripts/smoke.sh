#!/usr/bin/env bash
# Production smoke test: scripts/smoke.sh https://crate.fly.dev
set -euo pipefail
BASE="${1:?usage: smoke.sh <base-url>}"
fail=0
check() { # path expected-status [grep-pattern]
  local code body
  body=$(curl -sS --max-time 20 -o /tmp/smoke_body -w '%{http_code}' -H 'Accept: text/html' "$BASE$1") || { echo "FAIL $1: curl error"; fail=1; return; }
  if [[ "$body" != "$2" ]]; then echo "FAIL $1: got $body want $2"; fail=1; return; fi
  if [[ -n "${3:-}" ]] && ! grep -q "$3" /tmp/smoke_body; then echo "FAIL $1: missing '$3'"; fail=1; return; fi
  echo "ok   $1 -> $2"
}
check /api/health 200 '"ok"'
check / 200 'CRATE'
check /login 200 'csrf_token'
check /signup 200 'csrf_token'
check /privacy 200 'session cookie'
check /forgot-password 200 'csrf_token'
check /account 303
check /item/1 303
check /api/scan/status 401
check /docs 404
hdrs=$(curl -sSI --max-time 20 "$BASE/login")
hdr_list="content-security-policy x-frame-options"; [[ "$BASE" == https://* ]] && hdr_list="$hdr_list strict-transport-security"
for h in $hdr_list; do
  echo "$hdrs" | grep -qi "^$h:" && echo "ok   header $h" || { echo "FAIL header $h"; fail=1; }
done
echo "$hdrs" | grep -qi "set-cookie:.*secure" && echo "ok   cookie Secure" || echo "note no session cookie set on GET (fine)"
exit $fail
