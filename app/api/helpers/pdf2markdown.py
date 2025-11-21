


# pipeline_options = PdfPipelineOptions()
# pipeline_options.do_ocr = False
# pipeline_options.do_table_structure = True

# doc_converter = (
#     DocumentConverter(  # all of the below is optional, has internal defaults.
#         allowed_formats=[
#             InputFormat.PDF,
#             InputFormat.DOCX,
#         ],  # whitelist formats, non-matching files are ignored.
#         format_options={
#             InputFormat.PDF: PdfFormatOption(
#                 pipeline_options=pipeline_options, # pipeline options go here.
#                 backend=PyPdfiumDocumentBackend # optional: pick an alternative backend
#             ),
#             InputFormat.DOCX: WordFormatOption(
#                 pipeline_cls=SimplePipeline # default for office formats and HTML
#             ),
#         },
#     )
# )

def pdf_to_markdown(file_path: str) -> str:
    """Converts a PDF document to markdown format"""

    return 1
