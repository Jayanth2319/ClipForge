import os
import tempfile
import streamlit as st
from dotenv import load_dotenv

# Import custom modules
from peak_detector import get_peak_segments
from transcriber import transcribe_audio
from gemini_engine import analyze_transcript
from face_tracker import get_face_center_x
from video_processor import process_video

# Load environment variables
load_dotenv()

st.set_page_config(page_title="ClipForge", page_icon="✂️", layout="centered")

def main():
    st.title("ClipForge - AI Video Repurposing Engine")
    st.subheader("Turn long videos into viral 60 second shorts")

    # File uploader
    uploaded_file = st.file_uploader("Upload a video", type=["mp4", "mov", "avi"])

    if uploaded_file is not None:
        st.video(uploaded_file)
        
        if st.button("Process Video", use_container_width=True, type="primary"):
            # Check for API key
            if not os.getenv("GEMINI_API_KEY"):
                st.error("GEMINI_API_KEY is not set in the .env file. Please add your key to proceed.")
                return

            with st.spinner("Setting up workspaces..."):
                # Save uploaded file to a temporary location
                temp_dir = tempfile.mkdtemp()
                temp_video_path = os.path.join(temp_dir, uploaded_file.name)
                with open(temp_video_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                    
            # Setup Progress Bar
            progress_bar = st.progress(0)
            status_text = st.empty()

            try:
                # Step 1: Detect Emotional Peaks (and Extract Audio internally)
                status_text.info("Extracting Audio & Detecting Emotional Peaks...")
                progress_bar.progress(10)
                peaks = get_peak_segments(temp_video_path, num_segments=3, segment_duration=60)
                
                if not peaks:
                    st.error("Failed to detect audio peaks or video is too short/silent.")
                    return
                print(f"Detected peaks: {peaks}")

                # Step 2: Transcribe Video
                status_text.info("Transcribing Video...")
                progress_bar.progress(35)
                transcript_data = transcribe_audio(temp_video_path)
                
                transcript_text = transcript_data.get("text", "")
                if not transcript_text:
                    st.error("Failed to transcribe audio or audio contains no speech.")
                    return

                # Step 3: Analyze with Gemini AI
                status_text.info("Analyzing with Gemini AI...")
                progress_bar.progress(60)
                analysis = analyze_transcript(transcript_text, peaks)
                
                if not analysis:
                    st.error("Gemini AI failed to analyze the transcript. Check the console for errors.")
                    return
                
                best_segment = analysis.get("best_segment", {})
                hook_headline = analysis.get("hook_headline", "Viral Moment")
                captions = analysis.get("captions", [])
                reasoning = analysis.get("reasoning", "This segment has high emotional impact.")
                
                start_time = best_segment.get("start", 0)
                end_time = best_segment.get("end", 60)

                # Step 4: Tracking Face
                status_text.info("Tracking Face Position...")
                progress_bar.progress(75)
                face_x_ratio = get_face_center_x(temp_video_path, start_time)

                # Step 5: Processing Video
                status_text.info("Processing Video...")
                progress_bar.progress(85)
                output_video_path = process_video(
                    video_path=temp_video_path,
                    start_time=start_time,
                    end_time=end_time,
                    face_x_ratio=face_x_ratio,
                    hook_headline=hook_headline,
                    captions=captions
                )

                if not output_video_path or not os.path.exists(output_video_path):
                    st.error("Video processing failed.")
                    return

                # Step 6: Done
                status_text.success("Done!")
                progress_bar.progress(100)

                # Display Results
                st.divider()
                st.markdown(f"<h1 style='text-align: center; color: #ff4b4b;'>{hook_headline}</h1>", unsafe_allow_html=True)
                
                st.markdown("### Initial Peak Detections")
                for i, (p_start, p_end) in enumerate(peaks):
                    st.write(f"**Peak {i+1}:** {p_start:.1f}s to {p_end:.1f}s")
                    
                st.markdown("### Gemini AI Reasoning")
                st.info(reasoning)

                st.markdown("### Final Processed Video")
                st.video(output_video_path)
                
                # Download Button
                with open(output_video_path, "rb") as file:
                    st.download_button(
                        label="Download MP4",
                        data=file,
                        file_name=f"viral_short_{uploaded_file.name}",
                        mime="video/mp4",
                        type="primary",
                        use_container_width=True
                    )

            except Exception as e:
                st.error(f"An unexpected error occurred: {e}")
            
            finally:
                # Cleanup
                if os.path.exists(temp_video_path):
                    try:
                        os.remove(temp_video_path)
                        os.rmdir(temp_dir)
                    except Exception as cleanup_error:
                        print(f"Could not delete temp files: {cleanup_error}")

if __name__ == "__main__":
    main()
