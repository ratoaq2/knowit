# Record with scripts/demo.sh
Output docs/images/demo.gif

Set Shell "bash"
Set FontSize 15
Set Width 760
Set Height 1000
Set Padding 20
Set Theme "Dracula"
Set TypingSpeed 60ms

# A small copy of a test video: 1 video, 1 audio, and 2 subtitle tracks
Hide
Type "mkdir -p /tmp/demo && cd /tmp/demo && mkvmerge -q -o movie.mkv -a 1 -s 2,5 --disable-track-statistics-tags /repo/tests/data/videos/test5.mkv && export PS1='$ ' && clear"
Enter
Wait+Line@60s /^\$ *$/
Show

Sleep 500ms
Type "knowit -y -P human movie.mkv"
Sleep 500ms
Enter
Wait+Line@60s /^\$ *$/
Sleep 20s
