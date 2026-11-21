#!/bin/bash
# Record docs/images/demo.gif with VHS in a container, with the released knowit image and a test video.
# Usage: scripts/demo.sh. See the demo-gif skill.

set -e

# Git Bash: do not change the container paths into Windows paths
export MSYS_NO_PATHCONV=1

# The tests download the Matroska test files to tests/data/videos
if [[ ! -f tests/data/videos/test5.mkv ]]; then
    echo "tests/data/videos/test5.mkv is missing. Run 'uv run pytest -q tests' first." >&2
    exit 1
fi

repo=$(pwd -W 2>/dev/null || pwd)
engine=$(command -v podman || command -v docker)
# Podman on WSL: crun fails with "controller `pids` is not available"
opts=()
[[ "$engine" == *podman* ]] && opts=(--cgroups=disabled)

"$engine" pull -q docker.io/ratoaq2/knowit:latest
"$engine" build -q --pull=never -t localhost/knowit-vhs -f scripts/demo.Dockerfile .
"$engine" run --rm "${opts[@]}" -v "$repo:/repo" -w /repo localhost/knowit-vhs scripts/demo.tape
