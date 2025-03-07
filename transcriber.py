import argparse
import os
import sys
import time
from typing import List, Dict, Optional, Tuple
from pathlib import Path

import torch
import whisper
from pydub import AudioSegment
from tqdm import tqdm

# Import language utilities
from language_utils import print_supported_languages, is_language_supported, get_language_name

def get_audio_duration(file_path: str) -> float:
    """Get the duration of an audio file in seconds."""
    audio = AudioSegment.from_file(file_path)
    return len(audio) / 1000  # Convert milliseconds to seconds

def convert_to_wav(input_file: str) -> str:
    """Convert audio file to WAV format if needed."""
    file_ext = os.path.splitext(input_file)[1].lower()
    
    if file_ext == '.wav':
        return input_file
    
    # Create a temporary WAV file
    temp_wav = os.path.splitext(input_file)[0] + "_temp.wav"
    
    # Load audio file using pydub
    if file_ext == '.mp3':
        print(f"Converting MP3 to WAV format...")
        audio = AudioSegment.from_mp3(input_file)
    elif file_ext == '.ogg':
        print(f"Converting OGG to WAV format...")
        audio = AudioSegment.from_ogg(input_file)
    else:
        raise ValueError(f"Unsupported file format: {file_ext}")
    
    # Get audio duration in seconds
    duration_seconds = len(audio) / 1000
    chunks = 100
    chunk_duration = duration_seconds / chunks
    
    # Create a progress bar for conversion
    with tqdm(total=chunks, desc="Converting", unit="%") as pbar:
        # Start export
        audio.export(temp_wav, format="wav")
        
        # Simulate progress updates
        for _ in range(chunks):
            time.sleep(chunk_duration / 10)  # Speed up simulation for better UX
            pbar.update(1)
    
    print(f"Conversion complete: {temp_wav}")
    return temp_wav

def transcribe_audio(input_file: str, model_size: str = "base", model=None, language: str = None) -> dict:
    """Transcribe audio file to text using Whisper model."""
    # Check if file exists
    if not os.path.exists(input_file):
        raise FileNotFoundError(f"Audio file not found: {input_file}")
    
    # Check file extension
    file_ext = os.path.splitext(input_file)[1].lower()
    if file_ext not in ['.mp3', '.wav', '.ogg']:
        raise ValueError(f"Unsupported file format: {file_ext}")
    
    # Convert to WAV if needed
    wav_file = convert_to_wav(input_file)
    
    # Load the Whisper model if not provided
    if model is None:
        print(f"Loading Whisper {model_size} model...")
        with tqdm(total=100, desc="Loading model", unit="%") as pbar:
            # Model loading doesn't provide progress updates, so we simulate it
            for i in range(90):
                time.sleep(0.01)  # Simulate loading time
                pbar.update(1)
                
            model = whisper.load_model(model_size)
            
            # Complete the progress bar
            pbar.update(10)
    
    # Get audio duration for estimating transcription time
    duration = get_audio_duration(wav_file)
    chunks = 100
    # Rough estimate: transcription takes ~30% of audio duration or at least 5 seconds
    chunk_duration = max(duration * 0.3 / chunks, 5 / chunks)  
    
    # Prepare transcription options
    transcribe_options = {}
    
    # Handle language option
    if language and language != "auto":
        transcribe_options["language"] = language
        print(f"Transcribing in {get_language_name(language)} ({language})...")
    elif language == "auto":
        print("Performing automatic language detection...")
    else:
        print("Transcribing with default language settings...")
    
    # Transcribe the audio with progress bar
    print(f"Transcribing {os.path.basename(input_file)}...")
    with tqdm(total=chunks, desc="Transcribing", unit="%") as pbar:
        # Start transcription
        transcription_start = time.time()
        
        # Run transcription
        result = model.transcribe(wav_file, **transcribe_options)
        
        # Update progress bar based on chunks
        elapsed = time.time() - transcription_start
        # If transcription was faster than expected, update all at once
        if elapsed < chunk_duration * chunks:
            pbar.update(chunks)
        else:
            # Otherwise simulate remaining progress
            current_progress = pbar.n
            for _ in range(current_progress, chunks):
                time.sleep(0.01)
                pbar.update(1)
    
    # Clean up temporary file if created
    if wav_file != input_file:
        os.remove(wav_file)
    
    # Print detected language if auto-detection was used
    if language == "auto" and "language" in result:
        detected_code = result["language"]
        detected_name = get_language_name(detected_code)
        print(f"Detected language: {detected_name} ({detected_code})")
        
    return result

def save_transcription(result, output_file: str) -> None:
    """Save transcribed text to output file."""
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(os.path.abspath(output_file)), exist_ok=True)
    
    # Extract text from result (which could be a string or a dict)
    text = result["text"] if isinstance(result, dict) else result
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(text)
    print(f"Transcription saved to {output_file}")

