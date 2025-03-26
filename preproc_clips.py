import os
import re
import subprocess

VIDEO_FILE = "output.mp4"
OUTPUT_DIR = "clips"
SCENE_THRESHOLD = 0.3  # Adjust based on previous test

def detect_scenes(video_path, threshold):
    """Run FFmpeg scene detection and extract timestamps."""
    command = [
        "ffmpeg", "-i", video_path, "-vf", f"select='gt(scene,{threshold})',showinfo",
        "-vsync", "vfr", "-f", "null", "-"
    ]
    result = subprocess.run(command, stderr=subprocess.PIPE, text=True)

    timestamps = []
    for line in result.stderr.splitlines():
        match = re.search(r"pts_time:([\d.]+)", line)
        if match:
            timestamps.append(float(match.group(1)))

    return timestamps

def split_video(video_path, timestamps, output_dir):
    """Splits video into clips based on detected scene changes."""
    os.makedirs(output_dir, exist_ok=True)
    clip_paths = []

    for i, (start, end) in enumerate(zip(timestamps, timestamps[1:] + [None])):
        output_file = os.path.join(output_dir, f"clip_{i}.mp4")
        command = ["ffmpeg", "-i", video_path, "-ss", str(start)]
        
        if end is not None:
            command += ["-to", str(end)]
        
        command += ["-c", "copy", output_file]

        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        if result.returncode == 0:
            clip_paths.append(output_file)
        else:
            print(f"Error processing clip {i}: {result.stderr}")

    return clip_paths

if __name__ == "__main__":
    print("Detecting scene changes...")
    scene_timestamps = detect_scenes(VIDEO_FILE, SCENE_THRESHOLD)
    print(f"Detected scene changes at: {scene_timestamps}")

    if not scene_timestamps:
        print("No scene changes detected. Try lowering SCENE_THRESHOLD.")
        exit(0)

    print("Splitting video into original shots...")
    clips = split_video(VIDEO_FILE, scene_timestamps, OUTPUT_DIR)
    print("Saved clips:", clips)