import ffmpeg

timestamps = {
    "Cardinals": (0, 26),
    "Lions": (27, 70),
    "Titans": (123, 128),
    "Chargers": (129, 153),
    "Browns": (154, 251),
    "Bills": (252, 293),
    "Jets": (303, 328),
    "Dolphins": (370, 420),
    "Raiders": (421, 449),
    "Bears": (450, 482),
    "Commanders": (483, 514),
    "Niners": (515, 543),
    "Cowboys": (555, 581),
    "Colts": (644, 669),
    "Steelers": (670, 687),
    "Saints": (688, 739),
    "Packers": (740, 760),
    "Giants": (761, 775),
    "Ravens": (776, 799),
    "Seahawks": (800, 847),
    "Broncos": (848, 876)
}

input_video = "full_video.mp4"

for team, (start, end) in timestamps.items():
    output = f"{team}.mp4"
    (
        ffmpeg
        .input(input_video, ss=start, to=end)
        .output(output, vcodec="libx264", acodec="aac", strict="experimental")  
        .overwrite_output()
        .run()
    )
    print(f"Created {output}")
