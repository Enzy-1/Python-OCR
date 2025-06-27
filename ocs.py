import os
import sys
import argparse

from pdf2image import convert_from_path
from PIL import Image
import easyocr


def extract_text_from_image(reader, image_path):
    # Load image and perform OCR
    image = Image.open(image_path)
    results = reader.readtext(np.array(image), detail=0)
    return "\n".join(results)


def extract_text_from_pdf(reader, pdf_path, dpi=300):
    # Convert PDF pages to images
    pages = convert_from_path(pdf_path, dpi=dpi)
    texts = []
    for i, page in enumerate(pages, start=1):
        print(f"Processing page {i}/{len(pages)}...")
        results = reader.readtext(np.array(page), detail=0)
        texts.append("\n".join(results))
    return "\n\n".join(texts)


def main():
    parser = argparse.ArgumentParser(
        description="Ocr extraction from images (png/jpg) and pdfs using EasyOCR"
    )
    parser.add_argument(
        "file",
        help="Path to the input file (PNG, JPG, or PDF)",
    )
    parser.add_argument(
        "--lang",
        nargs="+",
        default=["en"],
        help="Language(s) for OCR (e.g., en, es)",
    )
    parser.add_argument(
        "--output",
        help="Path to save extracted text. Defaults to stdout.",
        default=None,
    )

    args = parser.parse_args()
    file_path = args.file

    # Ensure file exists
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        sys.exit(1)

    # Initialize EasyOCR reader
    print(f"Loading EasyOCR Reader for languages: {args.lang}...")
    reader = easyocr.Reader(args.lang)

    # Determine file type and extract text
    ext = os.path.splitext(file_path)[1].lower()
    if ext in [".png", ".jpg", ".jpeg"]:
        text = extract_text_from_image(reader, file_path)
    elif ext == ".pdf":
        text = extract_text_from_pdf(reader, file_path)
    else:
        print("Unsupported file type. Please provide a PNG, JPG, or PDF.")
        sys.exit(1)

    # Output
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(text)
        print(f"Text extracted and saved to {args.output}")
    else:
        print("----- Extracted Text -----")
        print(text)


if __name__ == '__main__':
    import numpy as np

    main()
