from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound, VideoUnavailable
from langchain_core.documents import Document


def load_youtube(video_id: str):
    try:
        transcript = YouTubeTranscriptApi.get_transcript(
            video_id
        )

        text = "\n".join(
            item["text"]
            for item in transcript
        )

        documents = [
            Document(
                page_content=text,
                metadata={
                    "video_id": video_id
                }
            )
        ]

        return documents
    except TranscriptsDisabled:
        raise ValueError("Transcripts are disabled for this YouTube video. Please try another video.")
    except NoTranscriptFound:
        raise ValueError("No transcript was found for this video. Please upload a notes file instead.")
    except VideoUnavailable:
        raise ValueError("The requested video is unavailable or does not exist.")
    except Exception as e:
        raise ValueError(f"YouTube transcript error: {str(e)}")