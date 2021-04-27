"""
The CLI of RAINLotus.
"""
if __name__ != '__main__':
    exit()

try:
    from .v import __version__
except ImportError:
    from v import __version__

import os
import codecs
from sys import stdin, stderr
from pathlib import Path
from argparse import ArgumentParser, RawTextHelpFormatter

def CONCAT(*x) -> str:
    return '\n'.join(x)

FIGLET_CHUNKY = CONCAT(
    r" ______  _______  _______  _______  _____           __",
    r"|   __ \|   _   ||_     _||    |  ||     |_ .-----.|  |_ .--.--..-----.",
    r"|      <|       | _|   |_ |       ||       ||  _  ||   _||  |  ||__ --|",
    r"|___|__||___|___||_______||__|____||_______||_____||____||_____||_____|"
)

cli = ArgumentParser(
    prog='RAINLotus',
    allow_abbrev=False,
    formatter_class=RawTextHelpFormatter,
    description=FIGLET_CHUNKY,
    epilog='See https://github.com/20x48/RAINLotus for details.'
)
cli.add_argument(
    metavar='INPUT',
    dest='input_',
    nargs='+',
    type=Path,
    help=r'File(s) to process; "-" means read from STDIN.'
)
cli.add_argument(
    '-o', '--output',
    type=Path,
    help=CONCAT(
        r'Path to save processed file(s); "-" means write to STDOUT.',
        r'If multiple input files are specified, this must be a directory.',
        r'If the directory not existing, program will create one.'
    )
)
cli.add_argument(
    '-e', '--encoding',
    default='utf-8',
    help=CONCAT(
        r'Specify the encoding of READING file(s). [Default: "%(default)s"]',
        r'CANNOT specify the encoding of WRITING file(s), because utf-8 can solve all problems.'
    )
)
cli.add_argument(
    '-j', '--parse-only',
    action='store_true',
    help=r'Output JSON instead of HTML. [Default: %(default)s]'
)
cli.add_argument(
    '-O', '--overwrite',
    action='store_true',
    help=r'If file already exists, whether to overwrite it. [Default: %(default)s]'
)
cli.add_argument(
    '-q', '--quiet',
    action='store_true',
    help=r'Disable terminal information output. [Default: %(default)s]'
)
cli.add_argument(
    '-V', '--version',
    action='version',
    help='Show version info then exit.',
    version=CONCAT(
       fr'%(prog)s {__version__}',
        r'Copyright (c) 2020-2021 20x48. Licensed under MIT.'
    )
)

args = cli.parse_args()
encoding, input_, output, parse_only, overwrite, quiet = args.encoding, args.input_, args.output, args.parse_only, args.overwrite, args.quiet

try:
    codecs.lookup(encoding)
except LookupError:
    exit(f'Error: unknown encoding: "{encoding}".')

multiple = len(input_) > 1

if multiple:
    use_stdout = False
    if not output:
        exit(1 if quiet else 'Error: multiple input files specified but no output specified.')
    elif str(output) == '-':
        exit(1 if quiet else 'Error: multiple input files specified but output is STDOUT.')
    elif output.is_file():
        exit(1 if quiet else 'Error: multiple input files specified but output is a file.')
    elif not output.exists():
        try:
            os.mkdir(output)
        except OSError as e:
            exit(1 if quiet else f'Error: cannot create output directory: {e.strerror}')
elif not output:
    use_stdout = False
elif str(output) == '-':
    use_stdout = True
else:
    use_stdout = False

try:
    from .p import Parser
    from .r import Renderer, Template
except ImportError:
    from p import Parser
    from r import Renderer, Template

from json import dumps, JSONEncoder

def eprint(msg: str):
    stderr.write(f'{msg}\n')

class CustomJSONEncoder(JSONEncoder):
    def default(self, obj) -> str:
        return JSONEncoder.default(self, tuple(obj) if isinstance(obj, set) else obj)

parse = Parser()
render = Renderer()
if not parse_only:
    template = Template()

for file in input_:
    # 先把原文件加载到内存当中
    if str(file) == '-':
        article = stdin.read()
    else:
        try:
            with open(file, encoding=encoding) as f:
                article = f.read()
        except OSError as e:
            if not quiet:
                eprint(f'Failed: "{file}": {e.strerror}')
            continue
    # 检查输出路径是否已经存在
    if not use_stdout:
        if multiple:
            path = output / (file.stem + ('.json' if parse_only else '.html'))
        else:
            path = file.with_suffix('.json' if parse_only else '.html')
        if path.exists():
            if overwrite:
                if not quiet:
                    eprint(f'Notice: "{path}": overwrote.')
            else:
                if not quiet:
                    eprint(f'Failed: "{path}": output path already exists.')
                continue
        # 试图占个位子
        try:
            output_ = open(path, 'w', encoding='utf-8')
        except OSError as e:
            if not quiet:
                eprint(f'Failed: "{path}": cannot create output file: {e.strerror}')
            continue
    # 处理文件
    article >>= parse
    if parse_only:
        article = dumps(article >> render, ensure_ascii=False, cls=CustomJSONEncoder)
    else:
        article = article >> render >> template
    # 写文件
    if use_stdout:
        print(article)
    else:
        try:
            output_.write(article)
        except Exception as e:
            eprint(f'Failed: "{path}": {e}')
        output_.close()