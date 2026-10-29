#!/usr/bin/env python3
"""Join the nearby warp recordings into one before/after comparison video.

The recordings live in src/, one per case:

    before.mp4    stock: the 10s Initiating Warp hold, then the tunnel
    after.mp4     modded: straight into the tunnel, no hold

The output holds both clips, before first. Each segment is labelled. The
cut is ten seconds apart by construction - the mod skips the hold and
nothing else - so there is no timer to find.

The video is re-encoded losslessly, so the result is bit identical to the
recordings apart from the overlay. The audio is re-encoded, because the
segments have to be joined and the sources are AAC.

Usage:
    python3 assets/combine.py            # lossless master, for upload
"""

import argparse
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "src")
FONT = os.path.join(HERE, "fonts", "GeosansLight-NMS.ttf")
OUT_DIR = os.path.join(HERE, "video")

# The clips, before first.
CLIPS = ["before", "after"]
CASES = [("Warp", "NEARBY WARP")]

FPS = 60
WIDTH, HEIGHT = 2560, 1440

# Overlay layout.
SPEED_X, SPEED_Y, SPEED_SIZE = 60, 44, 72
CASE_X, CASE_Y, CASE_SIZE = 64, 140, 30
AMBER = "0xFFC878"
WHITE = "0xFFFFFF"
EDGE = "borderw=2:bordercolor=0x000000@0.8"


def run(cmd):
    """Run a command, raising with its output on failure."""
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        raise SystemExit("%s failed:\n%s" % (" ".join(cmd[:3]), proc.stderr[-4000:]))
    return proc.stdout


def frame_count(clip):
    """Return the number of frames a recording holds."""
    out = run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-count_frames",
               "-show_entries", "stream=nb_read_frames", "-of", "csv=p=0", clip])
    return int(out.strip().split(",")[0])


def draw(text, x, y, size, colour):
    """A drawtext that draws the given text in the game's font."""
    return "drawtext=" + ":".join(["fontfile=%s" % FONT, "text='%s'" % text,
                                    "x=%s" % x, "y=%d" % y, "fontsize=%d" % size,
                                    "fontcolor=%s" % colour, EDGE])


def build_graph(segments):
    """Build the filter graph for the segments."""
    lines = []
    for index, segment in enumerate(segments):
        parts = [
            draw(segment["label"], SPEED_X, SPEED_Y, SPEED_SIZE, AMBER),
            draw(segment["case"], CASE_X, CASE_Y, CASE_SIZE, WHITE),
        ]
        # The frames are put back on a plain 60 fps timeline so the two
        # recordings play at the speed they were captured at.
        lines.append("[%d:v]setpts=N/(%d*TB),scale=%d:%d,setsar=1,%s[v%d];"
                     % (index, FPS, WIDTH, HEIGHT, ",".join(parts), index))
        lines.append("[%d:a]aresample=48000,aformat=sample_fmts=fltp:channel_layouts=stereo,"
                     "apad,atrim=end=%.6f,asetpts=N/SR/TB[a%d];"
                     % (index, segment["frames"] / float(FPS), index))
    chains = "".join("[v%d][a%d]" % (i, i) for i in range(len(segments)))
    lines.append("%sconcat=n=%d:v=1:a=1[outv][outa]" % (chains, len(segments)))
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default=None)
    args = parser.parse_args()

    if args.out is None:
        args.out = os.path.join(OUT_DIR, "warp-comparison.mp4")

    segments = []
    for clip_name in CLIPS:
        for case, label in CASES:
            clip = os.path.join(SRC, "%s.mp4" % clip_name)
            if not os.path.isfile(clip):
                raise SystemExit("missing recording: %s" % clip)
            segments.append({
                "clip": clip,
                "label": clip_name.upper(),
                "case": label,
                "frames": frame_count(clip),
            })
            print("%-22s %d frames" % (os.path.basename(clip),
                                        segments[-1]["frames"]))

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    graph = os.path.join(OUT_DIR, "filtergraph.txt")
    with open(graph, "w", encoding="utf-8") as handle:
        handle.write(build_graph(segments))

    cmd = ["ffmpeg", "-y", "-v", "error", "-vsync", "0"]
    for segment in segments:
        cmd += ["-i", segment["clip"]]
    cmd += ["-filter_complex_script", graph, "-map", "[outv]", "-map", "[outa]"]
    cmd += ["-c:v", "libx264", "-qp", "0", "-preset", "medium", "-pix_fmt", "yuv420p"]
    cmd += ["-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", args.out]
    run(cmd)

    size = os.path.getsize(args.out)
    print("wrote %s (%.1f MB, lossless)" % (args.out, size / 1048576.0))
    return 0


if __name__ == "__main__":
    sys.exit(main())
