#!/usr/bin/python3

import argparse
import configparser
import io
import os
import pathlib
import shutil
import subprocess
from typing import List

from latexify import latexify

# should be $HOME/.local/share/lilasmr
lilasmr = pathlib.Path(__file__).absolute().parent.parent

# configuration file
config = configparser.ConfigParser()
config.read(pathlib.Path().home() / ".config" / "lilasmr" / "config.ini")


def process_command_line() -> argparse.Namespace:
    """Parse all arguments and flags given on the command line."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "files",
        nargs="+",
        type=pathlib.Path,
        help="the files to include in the script, in order",
    )

    parser.add_argument(
        "-o", "--output", required=True, type=pathlib.Path, help="path to rendered pdf"
    )

    parser.add_argument(
        "-t", "--title", default=config["Defaults"]["PDFTitle"], help="the pdf title"
    )

    parser.add_argument(
        "-a",
        "--author",
        default=config["Defaults"]["ScriptAuthor"],
        help="the script author",
    )

    parser.add_argument(
        "--preamble",
        type=pathlib.Path,
        default=config["Defaults"]["TeXPreamble"],
        help="the preamble file to use",
    )

    parser.add_argument("-v", "--verbose", action="store_true")

    return parser.parse_args()


def create_tex_file(
    tex_files: List[pathlib.Path], preamble: pathlib.Path, title: str, author: str
):
    s = io.StringIO()

    # include the entire preamble
    with open(preamble, "r") as preamble:
        if title == "@filename":
            # create special rule for $filename -> the filename
            title = tex_files[0].with_suffix(".pdf").name
        pre = (
            preamble.read()
            .replace(":::TITLE:::", title)
            .replace(":::AUTHOR:::", author)
        )
        s.write(pre)

    s.write(r"\begin{document}" + "\n")

    # handle each input file
    for script in tex_files:
        # shutil.copy(script, lilasmr / "staging" / (script.stem + ".tex"))
        s.write(r"\input{" + script.stem + "}\n")

    s.write(r"\end{document}")

    # write tex to file
    out = lilasmr / "staging" / "main.tex"
    with open(out, "w") as f:
        s.seek(0)
        f.write(s.read())

    return out


def render_pdf(tex: pathlib.Path, verbose: bool = False):
    cwd = os.getcwd()
    os.chdir(tex.resolve().parent)

    # render the pdf file
    xelatex = ["xelatex", "-synctex=1", "-interaction=nonstopmode", tex.resolve()]
    subprocess.run(xelatex, capture_output=not verbose)

    # clean up the directory
    # latexmk = ["latexmk", "-c"]
    # subprocess.run(latexmk)

    os.chdir(cwd)


def main():
    args = process_command_line()

    # clean up the staging folder
    for s in (lilasmr / "staging").iterdir():
        s.unlink()

    # process the .asmr files
    for f in args.files:
        tex = latexify(f)
        with open(lilasmr / "staging" / (f.stem + ".tex"), "w") as q:
            q.write(tex)

    # create the main.tex file
    main_tex = create_tex_file(
        tex_files=args.files,
        preamble=args.preamble,
        title=args.title,
        author=args.author,
    )

    # render it to main.tex
    render_pdf(main_tex, verbose=args.verbose)

    # move the pdf to the desired location
    shutil.move(lilasmr / "staging" / "main.pdf", args.output.resolve())


if __name__ == "__main__":
    main()
