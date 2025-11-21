import os
import time
import json
from unidecode import unidecode
import google.generativeai as genai
from pydantic import ValidationError

from app.api.helpers.check_language import check_language_is_en
from app.api.helpers.pdf2markdown import pdf_to_markdown
from app.api.helpers.pdf2text import rewrite_pdf, get_pdf_page_count
from app.core.prompts.v1.intern import jd as prompt_jd
from app.core.prompts.v1.intern import cv as prompt_cv
from app.core.prompts.v1.intern.schemas.jd import JDInformation
from app.core.prompts.v1.intern.schemas.cv import CVInformation, Certificates
from app.core.config import MODEL_NAME, OUTPUT_FOLDER
from app.logger.logger import custom_logger


class ExtractService:
    """Service class for extracting job description and CV information"""

    def __init__(self):
        self.folders = {
            "text_jd": os.path.join(OUTPUT_FOLDER, "text_jd"),
            "json_jd": os.path.join(OUTPUT_FOLDER, "json_jd"),
            "text_cv": os.path.join(OUTPUT_FOLDER, "text_cv"),
            "cleaned_text_cv": os.path.join(OUTPUT_FOLDER, "cleaned_text_cv"),
            "json_cv": os.path.join(OUTPUT_FOLDER, "json_cv"),
        }

        for folder in self.folders.values():
            os.makedirs(folder, exist_ok=True)

    @staticmethod
    def save_text(text: str, file_path: str):
        """Saves text to a file"""
        
        with open(file_path, "w") as f:
            f.write(text)

    @staticmethod
    def save_json(data: dict, file_path: str):
        """Saves JSON data to a file"""

        with open(file_path, "w") as f:
            f.write(json.dumps(data, indent=2))

    def parse_pdf(self, file_path: str) -> str:
        """Extracts text from a PDF file"""
        try:
            return pdf_to_markdown(file_path)

        except UnicodeDecodeError as e:
            custom_logger.error(f"UnicodeDecodeError: {e}, rewriting the PDF file")
            rewrite_file_path = rewrite_pdf(file_path)
            custom_logger.info(f"Rewritten PDF file: {rewrite_file_path}")
            return pdf_to_markdown(rewrite_file_path)

    @staticmethod
    def extract_jd(text: str):
        """Extracts job description information from a document"""

        model = genai.GenerativeModel(
            MODEL_NAME,
            system_instruction=prompt_jd.extract_prompt,
            generation_config={
                "response_mime_type": "application/json",
            },
        )
        response = model.generate_content(text)

        # Validate the data
        try:
            return JDInformation.model_validate_json(response.text)

        except ValidationError as e:
            custom_logger.error(f"Validation Error: {e.json(indent=2)}")

    def process_jd(self, file_path: str):
        """Processes job description information from a document"""

        name = os.path.splitext(os.path.basename(file_path))[0]
        file_path_json = os.path.join(self.folders["json_jd"], f"{name}_jd.json")

        if os.path.exists(file_path_json):
            custom_logger.info(f"File {file_path_json} already exists")
            with open(file_path_json, "r") as f:
                return JDInformation.model_validate(json.load(f))

        text = self.parse_pdf(file_path)
        self.save_text(text, os.path.join(self.folders["text_jd"], f"{name}_jd.txt"))

        jd_info = self.extract_jd(text)
        if jd_info:
            self.save_json(jd_info.model_dump(), file_path_json)

        return jd_info

    @staticmethod
    def extract_cv(text: str):
        """Extracts CV information from a document"""

        model = genai.GenerativeModel(
            MODEL_NAME,
            system_instruction=prompt_cv.extract_prompt,
            generation_config={
                "response_mime_type": "application/json",
            },
        )
        response = model.generate_content(text)

        # Validate the data
        try:
            return CVInformation.model_validate_json(response.text)

        except ValidationError as e:
            custom_logger.error(f"Validation Error: {e.json(indent=2)}")
            return CVInformation(certificates=Certificates())

    @staticmethod
    def reorganize_cv_text(text: str):
        """Reorganizes the text for better extraction"""

        model = genai.GenerativeModel(
            MODEL_NAME,
            system_instruction=prompt_cv.reorganize_prompt,
        )
        response = model.generate_content(text)

        return response.text

    def process_cv(self, file_path: str):
        """Processes CV information from a document"""

        # Reject CVs with more than 2 pages
        if get_pdf_page_count(file_path) > 10:
            return None

        name = os.path.splitext(os.path.basename(file_path))[0]
        file_path_txt = os.path.join(self.folders["text_cv"], f"{name}_cv.txt")
        file_path_cleaned = os.path.join(
            self.folders["cleaned_text_cv"], f"{name}_cv_clean.txt"
        )
        file_path_json = os.path.join(self.folders["json_cv"], f"{name}_cv.json")

        # Parse the PDF file
        text = self.parse_pdf(file_path)

        # Reject CVs that are not in English
        if not check_language_is_en(text):
            return None

        self.save_text(unidecode(text), file_path_txt)
        text_cleaned = self.reorganize_cv_text(unidecode(text))
        self.save_text(text_cleaned, file_path_cleaned)

        time.sleep(2)

        extracted_cv = self.extract_cv(text_cleaned)

        # Reject CVs that have "college" in the university name
        if extracted_cv and "college" not in extracted_cv.university.lower():
            self.save_json(extracted_cv.model_dump(), file_path_json)
            return extracted_cv

        return None
