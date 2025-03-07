# Whisper Speech-to-Text Transcriber

A powerful, user-friendly application for transcribing audio recordings to text, powered by OpenAI's Whisper model. This project provides both a command-line interface and a web application for speech-to-text transcription with support for 90+ languages.

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Command-Line Usage](#command-line-usage)
- [Web Interface](#web-interface)
- [Advanced Features](#advanced-features)
- [Technical Details](#technical-details)
- [Troubleshooting](#troubleshooting)
- [Future Enhancements](#future-enhancements)
- [Contributing](#contributing)
- [License](#license)

## Features

### Core Features

- **High-Accuracy Transcription**: Powered by OpenAI's state-of-the-art Whisper model
- **Multi-Format Support**: Process MP3, WAV, and OGG audio files
- **Multiple Model Sizes**: Choose from tiny, base, small, medium, or large models based on your needs
- **Multilingual Support**: Transcribe audio in 90+ languages with excellent recognition
- **Automatic Language Detection**: Let the model identify the spoken language
- **Real-Time Progress Tracking**: Detailed progress bars and status updates
- **Batch Processing**: Efficiently process multiple files or entire directories
- **Format Conversion**: Automatic conversion of various audio formats to the required format

### Command-Line Interface

- **Intuitive Arguments**: Easy-to-use command-line options
- **Flexible Input Options**: Process single files, directories, or specific file lists
- **Detailed Progress Bars**: Visual feedback during processing
- **Comprehensive Error Handling**: Clear error messages and recovery options
- **Language Listing**: View all supported languages and their codes
- **Batch Summary Reports**: Get detailed success/failure reports for batch jobs

### Web Interface

- **User-Friendly Upload**: Drag-and-drop file uploading
- **Visual Progress Tracking**: Real-time progress indicators for all stages
- **Language Detection Display**: See which language was detected in your audio
- **Job History**: Track and access recent transcription jobs
- **One-Click Downloads**: Easily download completed transcriptions
- **Responsive Design**: Works on desktop and mobile devices
- **Intuitive Settings**: Simple controls for model size and language selection

## Installation

### Prerequisites

- Python 3.8 or higher
- FFmpeg (required for audio processing)
- 2GB+ RAM (more for larger models)
- CUDA-compatible GPU (optional, for faster processing)

### Installing FFmpeg

#### Ubuntu/Debian
```bash
sudo apt update
sudo apt install ffmpeg
```

#### macOS

```shellscript
brew install ffmpeg
```

#### Windows

Download from [https://ffmpeg.org/download.html](https://ffmpeg.org/download.html) or install with Chocolatey:

```shellscript
choco install ffmpeg
```

### Setting Up the Project

1. Clone the repository (or download and extract the ZIP):


```shellscript
git clone https://github.com/rmnobarra/whisper-transcriber.git
cd whisper-transcriber
```

2. Create a virtual environment:


```shellscript
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:


```shellscript
pip install --upgrade pip
pip install -r requirements.txt
```

This will install all required packages including:

- torch
- openai-whisper
- pydub
- ffmpeg-python
- tqdm
- flask (for web interface)


### GPU Acceleration (Optional)

For faster transcription, install PyTorch with CUDA support:

```shellscript
# For CUDA 11.8 (adjust version as needed)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

## Command-Line Usage

### Basic Usage

Transcribe a single audio file:

```shellscript
python transcriber.py -f path/to/audiofile.mp3 -o output.txt
```

### Command-Line Arguments

```plaintext
usage: transcriber.py [-h] (-f FILE | -d DIRECTORY | -b BATCH [BATCH ...]) -o OUTPUT [-m {tiny,base,small,medium,large}] [--language LANGUAGE] [--list-languages]

Transcribe audio files to text using Whisper

options:
  -h, --help            show this help message and exit
  -f FILE, --file FILE  Path to a single audio file
  -d DIRECTORY, --directory DIRECTORY
                        Path to a directory containing audio files
  -b BATCH [BATCH ...], --batch BATCH [BATCH ...]
                        List of audio files to process
  -o OUTPUT, --output OUTPUT
                        Output file (for single file) or directory (for batch processing)
  -m {tiny,base,small,medium,large}, --model {tiny,base,small,medium,large}
                        Whisper model size to use (default: base)
  --language LANGUAGE   Specify language code for transcription (use 'auto' for auto-detection)
  --list-languages      List all supported languages and their codes
```

### Examples

**Transcribe a single file with auto language detection:**

```shellscript
python transcriber.py -f recording.mp3 -o transcript.txt --language auto
```

**Process all audio files in a directory:**

```shellscript
python transcriber.py -d ./audio_files -o ./transcripts --model medium
```

**Process specific files with a specific language:**

```shellscript
python transcriber.py -b file1.mp3 file2.wav -o ./transcripts --language en
```

**List all supported languages:**

```shellscript
python transcriber.py --list-languages
```

**Transcribe a file in a specific language:**

```shellscript
python transcriber.py -f interview.mp3 -o interview_transcript.txt --language fr
```

## Web Interface

### Starting the Web Server

Run the Flask application:

```shellscript
python app.py
```

Then open your web browser and navigate to:

```plaintext
http://127.0.0.1:5000
```

For production deployment, consider using Gunicorn or uWSGI with Nginx.

### Using the Web Interface

1. **Upload an Audio File**:

1. Click on the upload area or drag and drop an audio file
2. Supported formats: MP3, WAV, OGG (max 100MB)



2. **Configure Transcription Settings**:

1. Select a model size (tiny, base, small, medium, large)
2. Choose a language or select "Auto-detect language"



3. **Start Transcription**:

1. Click the "Transcribe Audio" button
2. Monitor progress in real-time



4. **View and Download Results**:

1. Results will appear once transcription is complete
2. Click the "Download" button to save the transcription
3. View detected language (if auto-detection was used)



5. **Access Previous Jobs**:

1. Recent transcription jobs are listed in the sidebar
2. Click on completed jobs to view their results





### Web Interface Screenshots




*File upload and configuration screen*




*Real-time transcription progress tracking*




*Completed transcription with download option*

## Advanced Features

### Model Selection

The application supports multiple Whisper model sizes:

| Model | Parameters | Relative Speed | Memory Required | Accuracy | Use Case
|-----|-----|-----|-----|-----|-----
| tiny | 39M | Fastest (1x) | ~1GB | Basic | Quick transcriptions, clear audio
| base | 74M | Fast (1.5x) | ~1GB | Good | General purpose, good balance
| small | 244M | Medium (2x) | ~2GB | Better | Higher accuracy needs
| medium | 769M | Slow (5x) | ~5GB | High | Professional transcription
| large | 1550M | Slowest (10x) | ~10GB | Highest | Research, critical accuracy


Choose the appropriate model based on your hardware capabilities and accuracy requirements.

### Language Support

The transcriber supports 90+ languages with excellent recognition capabilities. Use `--language` with the appropriate language code, or `--list-languages` to see all supported languages.

Key supported languages include:

- English (en)
- Spanish (es)
- French (fr)
- German (de)
- Chinese (zh)
- Japanese (ja)
- Russian (ru)
- Arabic (ar)
- Hindi (hi)
- Portuguese (pt)
- Italian (it)
- Dutch (nl)
- Turkish (tr)
- Polish (pl)
- And many more...


### Batch Processing

Process multiple files efficiently:

```shellscript
# Process all audio files in a directory
python transcriber.py -d ./podcast_episodes -o ./transcripts

# Process specific files
python transcriber.py -b interview1.mp3 interview2.mp3 lecture.wav -o ./transcripts
```

The batch processor:

- Loads the model only once for all files
- Provides detailed progress tracking for each file
- Generates a summary report of successful and failed transcriptions
- Handles errors gracefully, continuing with remaining files


### Audio Format Handling

The application automatically handles various audio formats:

- Direct support for WAV files
- Automatic conversion of MP3 to WAV
- Automatic conversion of OGG to WAV
- Progress tracking during conversion


## Technical Details

### Project Structure

```plaintext
whisper-transcriber/
├── transcriber.py       # Command-line transcription tool
├── language_utils.py    # Language support utilities
├── app.py               # Flask web application
├── templates/           # Web templates
│   └── index.html       # Main web interface
├── uploads/             # Temporary storage for uploaded files
├── results/             # Storage for transcription results
├── .venv/               # Virtual environment (created during setup)
└── requirements.txt     # Project dependencies
```

### How It Works

1. **Audio Processing**:

1. Audio files are converted to WAV format if needed
2. FFmpeg handles audio conversion via pydub
3. Audio duration is calculated for progress estimation



2. **Transcription**:

1. OpenAI's Whisper model processes the audio
2. Progress is tracked and displayed in real-time
3. Language detection is performed if requested
4. Results are formatted and saved to the specified location



3. **Web Interface**:

1. Flask serves the web application
2. Background threads handle transcription tasks
3. AJAX requests update progress information
4. Results are stored for later retrieval
5. Job history is maintained for the session





### Performance Considerations

- **GPU vs CPU**: GPU acceleration can be 5-10x faster than CPU processing
- **Model Size Impact**: Larger models are more accurate but significantly slower
- **Memory Usage**: Larger models require more RAM/VRAM
- **Batch Efficiency**: Processing multiple files in batch is more efficient than individually
- **Web Server Load**: The web server can handle multiple concurrent users, but transcription is resource-intensive


### Security Considerations

- **File Validation**: The application validates file types and sizes
- **Secure Filenames**: Uploaded filenames are sanitized to prevent path traversal
- **Temporary Files**: Uploaded files are stored with unique IDs to prevent conflicts
- **Automatic Cleanup**: Old files and job data are periodically removed


## Troubleshooting

### Common Issues

**"FFmpeg not found" error:**

- Ensure FFmpeg is installed and available in your PATH
- On Windows, you might need to restart your terminal after installing FFmpeg
- Try running `ffmpeg -version` to verify the installation


**"CUDA not available" warning:**

- This means the application is running on CPU instead of GPU
- Ensure you have a compatible NVIDIA GPU and proper CUDA installation
- Install the appropriate PyTorch version for your CUDA setup
- Run `python -c "import torch; print(torch.cuda.is_available())"` to verify CUDA


**Slow transcription:**

- Try a smaller model (tiny or base)
- Ensure you're using GPU acceleration if available
- Split very long audio files into smaller segments
- Close other resource-intensive applications


**Language detection issues:**

- If auto-detection fails, try specifying the language explicitly
- Some dialects or accents may need manual language selection
- Ensure the audio quality is good enough for language detection


**Web server issues:**

- Check that port 5000 is not in use by another application
- Ensure you have sufficient permissions to write to the uploads and results directories
- Try running with `python app.py` to see any error messages


**"externally-managed-environment" error:**

- Create a proper virtual environment as described in the installation section
- Ensure you're activating the virtual environment before installing packages
- On Debian-based systems, make sure you have python3-venv installed


### Memory Requirements

| Model | CPU RAM | GPU VRAM
|-----|-----|-----|-----|-----|-----
| tiny | 1GB+ | 1GB+
| base | 1GB+ | 1GB+
| small | 2GB+ | 2GB+
| medium | 5GB+ | 4GB+
| large | 10GB+ | 8GB+


### Getting Help

If you encounter issues not covered here, please:

1. Check the GitHub issues page for similar problems
2. Create a new issue with detailed information about your setup and the problem
3. Include error messages and steps to reproduce the issue
4. Specify your operating system, Python version, and hardware details


## Future Enhancements

Planned features for future releases:

- Basic transcription functionality
- Multiple language support
- Batch processing
- Web interface
- Speaker diarization (identifying different speakers)
- Subtitle file generation (SRT, VTT formats)
- API endpoint for integration with other applications
- User accounts and job persistence
- Advanced audio pre-processing options
- Docker containerization
- Parallel processing for faster batch operations
- Timestamp generation for long-form content
- Text summarization of transcriptions
- Integration with cloud storage services
- Command-line completion and shell integration


## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request


### Development Setup

For development, you may want to install additional packages:

```shellscript
pip install -r requirements-dev.txt  # If provided
```

### Coding Standards

- Follow PEP 8 style guidelines
- Add docstrings to functions and classes
- Write unit tests for new features
- Update documentation when changing functionality


## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

- [OpenAI Whisper](https://github.com/openai/whisper) for the incredible speech recognition model
- [Flask](https://flask.palletsprojects.com/) for the web framework
- [PyDub](https://github.com/jiaaro/pydub) for audio processing
- [tqdm](https://github.com/tqdm/tqdm) for progress bar functionality


---

Built with ❤️ using [OpenAI Whisper](https://github.com/openai/whisper)