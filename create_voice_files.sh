#!/usr/bin/env bash

set -eauxo pipefail

OUTDIR=$1

test -d "$1"

mkdir -p "$OUTDIR/M"
mkdir -p "$OUTDIR/F"

function sound() {
    local filename=$1
    local voice=$2
    local letter=$3
    local response=$4

    test -f "$OUTDIR/$letter/$filename.mp3" && return

    say "$response" -o "$OUTDIR/$letter/$filename.aiff" -v "$voice"
    ffmpeg -i "$OUTDIR/$letter/$filename.aiff" -f mp3 -acodec libmp3lame -ab 64000 -ar 44100 "$OUTDIR/$letter/$filename.mp3" -nostdin
    rm "$OUTDIR/$letter/$filename.aiff"
}

while read line; do
    echo $line
    filename=`echo "$line" | cut -d'@' -f1`
    response=`echo "$line" | cut -d'@' -f2`

    sound "$filename" "Yuri" "M" "$response"
    sound "$filename" "Milena" "F" "$response"
done
