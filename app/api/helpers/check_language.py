from langdetect import detect


def check_language_is_en(text: str) -> bool:
    """Check if the language of the text is English"""
    
    return detect(text) == "en"
