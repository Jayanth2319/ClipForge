import os
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip

def process_video(video_path, start_time, end_time, face_x_ratio, hook_headline, captions):
    try:
        print(f"Processing video from {start_time} to {end_time}...")
        os.makedirs("output", exist_ok=True)
        video = VideoFileClip(video_path)

        end_time = min(end_time, video.duration - 0.1)
        start_time = max(0, start_time)
        clip = video.subclip(start_time, end_time)

        w, h = clip.size
        target_w = int(h * 9 / 16)

        if target_w >= w:
            # Video is already narrow, no crop needed
            final_clip = clip
        else:
            # Center crop always — ignore face ratio for now
            x1 = (w - target_w) // 2
            x2 = x1 + target_w
            final_clip = clip.crop(x1=x1, y1=0, x2=x2, y2=h)

        # Add captions
        try:
            text_clips = [final_clip]

            headline = TextClip(
                hook_headline,
                fontsize=35,
                color="white",
                stroke_color="black",
                stroke_width=2,
                method="caption",
                size=(final_clip.w, None)
            ).set_duration(3).set_position(("center", 40))
            text_clips.append(headline)

            for cap in captions:
                cap_start = cap["start"] - start_time
                cap_end = cap["end"] - start_time
                cap_start = max(0, cap_start)
                cap_end = min(final_clip.duration, cap_end)
                if cap_end <= cap_start:
                    continue
                txt = TextClip(
                    cap["text"],
                    fontsize=30,
                    color="white",
                    stroke_color="black",
                    stroke_width=2,
                    method="caption",
                    size=(final_clip.w, None)
                ).set_start(cap_start).set_end(cap_end).set_position(("center", h - 80))
                text_clips.append(txt)

            final = CompositeVideoClip(text_clips)
        except Exception as e:
            print(f"Caption error: {e}, exporting without captions")
            final = final_clip

        output_path = os.path.join("output", "clipforge_output.mp4")
        final.write_videofile(
            output_path,
            codec="libx264",
            audio_codec="aac",
            logger=None
        )
        video.close()
        return output_path

    except Exception as e:
        print(f"Error in video processor: {e}")
        return None
