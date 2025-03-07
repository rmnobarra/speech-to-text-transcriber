import os
from datetime import timedelta

def format_timestamp(seconds, format_type="srt"):
    """Convert seconds to SRT or VTT timestamp format."""
    td = timedelta(seconds=seconds)
    hours, remainder = divmod(td.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    milliseconds = td.microseconds // 1000
    
    if format_type == "srt":
        return f"{hours:02d}:{minutes:02d}:{seconds:02d},{milliseconds:03d}"
    else:  # vtt
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}.{milliseconds:03d}"

def generate_subtitles(segments, output_file, format_type="srt"):
    """Generate subtitle file from segments."""
    if format_type not in ["srt", "vtt"]:
        raise ValueError("Format type must be 'srt' or 'vtt'")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        # Write header for VTT
        if format_type == "vtt":
            f.write("WEBVTT\n\n")
        
        for i, segment in enumerate(segments):
            # Index (only for SRT)
            if format_type == "srt":
                f.write(f"{i+1}\n")
            
            # Timestamps
            start = format_timestamp(segment['start'], format_type)
            end = format_timestamp(segment['end'], format_type)
            
            if format_type == "srt":
                f.write(f"{start} --> {end}\n")
            else:  # vtt
                f.write(f"{start} --> {end}\n")
            
            # Text
            f.write(f"{segment['text'].strip()}\n\n")

def transcribe_with_timestamps(input_file, model_size="base", model=None, language=None):
    """Transcribe audio with timestamps for each segment."""
    import whisper
    
    # Load model if not provided
    if model is None:
        model = whisper.load_model(model_size)
    
    # Prepare transcription options
    transcribe_options = {
        "word_timestamps": True
    }
    
    # Add language if specified
    if language and language != "auto":
        transcribe_options["language"] = language
    
    # Transcribe with word-level timestamps
    result = model.transcribe(input_file, **transcribe_options)
    
    return result

def save_subtitles(result, output_base, formats=["srt", "vtt"]):
    """Save transcription as subtitle files."""
    for format_type in formats:
        output_file = f"{output_base}.{format_type}"
        generate_subtitles(result["segments"], output_file, format_type)
        print(f"Saved {format_type.upper()} subtitles to {output_file}")