def get_audio_files_from_directory(directory: str) -> List[str]:
    """Get all audio files from a directory."""
    audio_extensions = ['.mp3', '.wav', '.ogg']
    audio_files = []
    
    for root, _, files in os.walk(directory):
        for file in files:
            if any(file.lower().endswith(ext) for ext in audio_extensions):
                audio_files.append(os.path.join(root, file))
    
    return audio_files

def process_batch(input_files: List[str], output_dir: str, model_size: str, language: str = None) -> Dict[str, str]:
    """Process a batch of audio files."""
    results = {"success": [], "failed": []}
    
    # Load the model once for all files
    print(f"Loading Whisper {model_size} model for batch processing...")
    with tqdm(total=100, desc="Loading model", unit="%") as pbar:
        for i in range(90):
            time.sleep(0.01)
            pbar.update(1)
            
        model = whisper.load_model(model_size)
        pbar.update(10)
    
    # Process each file
    print(f"\nProcessing {len(input_files)} audio files...")
    
    for i, input_file in enumerate(input_files):
        try:
            # Create output filename
            base_name = os.path.basename(input_file)
            name_without_ext = os.path.splitext(base_name)[0]
            output_file = os.path.join(output_dir, f"{name_without_ext}.txt")
            
            print(f"\n[{i+1}/{len(input_files)}] Processing: {base_name}")
            
            # Transcribe audio
            result = transcribe_audio(input_file, model_size, model, language=language)
            
            # Save transcription
            save_transcription(result, output_file)
            
            # Add language info to success message if available
            lang_info = ""
            if language == "auto" and isinstance(result, dict) and "language" in result:
                detected_code = result["language"]
                detected_name = get_language_name(detected_code)
                lang_info = f" (Detected: {detected_name})"
            
            results["success"].append((input_file, output_file, lang_info))
            
        except Exception as e:
            print(f"❌ Error processing {input_file}: {e}")
            results["failed"].append((input_file, str(e)))
    
    return results

def main():
    parser = argparse.ArgumentParser(description="Transcribe audio files to text using Whisper")
    
    # Input options group
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument("-f", "--file", help="Path to a single audio file")
    input_group.add_argument("-d", "--directory", help="Path to a directory containing audio files")
    input_group.add_argument("-b", "--batch", nargs='+', help="List of audio files to process")
    
    # Output options
    parser.add_argument("-o", "--output", required=True, 
                        help="Output file (for single file) or directory (for batch processing)")
    
    # Model options
    parser.add_argument("-m", "--model", choices=["tiny", "base", "small", "medium", "large"], 
                        default="base", help="Whisper model size to use (default: base)")
    
    # Language options
    parser.add_argument("--language", 
                        help="Specify language code for transcription (use 'auto' for auto-detection)")
    parser.add_argument("--list-languages", action="store_true",
                        help="List all supported languages and their codes")
    
    args = parser.parse_args()
    
    # Show language list if requested
    if args.list_languages:
        print_supported_languages()
        sys.exit(0)
    
    # Validate language code if provided
    if args.language and not is_language_supported(args.language):
        print(f"Error: Unsupported language code '{args.language}'")
        print("Use --list-languages to see all supported language codes")
        sys.exit(1)
    
    try:
        # Determine if we're doing batch processing
        is_batch = args.directory is not None or args.batch is not None
        
        if is_batch:
            # Get list of files to process
            if args.directory:
                input_files = get_audio_files_from_directory(args.directory)
                if not input_files:
                    print(f"No audio files found in directory: {args.directory}")
                    sys.exit(1)
            else:  # args.batch
                input_files = args.batch
            
            # Create output directory if it doesn't exist
            os.makedirs(args.output, exist_ok=True)
            
            # Process batch
            start_time = time.time()
            results = process_batch(input_files, args.output, args.model, language=args.language)
            elapsed_time = time.time() - start_time
            
            # Print summary
            print("\n" + "="*50)
            print(f"Batch Processing Summary:")
            print(f"Total files: {len(input_files)}")
            print(f"Successfully processed: {len(results['success'])}")
            print(f"Failed: {len(results['failed'])}")
            print(f"Total time: {elapsed_time:.2f} seconds")
            print("="*50)
            
            if results["failed"]:
                print("\nFailed files:")
                for file, error in results["failed"]:
                    print(f"- {os.path.basename(file)}: {error}")
            
            # Print successful files with language info if available
            if results["success"]:
                print("\nSuccessful transcriptions:")
                for file, output, lang_info in results["success"]:
                    print(f"- {os.path.basename(file)}{lang_info} -> {output}")
            
        else:  # Single file processing
            # Process single file
            print(f"Processing single file: {args.file}")
            result = transcribe_audio(args.file, args.model, language=args.language)
            save_transcription(result, args.output)
            
            # Print language info if auto-detection was used
            if args.language == "auto" and isinstance(result, dict) and "language" in result:
                detected_code = result["language"]
                detected_name = get_language_name(detected_code)
                print(f"Detected language: {detected_name} ({detected_code})")
                
            print("✅ Transcription completed successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()

