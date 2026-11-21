---
name: demo-gif
description: Record the README terminal demo docs/images/demo.gif with VHS in a container. Use to make or update the demo GIF.
---

# Demo GIF

`docs/images/demo.gif` shows a knowit session in a terminal. VHS records it in a container:

- `scripts/demo.tape`: the session that VHS types and records. It is the source of the current GIF.
- `scripts/demo.Dockerfile`: the released knowit image from Docker Hub, plus VHS, ttyd, and Chromium. So the
  GIF shows a released version, not a dev version.
- `scripts/demo.sh`: pulls the released image, builds the VHS image, mounts the repository on `/repo`, and
  records.

The tape uses `test5.mkv` of the Matroska test files. The user gives no file. The tests download these
files, and git ignores them. If the file is missing, `scripts/demo.sh` stops. Run `uv run pytest -q tests`
first.

## 1. Edit the tape

Change only the lines that you must change: the tracks of the copy, or the `knowit` command.

- Keep the hidden setup at the top. It makes a small copy with mkvmerge (1 video, 1 audio, and 2 subtitle
  tracks, no statistics tags), goes to `/tmp/demo`, and sets the prompt to `$ `. The GIF must not show a
  path of the host.
- Keep the `Wait+Line` before `Show`. The setup is slow through the mount of the Podman machine. Without the
  wait, the first frames show the hidden command.
- All the output must fit on one screen. If it does not, remove tracks from the copy, or change
  `Set Height` and `Set FontSize`. Do not let the output scroll.

## 2. Record

1. On Windows or macOS, start the Podman machine: `podman machine start`. It is not an error if it runs
   already.
2. From the repository root, run `bash scripts/demo.sh`. The first build takes some minutes. The next runs
   take about 1 minute.
3. The output ends with `Creating docs/images/demo.gif...`. If it ends with `recording failed`, read the
   last value that VHS shows.

Known problems that the scripts already solve:

- Debian has no `ttyd` package. `scripts/demo.Dockerfile` downloads the static binary.
- Git Bash changes `/repo` into a Windows path. `scripts/demo.sh` sets `MSYS_NO_PATHCONV=1`.
- Podman on WSL fails with "controller `pids` is not available". `scripts/demo.sh` adds
  `--cgroups=disabled` for Podman.
- `Wait+Screen` reads the screen from the top. The tape waits for the `$ ` prompt line with `Wait+Line`.
- VHS records fewer frames than planned in the container. A `Sleep 20s` gives about 8 s in the GIF.

## 3. Check the frames

Save some frames as PNG, then read them:

```
uv run --no-project --with pillow python -c "
from PIL import Image
im = Image.open('docs/images/demo.gif')
n = im.n_frames
print(im.size, n, 'frames', sum((im.seek(i), im.info.get('duration', 0))[1] for i in range(n)) / 1000, 's')
for k, f in enumerate(range(0, n, n // 8)):
    im.seek(f)
    im.convert('RGB').save(f'plans/demo-gif/frame{k}.png')
"
```

Look for these problems:

- The last screen stays less than about 8 s: increase the last `Sleep`.
- A path of the host, or a command of the hidden setup, is in a frame.
- The GIF is more than about 2 MB or 30 s.

Record again after each change. Delete the PNG files when you are done.

## 4. Finish

1. Show some frames to the user, with the size and the duration of the GIF.
2. `README.md` shows `docs/images/demo.gif` with an absolute `raw.githubusercontent.com` URL, so that PyPI
   shows it too. Change its alt text if the content changed.
3. Record again after each release, so that the GIF shows the new version.
4. To commit, use the `ship` skill. Commit `docs/images/demo.gif` and `scripts/demo.tape` together.
