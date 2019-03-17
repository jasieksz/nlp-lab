import re

def register():
    base = r'W ustawie z dnia \d{1,2} \w* \d{4} r\.'
    title = r'((\w| )*)'
    ref = r'([\s\S]*?)(?=\))'
    return base + title + ref

def section():
    return r'\bArt. \d*.\n'