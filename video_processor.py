import os
from moviepy import VideoFileClip, TextClip, CompositeVideoClip

def process_video(video_path, start_time, end_time, face_x_ratio, hook_headline, captions):
    """
    Cuts the video, crops to 9:16 aspect ratio centered on face,
    and burns the hook headline and captions into the video.
    """
    try:
        print(f"Processing video from {start_time} to {end_time}...")
        clip = VideoFileClip(video_path).subclipped(start_time, end_time)
        
        # Calculate crop dimensions for 9:16 aspect ratio
        w, h = clip.size
        # 9:16 ratio means width = height * 9/16
        target_w = int(h * 9 / 16)
        
        # Calculate center based on face ratio
        center_x = int(w * face_x_ratio)
        
        # Determine x1 and x2 for cropping
        x1 = int(center_x - (target_w / 2))
        x2 = int(center_x + (target_w / 2))
        
        # Boundary checks
        if x1 < 0:
            x1 = 0
            x2 = target_w
        if x2 > w:
            x2 = w
            x1 = w - target_w
            
        print(f"Cropping video to {target_w}x{h} based on face position...")
        # Crop to 9:16
        cropped_clip = clip.cropped(x1=x1, y1=0, x2=x2, y2=h)
        
        # Generate Text Clips
        text_clips = []
        
        # 1. Hook Headline (First 3 seconds, top)
        if hook_headline:
            print("Creating hook headline text clip...")
            hook_txt = TextClip(
                text=hook_headline,
                font_size=75,
                color='white',
                font='Arial',
                stroke_color='black',
                stroke_width=2,
                method='caption',
                size=(target_w - 60, None),
                text_align='center'
            )
            hook_clip = hook_txt.with_position(('center', 100)).with_duration(min(3, cropped_clip.duration))
            text_clips.append(hook_clip)
            
        # 2. Captions (bottom center)
        if captions:
            print("Creating caption text clips...")
            for caption in captions:
                cap_start = caption.get('start', 0)
                cap_end = caption.get('end', 0)
                cap_text = caption.get('text', '')
                
                if not cap_text:
                    continue
                    
                # Adjust time if it's absolute from the original video
                if cap_start >= start_time:
                    rel_start = cap_start - start_time
                    rel_end = cap_end - start_time
                else:
                    # It might already be relative
                    rel_start = cap_start
                    rel_end = cap_end
                
                # Make sure duration is sensible and within clip length
                rel_start = max(0, min(rel_start, cropped_clip.duration))
                rel_end = max(0, min(rel_end, cropped_clip.duration))
                cap_duration = rel_end - rel_start
                
                if cap_duration <= 0:
                    continue
                    
                cap_txt = TextClip(
                    text=cap_text,
                    font_size=60,
                    color='white',
                    font='Arial',
                    stroke_color='black',
                    stroke_width=2,
                    method='caption',
                    size=(target_w - 60, None),
                    text_align='center'
                )
                
                cap_clip = cap_txt.with_position(('center', h - 300)) \
                                  .with_start(rel_start) \
                                  .with_duration(cap_duration)
                text_clips.append(cap_clip)

        # Composite video
        print("Compositing final video...")
        final_video = CompositeVideoClip([cropped_clip] + text_clips)
        
        # Make sure output directory exists
        out_dir = os.path.join(os.path.dirname(video_path), "output")
        os.makedirs(out_dir, exist_ok=True)
        
        # Output filename
        base_name = os.path.splitext(os.path.basename(video_path))[0]
        out_path = os.path.join(out_dir, f"{base_name}_viral_short.mp4")
        
        print(f"Exporting final video to {out_path}...")
        final_video.write_videofile(
            out_path,
            fps=clip.fps,
            codec="libx264",
            audio_codec="aac",
            threads=4,
            logger=None
        )
        
        clip.close()
        cropped_clip.close()
        final_video.close()
        
        return out_path
        
    except Exception as e:
        print(f"Error in video processor: {e}")
        return None
