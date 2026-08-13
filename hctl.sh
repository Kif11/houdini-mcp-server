#!/bin/sh
# hctl - CLI for Houdini RPC service
# Requires: curl
#
# Usage:
#   hctl exec "hou.node('/obj').createNode('box')"
#   hctl scene
#   hctl dot /obj/geo1
#   hctl errors /obj
#
# Environment:
#   HOUDINI_URL  - RPC endpoint (default: http://localhost:9876)

set -e

URL="${HOUDINI_URL:-http://localhost:9876}"

die() { echo "hctl: $*" >&2; exit 1; }

require_cmd() {
    command -v "$1" >/dev/null 2>&1 || die "'$1' is required but not installed"
}

require_cmd curl

case "${1:-}" in
    exec)
        [ -n "${2:-}" ] || die "usage: hctl exec <python-code>"
        curl -sf -X POST "$URL/exec" -d "$2"
        ;;
    scene)
        curl -sf "$URL/scene"
        ;;
    dot)
        ctx="${2:-/obj}"
        curl -sf "$URL/dot?path=$ctx"
        ;;
    errors)
        ctx="${2:-/obj}"
        curl -sf "$URL/errors?path=$ctx"
        ;;
    *)
        cat <<EOF
hctl - control a running Houdini instance

Usage:
  hctl exec <code>    execute Python in Houdini (quote the string)
  hctl scene          show scene info (hip, frames, selection)
  hctl dot [path]     network as Graphviz DOT graph (default: /obj)
  hctl errors [path]  list node errors (default: /obj)

Raw curl:
  curl http://localhost:9876/scene
  curl -X POST http://localhost:9876/exec -d "hou.hipFile.path()"

Environment:
  HOUDINI_URL  RPC endpoint (default: http://localhost:9876)
EOF
        exit 0
        ;;
esac
