# Report a problem and help to improve knowit

This page is for knowit users. It tells how to send the information that the maintainer needs to fix a
problem. You do not need to send your media files.

## Report a problem

Do not send your media file. It is not needed, and it is usually too large.
Run this command instead:

    $ knowit --bug-report "/path/to/your/video.mkv"
    Bug report written to knowit-report.yml

Attach `knowit-report.yml` to an issue at
<https://github.com/ratoaq2/knowit/issues>.

The report contains:

- the knowit version, and where knowit is installed from
- the Python version, the operating system, and the text encodings in use
- the location and version of MediaInfo, ffprobe, mkvmerge and enzyme
- the non-ascii symbols of the file path, with their Unicode names, and its text encoding facts
- the raw output of every installed provider for that file
- the values knowit parsed from that output, or the error it failed with

Titles, file names and free-text tags are masked. Letters and digits of every
script are masked. Symbols, such as `–` or `™`, are kept, because they are often
the cause of the problem. Technical tags, such as the track language, are kept.
Use `--no-redact` to keep the original text.

If knowit is bundled in another application, run the command with the same Python that runs that
application:

    $ python -m knowit --bug-report "/path/to/your/video.mkv"

If a codec, a profile or another value is not known by knowit, use `--report`
instead. It accepts a directory and lists every value knowit does not know:

    $ knowit --report /path/to/your/media

## Problems with a file name

Many problems come from the name of the file, not from its content: a superscript,
a fraction, an accent, or a character the file system encoding cannot represent.
For those, only the name is needed:

    $ knowit --check-name "The Accountant² (2025).mkv"

knowit writes a small generated Matroska file under that name, and also under a
plain ascii name. It then compares the two results:

    result:
      mediainfo: ok: the name is handled correctly
      ffmpeg: ok: the name is handled correctly
      mkvmerge: ok: the name is handled correctly
      enzyme: fails with this name only: the name is the problem

A provider that fails only with your name has a name handling problem. A provider
that fails with both names has a problem with the file content instead, and the
name is not the cause.

The generated sample holds one audio track, so all four providers read it. If a
provider reports a failure for both names on your system, that provider cannot
read the sample at all, and its line says nothing about your file name.

Add a file to use your own media as the sample:

    $ knowit --check-name "The Accountant² (2025).mkv" /path/to/any/video.mkv

## Help to improve knowit

knowit is more correct when it sees many different files. You can send the
output of the providers for your whole library. Your media is not needed:

    $ knowit --collect /path/to/your/media

This writes `knowit-collect.jsonl.gz`. It uses all installed providers. Use
`-p` to use only one. Titles, file names and free-text tags are masked, as in a
bug report. Use `-o` to write to a different file.

A large library takes some time. You can stop the scan with Ctrl+C. Run the same
command again to continue: files that did not change are not read again.

Add `--deep` to also read the first video frames with ffprobe. This finds HDR10+
and Dolby Vision data, but it is slower.

At the end, knowit shows a summary with the values it does not know. When a
file becomes too large to attach to an issue, knowit continues in a new file
(`knowit-collect.part2.jsonl.gz`, and so on). Attach all the files to an issue at
<https://github.com/ratoaq2/knowit/issues>.
