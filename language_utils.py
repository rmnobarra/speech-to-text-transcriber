"""Utility functions for language support in the transcriber."""

# List of languages supported by Whisper
# This is a comprehensive list of language codes and their full names
SUPPORTED_LANGUAGES = {
    "en": "English",
    "zh": "Chinese",
    "de": "German",
    "es": "Spanish",
    "ru": "Russian",
    "ko": "Korean",
    "fr": "French",
    "ja": "Japanese",
    "pt": "Portuguese",
    "tr": "Turkish",
    "pl": "Polish",
    "ca": "Catalan",
    "nl": "Dutch",
    "ar": "Arabic",
    "sv": "Swedish",
    "it": "Italian",
    "id": "Indonesian",
    "hi": "Hindi",
    "fi": "Finnish",
    "vi": "Vietnamese",
    "he": "Hebrew",
    "uk": "Ukrainian",
    "el": "Greek",
    "ms": "Malay",
    "cs": "Czech",
    "ro": "Romanian",
    "da": "Danish",
    "hu": "Hungarian",
    "ta": "Tamil",
    "no": "Norwegian",
    "th": "Thai",
    "ur": "Urdu",
    "hr": "Croatian",
    "bg": "Bulgarian",
    "lt": "Lithuanian",
    "la": "Latin",
    "mi": "Maori",
    "ml": "Malayalam",
    "cy": "Welsh",
    "sk": "Slovak",
    "te": "Telugu",
    "fa": "Persian",
    "lv": "Latvian",
    "bn": "Bengali",
    "sr": "Serbian",
    "az": "Azerbaijani",
    "sl": "Slovenian",
    "kn": "Kannada",
    "et": "Estonian",
    "mk": "Macedonian",
    "br": "Breton",
    "eu": "Basque",
    "is": "Icelandic",
    "hy": "Armenian",
    "ne": "Nepali",
    "mn": "Mongolian",
    "bs": "Bosnian",
    "kk": "Kazakh",
    "sq": "Albanian",
    "sw": "Swahili",
    "gl": "Galician",
    "mr": "Marathi",
    "pa": "Punjabi",
    "si": "Sinhala",
    "km": "Khmer",
    "sn": "Shona",
    "yo": "Yoruba",
    "so": "Somali",
    "af": "Afrikaans",
    "oc": "Occitan",
    "ka": "Georgian",
    "be": "Belarusian",
    "tg": "Tajik",
    "sd": "Sindhi",
    "gu": "Gujarati",
    "am": "Amharic",
    "yi": "Yiddish",
    "lo": "Lao",
    "uz": "Uzbek",
    "fo": "Faroese",
    "ht": "Haitian Creole",
    "ps": "Pashto",
    "tk": "Turkmen",
    "nn": "Nynorsk",
    "mt": "Maltese",
    "sa": "Sanskrit",
    "lb": "Luxembourgish",
    "my": "Myanmar",
    "bo": "Tibetan",
    "tl": "Tagalog",
    "mg": "Malagasy",
    "as": "Assamese",
    "tt": "Tatar",
    "haw": "Hawaiian",
    "ln": "Lingala",
    "ha": "Hausa",
    "ba": "Bashkir",
    "jw": "Javanese",
    "su": "Sundanese",
}

def print_supported_languages():
    """Print a formatted list of supported languages."""
    print("\nSupported Languages:")
    print("=" * 50)
    print(f"{'Code':<6} {'Language':<20}")
    print("-" * 50)
    
    # Sort languages by name for better readability
    sorted_languages = sorted(SUPPORTED_LANGUAGES.items(), key=lambda x: x[1])
    
    # Print in columns
    for i, (code, name) in enumerate(sorted_languages):
        print(f"{code:<6} {name:<20}", end="")
        
        # Print 3 languages per line
        if (i + 1) % 3 == 0:
            print()
    
    # Add a final newline if needed
    if len(sorted_languages) % 3 != 0:
        print()
    
    print("=" * 50)
    print("Use the language code with the --language option.")
    print("Example: --language fr (for French)")
    print("Use --language auto for automatic language detection.")

def is_language_supported(language_code):
    """Check if a language code is supported."""
    return language_code in SUPPORTED_LANGUAGES or language_code == "auto"

def get_language_name(language_code):
    """Get the full name of a language from its code."""
    if language_code == "auto":
        return "Auto-detected"
    return SUPPORTED_LANGUAGES.get(language_code, "Unknown")

