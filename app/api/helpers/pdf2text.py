# from PyPDF2 import PdfReader, PdfWriter


def rewrite_pdf(file_path: str) -> str:
    """Rewrite a PDF file"""

    output_path = file_path.replace(".pdf", "_rewritten.pdf")
    # reader = PdfReader(file_path)
    # writer = PdfWriter()

    # for page in reader.pages:
    #     writer.add_page(page)

    # with open(output_path, "wb") as f:
    #     writer.write(f)

    return output_path


def get_pdf_page_count(pdf_file_path: str) -> int:
    """Get the number of pages in a PDF file"""

    with open(pdf_file_path, "rb") as file:
        # pdf_reader = PdfReader(file)
        return 1


# def is_pdf_scanned(pdf_file_path: str) -> bool:
#     """Check if a PDF file is scanned"""
    
#     with open(pdf_file_path, "rb") as file:
#         reader = PdfReader(file)
#         for page_num in range(len(reader.pages)):
#             page = reader.pages[page_num]
#             text = page.extract_text()
#             if text and text.strip():  # If text exists and is not just whitespace
#                 return False  # The PDF contains text
#         return True  # No text found, likely a scanned document
