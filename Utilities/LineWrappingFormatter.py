import logging
import textwrap

class LineWrappingFormatter(logging.Formatter):
    def __init__(self, fmt=None, datefmt=None, style='%', width=80):
        super().__init__(fmt, datefmt, style)
        self.width = width

    def format(self, record):
        # Generate the initial single-line formatted log
        original_msg = super().format(record)

        # Split the text by existing newlines first, then wrap each chunk
        wrapped_lines = [
            textwrap.fill(line, width=self.width)
            for line in original_msg.splitlines()
        ]

        return "\n".join(wrapped_lines)