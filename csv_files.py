import csv
import re


class CSVRead:
    def __init__(self, **kwargs):
        self.file = kwargs.get("file", "")
        self.regex = kwargs.get("regex", "")
        self.url = []

    def main(self):
        self.csv_read()
        return self.url

    def csv_read(self):  # find urls in plain text. csv does not support hyperlinks
        with open(self.file, mode="r", newline="", encoding="utf-8") as file:
            reader = csv.reader(file)
            for row in reader:
                for cell in row:
                    words = cell.split()
                    if len(words) > 1:
                        for word in words:
                            url = re.findall(self.regex, word)
                            if url:
                                self.url.append(word)
                    else:
                        url = re.findall(self.regex, cell)
                        if url:
                            self.url.append(cell)
