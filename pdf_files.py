import io
import re

import fitz #pymupdf
import PyPDF2
from PIL import Image
from pyzbar.pyzbar import decode


class PDFRead:
    def __init__(self, **kwargs):
        self.file = kwargs.get("file", "")
        self.regex = kwargs.get("regex", "")
        self.url = []

    def main(self):
        self.plain_text()
        self.hyperlinks()
        self.qr_codes()
        return self.url

    def plain_text(self):
        text = ""
        with open(self.file, "rb") as file:  # find plain text urls
            reader = PyPDF2.PdfReader(file)
            for page_num in range(len(reader.pages)):
                page = reader.pages[page_num]
                text += page.extract_text()
                text_list = text.split()
                for word in text_list:
                    url = re.findall(self.regex, word)
                    if url:
                        self.url.append(word)

    def hyperlinks(self):
        reader = PyPDF2.PdfReader(self.file)  # find  embedded hyperlinks
        for page in reader.pages:
            if "/Annots" in page:
                for annot in page["/Annots"]:
                    annot_obj = annot.get_object()
                    if "/A" in annot_obj and "/URI" in annot_obj["/A"]:
                        self.url.append(annot_obj["/A"]["/URI"])

    def qr_codes(self):
        doc = fitz.open(self.file)
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            pix = page.get_pixmap(dpi=300)
            img = Image.open(io.BytesIO(pix.tobytes("png")))
            decoded_objects = decode(img)
            for obj in decoded_objects:
                print(f"Page {page_num + 1}: {obj.data.decode('utf-8')}")
                self.url.append(obj.data.decode("utf-8"))
        doc.close()
