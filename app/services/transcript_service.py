from youtube_transcript_api import YouTubeTranscriptApi
from typing import Optional

def get_video_transcript(video_id: str) -> Optional[str]:
    """
    Fetches the transcript for a given YouTube video ID.
    Returns the full transcript as a single string.
    
    Args:
        video_id (str): The YouTube video ID (e.g., 'T-kiZ_K1XtY').
        
    Returns:
        Optional[str]: The full transcript text, or None if not found/error.
    """
    try:
        # Use the API to fetch the transcript object
        ytt=YouTubeTranscriptApi()
        transcript = ytt.fetch(video_id)

        print("the transcript is ", transcript)
        
        # Convert to raw data (list of dicts) to avoid 'not subscriptable' error
        # with newer library versions
        transcript_list = transcript.to_raw_data()
        
        # Combine all parts into one text
        full_text = " ".join([t['text'] for t in transcript_list])
        return full_text
    except Exception as e:
        print(f"Could not retrieve transcript for video {video_id}: {e}")
        return None

if __name__ == "__main__":
    # Simple test
    test_id = "1fu2X4MSCPQ"
    print(f"Fetching transcript for {test_id}...")
    text = get_video_transcript(test_id)
    if text:
        print(f"Success! Length: {len(text)} chars")
        print(f"Preview: {text[:]}...")
    else:
        print("Failed to get transcript.")
