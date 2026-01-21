import re

from striprtf.striprtf import rtf_to_text


class RTFRead:
    def __init__(self, **kwargs):
        self.file = kwargs.get("file", "")
        self.regex = kwargs.get("regex", "")
        self.url = []

    def main(self):
        self.rtf_read()
        return self.url

    def rtf_read(self):  # find urls in plain text and hyperlinks
        with open(self.file) as file:
            content = file.read()
            text_str = rtf_to_text(content)
        text_list = text_str.split()
        for text in text_list:
            url = re.findall(self.regex, text)
            if url:
                url_split = text.split('"')
                if len(url_split) > 1:
                    text = url_split[1]
                else:
                    text = url_split[0]
                self.url.append(text)
