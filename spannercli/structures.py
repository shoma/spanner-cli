from typing import List


class ResultContainer(object):
    def __init__(self, data: List, header, **kwargs):
        self.data = data
        self.header = header
        self.meta = kwargs

    def print_message(self):
        message = self.meta.get('message', None)
        if message is not None:
            print("\n", message, "\n", sep="")

    def format(self):
        return self.meta.get('format', None)

    def __len__(self):
        return len(self.data)
