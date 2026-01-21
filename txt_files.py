import re


class TXTRead:
    def __init__(self, **kwargs):
        self.file = kwargs.get("file", "")
        self.regex = kwargs.get("regex", "")
        self.url = []

    def main(self):
        self.txt_read()
        return self.url

    def txt_read(self):  # finds urls in plain text txt files don't support hyperlinks
        with open(self.file, "r") as file:
            read_txt = file.read()
            text_list = read_txt.split()
            for text in text_list:
                url = re.findall(self.regex, read_txt)
                if url:
                    self.url.append(text)
