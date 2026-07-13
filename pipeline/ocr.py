"""OCR for scanned pages. Only called by extract.py when a page has no text layer."""

import cv2
import fitz
import numpy as np
import pytesseract

from . import config

if config.TESSERACT_CMD:
    pytesseract.pytesseract.tesseract_cmd = config.TESSERACT_CMD


def _deskew(gray):
    # find the angle of the text block and rotate to straighten it
    inverted = cv2.bitwise_not(gray)
    thresh = cv2.threshold(inverted, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
    coords = np.column_stack(np.where(thresh > 0))
    if len(coords) < 50:
        return gray  # not enough signal to estimate an angle, skip
    angle = cv2.minAreaRect(coords)[-1]
    angle = -(90 + angle) if angle < -45 else -angle
    if abs(angle) < 0.1:
        return gray
    h, w = gray.shape
    matrix = cv2.getRotationMatrix2D((w // 2, h // 2), angle, 1.0)
    return cv2.warpAffine(gray, matrix, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)


def preprocess_for_ocr(pix):
    gray = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width)
    gray = _deskew(gray)
    binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
    return binary


def ocr_page(page, lang=config.OCR_LANG, dpi=config.OCR_DPI):
    """Rasterize a fitz page and run tesseract on it. Returns plain text."""
    zoom = dpi / 72  # fitz default render is 72dpi, scale up for better accuracy
    pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom), colorspace=fitz.csGRAY)
    image = preprocess_for_ocr(pix)
    return pytesseract.image_to_string(image, lang=lang)