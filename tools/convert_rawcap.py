"""把旧格式 rawcap 录像转成统一录像格式，供 CaptureFileCamera 回放。

Convert an old-format rawcap recording into the unified recording format that
CaptureFileCamera replays.

旧格式：frames.csv 为 frame,dev_ts,host_ms；session.txt 的 offset_x/offset_y 是跳采后的
像素，decimation 为跳采倍数；没有 IMU。设备时间戳的单位由整段录像的设备时间与主机时间
之比定出（取最近的 10 的幂）。PGM 不变，以硬链接（不支持时复制）放进输出目录。

Old format: frames.csv holds frame,dev_ts,host_ms; offset_x/offset_y in session.txt are
in decimated pixels and decimation is the skip factor; there is no IMU. The unit of the
device timestamp follows from the ratio of device to host time over the recording (the
nearest power of ten). The PGM files stay unchanged and are hard-linked (copied where
links are not supported) into the output directory.

  python convert_rawcap.py OLD_DIR NEW_DIR
"""
import csv
import math
import os
import shutil
import sys


def read_session(path):
    values = {}
    with open(path) as f:
        for line in f:
            parts = line.split()
            if len(parts) >= 2:
                values[parts[0]] = parts[1]
    return values


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) != 2:
        sys.exit(__doc__.strip().splitlines()[-1])
    old, new = argv
    session = read_session(os.path.join(old, "session.txt"))
    decimation = int(session.get("decimation", "1"))
    roi_x = int(session.get("offset_x", "0")) * decimation
    roi_y = int(session.get("offset_y", "0")) * decimation
    with open(os.path.join(old, "frames.csv"), newline="") as f:
        rows = [(int(r["frame"]), int(r["dev_ts"]), int(r["host_ms"])) for r in csv.DictReader(f)]
    if len(rows) < 2:
        sys.exit("need at least two frames")
    host_us = (rows[-1][2] - rows[0][2]) * 1000
    ticks_per_us = 10 ** round(math.log10((rows[-1][1] - rows[0][1]) / host_us))

    os.makedirs(new, exist_ok=True)
    with open(os.path.join(new, "frames.csv"), "w", newline="") as f:
        f.write("frame,timestamp_us,frame_counter,roi_x,roi_y,decimation\n")
        for i, (frame, dev_ts, _) in enumerate(rows):
            src = os.path.join(old, f"{frame:06d}.pgm")
            dst = os.path.join(new, f"{i:06d}.pgm")
            if not os.path.exists(dst):
                try:
                    os.link(src, dst)
                except OSError:
                    shutil.copyfile(src, dst)
            t_us = (dev_ts - rows[0][1]) // ticks_per_us
            f.write(f"{i},{t_us},{frame},{roi_x},{roi_y},{decimation}\n")
    with open(os.path.join(new, "session.txt"), "w") as f:
        f.write(f"converted_from {os.path.abspath(old)}\n")
        f.write(f"device_ticks_per_us {ticks_per_us}\n")
        for key, value in session.items():
            f.write(f"{key} {value}\n")
    print(f"{len(rows)} frames, roi {roi_x},{roi_y}, decimation {decimation}, "
          f"{ticks_per_us} device ticks per us -> {new}")


if __name__ == "__main__":
    main()
