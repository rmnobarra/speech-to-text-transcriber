import os
import time
import concurrent.futures
from typing import List, Dict, Any
import whisper

def process_file(input_file: str, output_dir: str, model_size: str, model, language=None, with_timestamps=False) -> Dict[str, Any]:
    """Process a single file and return results."""
    try:
        # Create output filename
        base_name = os.path.basename(input_file)
        name_without_ext = os.path.splitext(base_name)[0]
        output_file = os.path.join(output_dir, f"{name_without_ext}.txt")
        
        print(f"Processing: {base_name}")
        
        # Prepare transcription options
        transcribe_options = {
            "word_timestamps": with_timestamps
        }
        
        # Add language if specified
        if language and language != "auto":
            transcribe_options["language"] = language
            print(f"Transcribing in specified language: {language}")
        elif language == "auto":
            print("Performing automatic language detection...")
        
        # Transcribe audio
        start_time = time.time()
        result = model.transcribe(input_file, **transcribe_options)
        elapsed_time = time.time() - start_time
        
        # Save transcription
        with open(output_file, 'w', encoding='utf-8') as f:
            if with_timestamps and "segments" in result:
                # Write with timestamps
                for segment in result["segments"]:
                    start_time = format_time(segment["start"])
                    end_time = format_time(segment["end"])
                    f.write(f"[{start_time} --> {end_time}] {segment['text']}\n")
            else:
                # Write plain text
                f.write(result["text"])
        
        # Print detected language if auto-detection was used
        if language == "auto" and "language" in result:
            print(f"Detected language: {result['language']}")
        
        return {
            "file": input_file,
            "output": output_file,
            "success": True,
            "time": elapsed_time,
            "error": None,
            "language": result.get("language", None)
        }
        
    except Exception as e:
        print(f"Error processing {input_file}: {e}")
        return {
            "file": input_file,
            "output": None,
            "success": False,
            "time": 0,
            "error": str(e),
            "language": None
        }

def format_time(seconds):
    """Format seconds as HH:MM:SS."""
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{int(hours):02d}:{int(minutes):02d}:{seconds:05.2f}"

def parallel_batch_process(
    input_files: List[str], 
    output_dir: str, 
    model_size: str, 
    max_workers: int = None,
    language: str = None,
    with_timestamps: bool = False
) -> Dict[str, List]:
    """Process a batch of audio files in parallel."""
    if max_workers is None:
        # Default to number of CPU cores or 4, whichever is smaller
        import multiprocessing
        max_workers = min(4, multiprocessing.cpu_count())
    
    results = {"success": [], "failed": []}
    
    # Load the model once (shared between workers)
    print(f"Loading Whisper {model_size} model...")
    model = whisper.load_model(model_size)
    
    # Process files in parallel
    print(f"\nProcessing {len(input_files)} audio files with {max_workers} workers...")
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all tasks
        future_to_file = {
            executor.submit(
                process_file, 
                file, 
                output_dir, 
                model_size, 
                model,
                language,
                with_timestamps
            ): file 
            for file in input_files
        }
        
        # Process results as they complete
        for future in concurrent.futures.as_completed(future_to_file):
            file = future_to_file[future]
            try:
                result = future.result()
                if result["success"]:
                    results["success"].append(result)
                    lang_info = f" ({result['language']})" if result['language'] else ""
                    print(f"✅ Completed: {os.path.basename(file)}{lang_info} in {result['time']:.2f}s")
                else:
                    results["failed"].append(result)
                    print(f"❌ Failed: {os.path.basename(file)} - {result['error']}")
            except Exception as e:
                results["failed"].append({
                    "file": file,
                    "output": None,
                    "success": False,
                    "time": 0,
                    "error": str(e),
                    "language": None
                })
                print(f"❌ Error: {os.path.basename(file)} - {e}")
    
    return results

