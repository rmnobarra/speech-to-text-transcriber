import os
import numpy as np
import torch
from pyannote.audio import Pipeline
from pydub import AudioSegment
import whisper

def transcribe_with_diarization(audio_file, model_size="base", num_speakers=None):
    """
    Transcribe audio with speaker diarization.
    
    Args:
        audio_file: Path to audio file
        model_size: Whisper model size
        num_speakers: Number of speakers (if known)
        
    Returns:
        Transcription with speaker labels
    """
    print("Loading diarization pipeline...")
    # Note: You need to get access to pyannote/speaker-diarization on HuggingFace
    # and set HUGGINGFACE_TOKEN environment variable
    diarization_pipeline = Pipeline.from_pretrained(
        "pyannote/speaker-diarization@2.1",
        use_auth_token=os.environ.get("HUGGINGFACE_TOKEN")
    )
    
    print("Loading Whisper model...")
    whisper_model = whisper.load_model(model_size)
    
    print("Transcribing audio...")
    result = whisper_model.transcribe(audio_file)
    segments = result["segments"]
    
    print("Performing speaker diarization...")
    # Run diarization
    diarization = diarization_pipeline(audio_file, num_speakers=num_speakers)
    
    # Convert diarization to speaker turns with timestamps
    speaker_turns = []
    for turn, _, speaker in diarization.itertracks(yield_label=True):
        speaker_turns.append({
            "start": turn.start,
            "end": turn.end,
            "speaker": speaker
        })
    
    # Assign speakers to transcription segments
    for segment in segments:
        segment_mid = (segment["start"] + segment["end"]) / 2
        # Find the speaker active at the middle of this segment
        for turn in speaker_turns:
            if turn["start"] <= segment_mid <= turn["end"]:
                segment["speaker"] = turn["speaker"]
                break
        else:
            segment["speaker"] = "UNKNOWN"
    
    # Format the final transcription with speaker labels
    transcript_with_speakers = ""
    current_speaker = None
    
    for segment in segments:
        if segment["speaker"] != current_speaker:
            current_speaker = segment["speaker"]
            transcript_with_speakers += f"\n[{current_speaker}]: "
        
        transcript_with_speakers += segment["text"] + " "
    
    return {
        "text": transcript_with_speakers.strip(),
        "segments": segments,
        "speaker_turns": speaker_turns
    }

def save_diarized_transcription(result, output_file):
    """Save transcription with speaker labels."""
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(result["text"])
    
    # Also save a detailed JSON version with all segment info
    import json
    json_output = output_file.replace(".txt", "_detailed.json")
    with open(json_output, 'w', encoding='utf-8') as f:
        json.dump({
            "segments": result["segments"],
            "speaker_turns": result["speaker_turns"]
        }, f, indent=2)
    
    print(f"Saved diarized transcription to {output_file}")
    print(f"Saved detailed segment data to {json_output}")

