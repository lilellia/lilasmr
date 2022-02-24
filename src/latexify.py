import itertools
import logging
import pathlib
import re
import io
import sys

logging.basicConfig(level=logging.DEBUG)


class StringIO(io.StringIO):
    def writeline(self, text: str):
        self.write(f"{text}\n")

    @property
    def contents(self):
        # store current position
        pos = self.tell()

        # return to beginning and read
        self.seek(0)
        c = self.read()

        # restore old position
        self.seek(pos)

        return c


def latexcmd(cmd: str, *args: str) -> str:
    """Create a string representation of a LaTeX command.

    latexcmd(textit, abc)
        \textit{abc}

    latexcmd(custom, a, b, c)
        \custom{a}{b}{c}
    """
    return f"\\{cmd}" + "".join("{" + str(a) + "}" for a in args)


def split_file(asmr: pathlib.Path):
    header, body = [], []
    ptr = header
    for line in asmr.read_text().splitlines():
        if not line.strip():
            # ignore blank lines
            continue
        if re.fullmatch(r'\s*===START===\s*', line):
            ptr = body
            continue
        ptr.append(line)

    return header, body

def process_header(header: list):
    data = dict(title='', characters={})
    
    char_flag = False
    for i, line in enumerate(header):
        if line.startswith('TITLE:'):
            data['title'] = line[7:]
            continue

        if line.startswith('CHARACTERS:'):
            char_flag = True
            continue

        if char_flag:
            match = re.match(r'\s+- (.*)', line)
            if match is None:
                raise ValueError(f'[line {i+1}] expecting character definition, instead found {line!r}')
            char = match.group(1)
            data['characters'][char.upper()] = char
            
    return data

def process_body(body: list, characters: dict):
    lines = []

    for line in body:
        if not line.strip():
            # skip blank lines
            continue

        match = re.match(r'([A-Z]+|-+):\s*(.*)', line)
        if match:
            char, dialogue = match.groups()
            
            if char == 'STAGE':
                # a stage direction
                lines.append(latexcmd('StageDir', dialogue))
                continue
            elif char in characters.keys():
                # spoken dialogue
                v = characters[char]
                lines.append(latexcmd(f'{v}speaks', dialogue))
                continue
            elif set(char) == {'-'}:
                # a continued line, defined by any number of - characters
                lines.append(latexcmd('continue', dialogue))
                continue
        
        # otherwise, allow the line to pass through, unaltered
        lines.append(line)

    return lines


def latexify(asmr: pathlib.Path):
    """Convert a .asmr file to .tex"""
    output = StringIO()

    header, body = split_file(asmr)
    
    # process the header
    proc = process_header(header)
    title = proc['title']
    characters = proc['characters']
    
    # write the header information
    output.writeline(latexcmd('renewcommand', '\\SceneName', title))
    output.writeline(latexcmd('thispagestyle', 'cfirstpage'))
    for ch in characters.values():
        output.writeline(latexcmd('Character', ch, ch))

    # open the drama environment
    output.writeline(latexcmd('begin', 'drama'))
    output.writeline(latexcmd('item', '\\scene[\\SceneName]'))
    
    for line in process_body(body, characters):
        output.writeline(line)
    
    # close the drama environment
    output.writeline(latexcmd('end', 'drama'))

    s = prettify(output.contents)
    return s


def prettify(script: str) -> str:
    def repl(cmd):
        return lambda match: latexcmd(cmd, match.group(1))
    
    # ... -> \ldots
    script = script.replace('...', '\\ldots')
    script = re.sub(r'ldots([A-Za-z0-9])', 'ldots{}\g<1>', script)
    
    # use standard markdown (* for italics, ** for bold, __ for underline, ~~ for strikethrough)
    script = re.sub(r'\*(.*?)\*', repl('textit'), script)
    script = re.sub(r'\*\*(.*?)\*\*', repl('textbf'), script)
    script = re.sub(r'__(.*?)__', repl('ul'), script)
    script = re.sub(r'~~(.*?)~~', repl('st'), script)
    
    # convert [[s]] to \direct{s}
    script = re.sub(r'\[\[(.*?)\]\]', repl('direct'), script)
    
    # convert "ABC" to ``ABC''
    script = re.sub(r'"(.*?)"', r"``\g<1>''", script)
    
    return script


if __name__ == "__main__":
    p = pathlib.Path(__file__).parent.parent / "iza-no-atorie-1.asmr"
    print(latexify(p))
