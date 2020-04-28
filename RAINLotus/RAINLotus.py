"""
::: RAINLotus
    A markup language.
::: (This program) RAINLotus
    A converter for converting text written in RAINLotus to HTML.
    Also named "RAINLotus".
--------------------------------------------------------------------------------
MIT License

Copyright (c) 2020 20x48

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
__author__ = '20x48'
__version__ = '1.1.1'
import logging
from os import walk, chdir, mkdir
from re import sub, compile, IGNORECASE
from csv import reader, QUOTE_NONE
from sys import stdin, stdout, exit
from json import loads, JSONDecodeError
from time import strftime, localtime
from random import random
from base64 import b32encode
from codecs import getencoder
from typing import Text, List, Dict, Iterable
from pathlib import Path
from hashlib import blake2s
from itertools import chain, repeat
from collections import defaultdict
#                   r
#                  r
#                 r
##################r###
# Regular Expressirn #
##################r###
# 好样哒, 保持队形ヾ(ｏ･ω･)ﾉ
# Common          r
RE_MAIL = compile(r'([A-Za-z0-9\u4e00-\u9fa5]+@[\w\-]+(?:\.[\w\-]+)+)')
# Mark            r
RE_SECT = compile(r'(\w+)((?: +\w+(?:=(?:".*?(?:\"".*?)*"|\w+))?)*):(?:  *(.*?) *| *)')
RE_MARK = compile(r'(?:(\w+)\.)?(\w+)((?: +\w+(?:=(?:".*?(?:\\".*?)*"|\w+))?)*)(?: *% *(.*?) *)?')
RE_ARGS = compile(r'(\w+)(?:=(?:"(.*?(?:"".*?)*)"|(\w+)))?')
# Config          r 嘿! ヾ(･ω･*)ﾉ
RE_ALIAS = compile(r' *(\w+)(?: *-> *(\w+))? *')
# Table            r
RE_TABLE = compile(r'(?:(quick|csv|json)(?: +(\d+))?)(?: +(rotate))?', IGNORECASE)
# Dialog           r
RE_DIALOG = compile(r'(?:(->|<-|::)|(:)?(?=\S)(.*?\S):)(?:  *(.*?) *| *)')
#                   r
#                    r
#                     r
# Content              r
RE_QUICK_HEAD = compile(r'(={2,6}) +(.+?) *')
RE_QUICK_LIST = compile(r'(\d+|[\.+XWDYN])\.(?:| +(.*?)) *')
RE_QUICK_ALLS = compile(r'([!"#$&*/:;>@`|~])\1{2}(?:  *(.*?) *| *)')
RE_ANYTH_INGS = compile(r'([*+\-/=^_~]{2})(?=\S)(.*?\S)\1'                      # "Hang Bue Lang"   | 0  1
                        r'|=([CSX]?\d+)='                                       # Shield            | 2
                        r'|/\*(?=\S)(.*?\S)\*/'                                 # Bold italic       | 3
                        r'|`(?=\S)(.*?\S)`'                                     # Code              | 4
                        r'|\$\$(.+?)\$\$'                                       # Inline formula    | 5
                        r'|\{(\S+?)\}'                                          # Reuse             | 6
                        r'|\[(##|#|\^)(?=\S)(.*?\S)\](?:\((?=\S)(.*?\S)\))?'    # Refer             | 7  8  9
                        r'|(?:\[([!~*]?)(?=\S)(.*?\S)\])?<(?=\S)(.*?\S)>'       # Link              | 10 11 12
                        r'|<<(?:(\w+)\.)?(\w+)\)(?:\((?=\S)(.*?\S)\))?')        # Customize         | 13 14 15
############# ヽ(;・＿・)ノ 停停停!
# RESOURCES #
#############
ABSOLUTE = Path(__file__).parent
with open(ABSOLUTE/'Template.html', encoding='utf-8') as f:
    HTML_TEMPLATE = f.read()
with open(ABSOLUTE/'Light.css', encoding='utf-8') as f:
    CSS_LIGHT = f.read()
CSS_HIGHLIGHT = '''<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/prismjs@1.19.0/themes/prism-tomorrow.min.css" />'''
JS_DIAGRAM = '''\
<script src="https://cdn.jsdelivr.net/npm/mermaid@8.4.8/dist/mermaid.min.js"></script>\
<script>mermaid.init(undefined,'.RM_diagram');</script>'''
JS_FORMULA = '''\
<script>var MathJax={tex:{inlineMath:[['$','$']],displayMath:[['$$','$$']]},options:{ignoreHtmlClass:'.*',processHtmlClass:'R[MS]_formula'}};</script>\
<script src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-svg.js"></script>'''
JS_HIGHLIGHT = '''\
<script src="https://cdn.jsdelivr.net/npm/prismjs@1.19.0/components/prism-core.min.js"></script>\
<script src="https://cdn.jsdelivr.net/npm/prismjs@1.19.0/plugins/autoloader/prism-autoloader.min.js"></script>'''
############
# Defaults #
############
DEFAULTS = defaultdict(lambda:False, {'toc': True})


def rain(path:Text, encoding:Text = 'utf-8', settings:Dict = {}) -> Dict:
    with open(path, 'r', encoding=encoding) as f:
        s = f.read()
    return rains(s, settings)


def rains(s:Text, settings:Dict = {}) -> Dict:
    return RAINLotus(settings).parse(s)


def fullpage(result:Dict, charset:Text = 'utf-8') -> Text:
    # TOC
    toc = list(filter(lambda x:x[0]<=result['toc_level'], result['toc']))
    toc = f'''<p>Table of Content</p><div>{''.join(
        f'<p class="_{qwq}"><a href="#H{RAINLotus._hash(text)}">{RAINLotus._escape_char(text)}</a></p>'
        for qwq, text in toc
    )}</div>''' if toc else '<p>(No table of content here)</p>'
    # JS
    before, js = [], []
    if result['diagram']:
        js.append(JS_DIAGRAM)
    if result['formula']:
        js.append(JS_FORMULA)
    if result['highlight']:
        before.append(CSS_HIGHLIGHT)
        js.append(JS_HIGHLIGHT)
    # Header
    header = result['header']
    if not header:
        header = 'Page by RAINLotus'
    # Metas
    try:
        metas = ''.join((f'<meta name="{k}" content="{RAINLotus._escape_char(v)}" />' for k, v in result['config']['RAINLotus']['meta'].items() if k in {'author', 'description', 'keywords'}))
    except KeyError:
        metas = ''
    # GG
    return HTML_TEMPLATE.format(
        charset=charset,
        version=__version__,
        metas=metas,
        title=header,
        css=CSS_LIGHT,
        before=''.join(before),
        header=header,
        toc=toc,
        content=result['content'],
        js=''.join(js))


class RAINLotus:
    def __init__(self, settings={}):
        self.settings = settings
        self.enable_toc = self._get_setting('toc')
        self.enable_diagram = self._get_setting('diagram')
        self.enable_formula = self._get_setting('formula')
        self.enable_highlight = self._get_setting('highlight')
        self.enable_raw = self._get_setting('raw')

    def parse(self, raw) -> Text:
        # Header
        lines = raw.splitlines()
        try:
            header, qwq = lines[:2]
        except ValueError:
            header = ''
            have_header = 0
        else:
            if (not header or header.isspace()) or (not qwq or qwq.count('=') != len(qwq.strip())):
                header = ''
                have_header = 0
            else:
                have_header = 2
        # TOC
        self.toc = []
        self.toc_level = 3
        # Diagram
        self.have_diagram = False
        # Formula
        self.have_formula = False
        # Highlight
        self.have_highlight = False
        #### Parse ! ####
        impt, config, children = self.lotus(lines[have_header:])
        config = self._config_integrate(impt, config)
        content = self.chunk(impt, config, children)
        #### OJBK ####
        return {
            'config': config,
            'header': self._escape_char(header),
            'toc': self.toc,
            'toc_level': self.toc_level,
            'content': content,
            'diagram': self.have_diagram,
            'formula': self.have_formula,
            'highlight': self.have_highlight,
        }

    def lotus(self, lines, start=0, status=1, indent=0) -> (Dict, Dict, List):
        impt, config, result = {}, defaultdict(list), []
        index, jump = start, 0
        if status == 2:
            more = 0
        for index, line in enumerate(lines[start:], start):
            # 掠过行
            if jump:
                jump -= 1
                continue
            # 忽略空白行
            if line.isspace() or not line:
                if status == 2:
                    more += 1
                continue
            # 探寻缩进等级
            pos = 0
            back = False
            while pos < len(line) and line[pos] == ' ':
                pos += 1
            if status == 2:
                pos_ = indent * 4
                if pos < pos_:
                    back = True
                else:
                    pos = pos_
            else:
                div, mod = divmod(pos, 4)
                if div < indent:
                    back = True
                elif mod != 0 or div > indent:
                    continue
            # 错误缩进的处理
            if back:
                index -= 1
                if status == 0:
                    return index
                else:
                    return index, result
            # ０: 注释
            if status == 0:
                continue
            if pos:
                line = line[pos:]
            line = line.rstrip()
            prefix = line[0]
            # Ｘ -> Ｑ
            # １: 正文
            if status == 1:
                # Quick-head
                if prefix == '=':
                    Xhead = RE_QUICK_HEAD.fullmatch(line)
                    if Xhead:
                        Qtype, Qhead = Xhead.groups()
                        Qtype = len(Qtype)
                        result.append([(None, f'h{Qtype}'), None, Qhead])
                        if self.enable_toc:
                            if not indent:
                                self.toc.append((Qtype, Qhead))
                        continue
                # Quick-list
                elif prefix in '.0123456789+XWDYN':
                    Xlist = RE_QUICK_LIST.fullmatch(line)
                    if Xlist:
                        Qstart, Qlist = Xlist.groups()
                        # . 0101110
                        # + 0101011
                        # 0 0110000
                        # 1 0110001
                        #...
                        # 9 0111001
                        #   v
                        # X 1011000
                        # W 1010111
                        # D 1000100
                        # Y 1011001
                        # N 1001110
                        prefis = ord(prefix)
                        Qtype, Qstatus = ('u', 3) if prefis==0b101110 else ('t', 5) if prefis>>6 else ('o', 4)
                        Qindex, Qresult = self.lotus(lines, index+1, 1, indent+1)
                        Qchild = [[prefix, [Qlist]+Qresult if Qlist else Qresult]]
                        QL = len(lines) - 1
                        while Qindex < QL:
                            Qindex, Qresult = self.lotus(lines, Qindex+1, Qstatus, indent)
                            if Qresult:
                                Qchild.append(Qresult)
                            else:
                                break
                        result.append([(None, f'{Qtype}list'),
                                       Qstart if Qstatus==4 and Qstart not in '1+' else None,
                                       Qchild])
                        jump = Qindex - index
                        continue
                # Separator & page break
                elif prefix in "%-" and 3 <= len(line) == line.count(prefix):
                    # % 100101
                    # - 101101
                    result.append([(None, ['pgbreak', 'sep'][(ord(prefix)>>3)&1])])
                    continue
                # Anything
                else:
                    Xline = RE_QUICK_ALLS.fullmatch(line)
                    if Xline:
                        Quick = Xline.group(2)
                        # Config
                        if prefix == '&' and indent == 0:
                            Qconfig = RE_ALIAS.fullmatch(Quick)
                            if Qconfig:
                                Qmodule, Qalias = Qconfig.groups()
                                if Qalias and Qmodule != 'RAINLotus':
                                    # impt[Qalias] = Qmodule    # TODO here.
                                    pass
                                Qindex, Qresult = self.lotus(lines, index+1, 7, indent+1)
                                config[Qmodule].extend(Qresult)
                                jump = Qindex - index
                        # Mark
                        # elif prefix == '/':
                        #     Xmark = RE_MARK.fullmatch(Quick)
                        #     if Xmark:
                        #         Qmodule, Qmark, Qargs, Qtext = Xmark.groups()
                        #         Qcheck = self._check_mark(Qmodule, Qmark)
                        #         if Qcheck:
                        #             Qindex, Qresult = self.lotus(lines, index+1, Qcheck, indent+1)
                        #             result.append([(Qmodule, Qmark), {k:(v1 if v1 else v2) for k, v1, v2 in RE_ARGS.findall(Qargs)}, [Qtext]+Qresult if Qtext else Qresult])
                        #         else:
                        #             Qindex = self.lotus(lines, index+1, 0, indent+1)
                        #             if Qcheck == 0:
                        #                 result.append([(Qmodule, Qmark), {k:(v1 if v1 else v2) for k, v1, v2 in RE_ARGS.findall(Qargs)}, Qtext])
                        #         jump = Qindex - index
                        # Note
                        elif prefix == '*':
                            # TIP: 好东西/废话
                            # NOTE: 注解/小细节
                            # IMPORTANT: 那些让你没那么容易逝世的细节
                            # CAUTION: 新手劝退
                            # WARNING: 试试就逝世
                            if Quick in {'TIP', 'NOTE', 'IMPORTANT', 'CAUTION', 'WARNING'}:
                                Qindex, Qresult = self.lotus(lines, index+1, 1, indent+1)
                                result.append([(None, 'note'), Quick, Qresult])
                                jump = Qindex - index
                        # Quote
                        elif prefix == '"':
                            Qindex, Qresult = self.lotus(lines, index+1, 1, indent+1)
                            if Quick and (Quick.startswith('--') or Quick.startswith('——')):
                                result.append([(None, 'quote'), Quick[2:].strip(), Qresult])
                            else:
                                result.append([(None, 'quote'), None, [Quick]+Qresult])
                            jump = Qindex - index
                        # Defined-list
                        elif prefix == ':':
                            if Quick:
                                Qindex, Qresult = self.lotus(lines, index+1, 1, indent+1)
                                Qchild = [[Quick, Qresult]]
                                QL = len(lines) - 1
                                while Qindex < QL:
                                    Qindex, Qresult = self.lotus(lines, Qindex+1, 6, indent)
                                    if Qresult:
                                        Qchild.append(Qresult)
                                    else:
                                        break
                                result.append([(None, 'dlist'), None, Qchild])
                                jump = Qindex - index
                        # Table
                        elif prefix == '|':
                            Xtable = RE_TABLE.fullmatch(Quick)
                            if Xtable:
                                Qmode, QH, Qrotate = Xtable.groups()
                                Qindex, Qresult = self.lotus(lines, index+1, 2, indent+1)
                                result.append([(None, 'table'),
                                               [Qmode.lower(),
                                                int(QH) if QH else 1,
                                                True if Qrotate else False],
                                               Qresult])
                                jump = Qindex - index
                        # Coll
                        elif prefix == '~':
                            if Quick:
                                try:
                                    Qopen, Qsummary = Quick.split(' ', 1)
                                    if Qopen != 'open':
                                        Qopen, Qsummary = False, Quick
                                except ValueError:
                                    if Quick == 'open':
                                        Qopen, Qsummary = True, ''
                                    else:
                                        Qopen, Qsummary = False, Quick
                            else:
                                Qopen, Qsummary = False, ''
                            Qindex, Qresult = self.lotus(lines, index+1, 1, indent+1)
                            result.append([(None, 'coll'), (Qopen, Qsummary), Qresult])
                            jump = Qindex - index
                        # Dialog
                        elif prefix == '@':
                            Qindex, Qresult = self.lotus(lines, index+1, 10, indent+1)
                            result.append([(None, 'dialog'), Quick, Qresult])
                        # Footnote & Code
                        elif prefix in '>`':
                            if Quick:
                                # > 0111110
                                # ` 1100000
                                prefix = ord(prefix) >> 6
                                Qindex, Qresult = self.lotus(lines, index+1, prefix+1, indent+1)
                                result.append([(None, ['footnote', 'code'][prefix]), Quick, Qresult])
                                jump = Qindex - index
                        # Raw & Diagram & Formula
                        elif prefix in '!#$':
                            # ! 100001
                            # # 100011
                            # $ 100100
                            prefix = ord(prefix) >>1 & 3
                            Qindex, Qresult = self.lotus(lines, index+1, 2, indent+1)
                            result.append([(None, ['raw', 'diagram', 'formula'][prefix]), None, [Quick]+Qresult if Quick else Qresult])
                        # Comment
                        elif prefix == ';':
                            Qindex = self.lotus(lines, index+1, 0, indent+1)
                            jump = Qindex - index
                        continue
            # ３４５: 无序/有序/Todos 列表延续
            elif status in (3, 4, 5):
                Xlist = RE_QUICK_LIST.fullmatch(line)
                if Xlist:
                    prefis = ord(prefix)
                    Qtext = Xlist.group(2)
                    Qstatus = 3 if prefis==0b101110 else 5 if prefis>>6 else 4
                    if status == Qstatus:
                        Qindex, Qresult = self.lotus(lines, index+1, 1, indent+1)
                        return Qindex, [prefix, [Qtext]+Qresult if Qtext else Qresult]
                return index-1, None
            # ６: 定义列表延续
            elif status == 6:
                if prefix == ':':
                    Xlist = RE_QUICK_ALLS.fullmatch(line)
                    if Xlist:
                        Qdefi = Xlist.group(2)
                        if Qdefi:
                            Qindex, Qresult = self.lotus(lines, index+1, 1, indent+1)
                            return Qindex, [Qdefi, Qresult]
                return index-1, None
            # ７: 配置解析
            elif status == 7:
                QS = RE_SECT.fullmatch(line)
                if QS:
                    Qcommand, Qargs, Qtext = QS.groups()
                    Qindex, Qersult = self.lotus(lines, index+1, 2, indent+1)
                    result.append([Qcommand, {k:(v1 if v1 else v2 if v2 else '') for k, v1, v2 in RE_ARGS.findall(Qargs)}, [Qtext]+Qersult if Qtext else Qersult])
                    jump = Qindex - index
                continue
            # 10: Dialog
            elif status == 10:
                # 0b000: 自己的话
                # 0b001: 自己的话 - 有名字
                # 0b010: 对方的话
                # 0b011: 对方的话 - 有名字
                # 0b100: 提示
                Xdialog = RE_DIALOG.fullmatch(line)
                if Xdialog:
                    Qtype, Qself, Qname, Qtext = Xdialog.groups()
                    if Qtype:
                        Qmode = {'<-': 0, '->': 2, '::': 4}[Qtype]
                    else:
                        Qmode = 1 if Qself else 3
                    Qindex, Qresult = self.lotus(lines, index+1, 1, indent+1)
                    result.append([Qmode, Qname, [Qtext]+Qresult if Qtext else Qresult])
                continue
            # ２: 不解析
            if status == 2:
                result.extend(repeat('', more))
                more = 0
            result.append(line)
        if status == 0:
            return index
        elif indent > 0:
            return index, result
        else:
            return impt, config, result

    def chunk(self, impt, config, children) -> Text:
        result = []
        for child in children:
            if isinstance(child, str):
                result.append(self.inline(impt, config, child))
            else:
                module, mark = child[0]
                if module:
                    continue    # TODO: Extension module.
                else:
                    if mark in {'h2', 'h3', 'h4', 'h5', 'h6'}:
                        result.append(self._mark_head(impt, config, mark[1], child[2]))
                        continue
                    # （づ￣3￣）づ╭❤～
                    func = {
                        'note': self._mark_note,
                        'quote': self._mark_quote,
                        'ulist': self._mark_ulist,
                        'olist': self._mark_olist,
                        'tlist': self._mark_tlist,
                        'dlist': self._mark_dlist,
                        'table': self._mark_table,
                        'coll': self._mark_coll,
                        'dialog': self._mark_dialog,
                        'footnote': self._mark_footnote,
                    }.get(mark)
                    if func:
                        result.append(func(impt, config, child[1], child[2]))
                        continue
                    # (〃'▽'〃)
                    if mark == 'code':
                        result.append(self._mark_code(child[1], child[2]))
                        continue
                    # ヾ(=･ω･=)o
                    func = {
                        'diagram': self._mark_diagram,
                        'formula': self._mark_formula,
                        'raw': self._mark_raw,
                    }.get(mark)
                    if func:
                        result.append(func(child[2]))
                        continue
                    #  (=´ω｀=)
                    func = {
                        'sep': self._mark_sep,
                        'pgbreak': self._mark_pgbreak,
                    }.get(mark)
                    if func:
                        result.append(func())
        return ''.join(result)

    def _mark_head(self, impt, config, mark, head):
        hash_ = f'H{self._hash(head)}'
        return f'''<h{mark} class="RM_header" id="{hash_}">{self._escape_char(head)}<a href="#{hash_}"></a></h{mark}>'''

    def _mark_note(self, impt, config, style, children):
        return f'''<div class="RM_note {style.lower()}"><div>{self.chunk(impt, config, children)}</div></div>'''

    def _mark_quote(self, impt, config, author, children):
        return f'''<div class="RM_quote"><blockquote>{self.chunk(impt, config, children)}</blockquote>{f'<p>——{self.inline(impt, config, author, True)}</p>' if author else ''}</div>'''

    def _mark_ulist(self, impt, config, _, children):
        return f'''<ul class="RM_list">{''.join(
            f'<li>{self.chunk(impt, config, child)}</li>'
            for qwq, child in children
        )}</ul>'''

    def _mark_olist(self, impt, config, start, children):
        try:
            start = int(start)
        except TypeError:
            start = None
        return f'''<ol class="RM_list"{f' start="{start}"' if start else ''}>{''.join(
            f'<li>{self.chunk(impt, config, child)}</li>'
            for qwq, child in children
        )}</ol>'''

    def _mark_tlist(self, impt, config, _, children):
        return f'''<ul class="RM_tlist">{''.join(
            f"""<li class="_{qwq}">{self.chunk(impt, config, child)}</li>"""
            for qwq, child in children
        )}</ul>'''

    def _mark_dlist(self, impt, config, _, children):
        return f'''<dl class="RM_dlist">{''.join(
            f'<dt>{self.inline(impt, config, qwq, True)}</dt><dd>{self.chunk(impt, config, child)}</dd>'
            for qwq, child in children
        )}</dl>'''

    def _mark_table(self, impt, config, args, children):
        mode, TH, _ = args
        if mode == 'quick':
            fresh = map(lambda x:x[1:], reader(children, delimiter='|', escapechar='\\', quoting=QUOTE_NONE))
        elif mode == 'csv':
            fresh = reader(children)
        elif mode == 'json':
            try:
                fresh = loads(''.join(children), parse_int=str, parse_float=str, parse_constant=str)
            except JSONDecodeError:
                return ''
        table = [[], []]
        columns = 0
        if isinstance(fresh, dict):
            try:
                thead, tlign, tbody = fresh['head'], fresh['align'], fresh['body']
            except KeyError:
                return ''
            if any(map(lambda x:not isinstance(x, list), (thead, tlign, tbody))):
                return ''
            TH = len(thead)
            fresh = chain(thead, [tlign], tbody)
        if isinstance(fresh, Iterable):
            for index, cells in enumerate(fresh):
                if not cells:
                    return ''
                if index == TH:
                    # < 111100
                    # = 111101
                    # > 111110
                    #       ^^
                    align_core = []
                    alipay = align_core.append
                    if all(map(lambda x:x[1], map(lambda x:(alipay(x), x in {'<', '=', '>'}), map(lambda x:x.strip(), cells)))):
                        align_core = [ord(i)&3 for i in align_core]
                        align = lambda x:('left', 'center', 'right')[align_core[x]]
                        check = len(align_core)
                    elif align_core[0] in {'<<<', '===', '>>>'}:
                        align_core = ('left', 'center', 'right')[ord(align_core[0][0])&3]
                        align = lambda x:align_core
                        check = -1
                    else:
                        return ''
                else:
                    row = []
                    check = 0
                    merged = 1
                    for check, cell in enumerate(map(lambda x:x.strip(), cells), 1):
                        if cell in {'>', '>>>'}:
                            if check == 1:
                                return ''
                            elif cell == '>':
                                merged += 1
                                continue
                            elif not columns:
                                return ''
                            else:
                                merged = 0
                                check = -1
                                break
                        elif check == 1:
                            last = cell
                        else:
                            row.append((last, merged))
                            last = cell
                            merged = 1
                    table[0 if index<TH else 1].append(row+[(last, merged)])
                if columns:
                    if -1 != check != columns:
                        return ''
                elif check != -1:
                    columns = check
        else:
            return ''
        result = [[], []]
        for i, tag, rows in zip((0, 1), ('th', 'td'), table):
            for cells in rows:
                total, qwq = 0, []
                for cell, span in cells:
                    if span > 1:
                        qwq.append(f'<{tag} colspan="{span}" style="text-align:center">{self.inline(impt, config, cell, True)}</{tag}>')
                    elif span == 1:
                        qwq.append(f'<{tag} style="text-align:{align(total)}">{self.inline(impt, config, cell, True)}</{tag}>')
                    else:
                        qwq.append(f'<{tag} colspan="{columns-total}" style="text-align:center">{self.inline(impt, config, cell, True)}</{tag}>')
                        break
                    total += span
                result[i].append(f'<tr>{"".join(qwq)}</tr>')
        return f'<div class="RM_table"><table><thead>{"".join(result[0])}</thead><tbody>{"".join(result[1])}</tbody></table></div>'

    def _mark_coll(self, impt, config, args, children):
        opem, summary = args
        return f'''<details class="RM_coll" {' open' if opem else ''}><summary>{self.inline(impt, config, summary, True)}</summary>{self.chunk(impt, config, children)}</details>'''

    def _mark_dialog(self, impt, config, name, children):
        return f'''<div class="RM_dialog">{
            f'<div class="_0">{self.inline(impt, config, name)}</div>'
            if name else ''
        }<div class="_1">{''.join(
            f"""<div class="_{mode>>1}">{f'<p>{self.inline(impt, config, nick, True)}</p>' if mode&1 else ''}<div>{''.join(
                self.inline(impt, config, one) if isinstance(one, str) else self.chunk(impt, config, one)
            )}</div></div>"""
            for mode, nick, child in children
            for one in child
        )}</div></div>'''

    def _mark_footnote(self, impt, config, name, children):
        href = self._hash(name)
        return f'''<div class="RM_footnote"><div><a class="RS_link" id="B{href}" href="#A{href}">{self.inline(impt, config, name, True)}</a></div><div>{self.chunk(impt, config, children)}</div></div>'''

    def _mark_code(self, lang, lines):
        lang = self._escape_char(lang)
        if self.enable_highlight:
            self.have_highlight = True
        return f'''<pre class="RM_code"><code class="language-{lang}">{"""
""".join(self._escape_char(line) for line in lines)}</code></pre>'''

    def _mark_diagram(self, lines):
        if self.enable_diagram:
            self.have_diagram = True
            return f'''<div class="RM_diagram">{self._escape_char("""
""".join(lines))}</div>'''
        return ''

    def _mark_formula(self, lines):
        if self.enable_formula:
            self.have_formula = True
            return f'''<div class="RM_formula">$${self._escape_char(''.join(lines))}$$</div>'''
        return ''

    def _mark_raw(self, raw):
        if self.enable_raw:
            return f'<div class="RM_raw">{"".join(raw)}</div>'
        return ''

    def _mark_sep(self):
        return '<hr />'

    def _mark_pgbreak(self):
        return '<div style="page-break-after:always"></div>'

    def inline(self, impt, config, text, internal=False) -> Text:
        result = []
        anything = RE_ANYTH_INGS.search(text)
        last = 0
        while anything:
            result.append(self._escape_char(text[last:anything.start()]))
            ant = anything.groups()
            if ant[0]:      # "Hang Bue Lang"
                result.append(self._symbols(impt, config, ant[0], ant[1]))
            elif ant[2]:    # Shield
                result.append(self._symbols(impt, config, '=', ant[2]))
            elif ant[3]:    # Bold italic
                result.append(self._symbols(impt, config, '/*', ant[3]))
            elif ant[4]:    # Code
                result.append(self._symbols(impt, config, '`', ant[4]))
            elif ant[5]:    # Inline formula
                result.append(self._symbols(impt, config, '$$', ant[5]))
            elif ant[6]:    # Reuse
                result.append(self._symbols(impt, config, '{}', ant[6]))
            elif ant[8]:    # Refer
                result.append(self._symbol_refer(impt, config, ant[7], ant[8], ant[9]))
            elif ant[12]:   # Link
                result.append(self._symbol_link(impt, config, ant[10], ant[11], ant[12]))
            # TODO: Extensions
            last = anything.end()
            anything = RE_ANYTH_INGS.search(text, last)
        result.append(self._escape_char(text[last:]))
        return ''.join(result) if internal else f'<p>{"".join(result)}</p>'

    def _symbols(self, impt, config, tp, text):
        if tp == '=':
            try:
                char = {'C': '█', 'S': '＊', 'X': '×'}[text[0]]
                repeat = text[1:]
            except KeyError:
                char = '*'
                repeat = text
            try:
                repeat = int(repeat)
            except ValueError:
                return ''
            else:
                return f'<span class="RS_shield">{char * repeat}</span>'
        elif tp == '/*':
            return f'<strong class="RS_bit"><em>{self.inline(impt, config, text, True)}</em></strong>'
        elif tp == '`':
            return f'<code class="RS_code">{self._escape_char(text)}</code>'
        elif tp == '$$':
            if self.enable_formula:
                self.have_formula = True
                return f'<span class="RS_formula">${self._escape_char(text)}$</span>'
            return ''
        elif tp == '{}':
            try:
                return config['RAINLotus']['alias'].get(text, '')
            except KeyError:
                return ''
        elif tp in {'^^', '__'}:
            tag = {'^^': 'sup', '__': 'sub'}[tp]
            return f'<{tag}>{self.inline(impt, config, text, True)}</{tag}>'
        else:
            tag, xls = {'**': ('strong', 'bold'),
                        '++': ('mark', 'mark'),
                        '--': ('span', 'dim'),
                        '//': ('em', 'italic'),
                        '==': ('a', 'shady'),
                        '~~': ('del', 'strike')}[tp]
            return f'<{tag} class="RS_{xls}">{self.inline(impt, config, text, True)}</{tag}>'

    def _symbol_refer(self, impt, config, mode, href, alt):
        if mode in '#^':
            hash_ = self._hash(href)
            desc = self.inline(impt, config, alt, True) if alt else self._escape_char(href)
            if mode == '#':
                return f'''<a class="RS_link" href="#H{hash_}">{desc}</a>'''
            else:
                return f'''<sup><a class="RS_link" id="A{hash_}" href="#B{hash_}">{desc}</a></sup>'''
        else:
            try:
                href_, hash_ = href.split('#', 1)
            except ValueError:
                return self._escape_char(href)
            else:
                return f'''<a class="RS_link" href="{self._escape_char(href_)}#H{self._hash(hash_)}">{self.inline(impt, config, alt, True) if alt else self._escape_char(href)}</a>'''

    def _symbol_link(self, impt, config, mode, alt, href):
        if alt in ('!', '~', '*'):
            mode, alt = alt, mode
        if mode == '!':
            return f'''<img class="RS_image" src="{self._escape_char(href)}"{f' alt="{self.inline(impt, config, alt, True)}"' if alt else ''} />'''
        elif mode in ('~', '*'):
            attr = []
            if 'A' in alt:
                attr.append('autoplay')
            if 'L' in alt:
                attr.append('loop')
            if 'M' in alt:
                attr.append('muted')
            if 'P' in alt:
                attr.append('preload')
            # * 0101010
            # ~ 1111110
            tag = ['video', 'audio'][ord(mode)>>6]
            return f'''<{tag} class="RS_{tag}" src="{self._escape_char(href)}" controls{' ' + ' '.join(attr) if attr else ''}></{tag}>'''
        elif href.startswith('mailto:') or RE_MAIL.match(href):
            return f'<a class="RS_link" href="{self._escape_mail(f"mailto:{href}")}">{self._escape_mail(alt if alt else href)}</a>'
        elif alt or any(map(lambda x:href.startswith(x), ('https://', 'http://', 'ftp://'))):
            return f'<a class="RS_link" href="{self._escape_char(href)}">{self.inline(impt, config, alt, True) if alt else self._escape_char(href)}</a>'
        else:
            return self._escape_char(href)

    def _config_integrate(self, impt, config):
        result = defaultdict(dict)
        for module, package in config.items():
            if module != 'RAINLotus':
                continue    # TODO
            else:
                func = self._config_analyze
                for command, args, values in package:
                    items = func(self, impt, config, command, args, values)
                    if isinstance(items, dict):
                        try:
                            result[module][command].update(items)
                        except KeyError:
                            result[module][command] = items
                    else:
                        result[module][command] = items
        return result

    def _config_analyze(self, _, impt, config, command, args, values):
        if command in {'alias', 'meta'}:
            result = {}
            func = self._escape_char if command == 'meta' else self._escape_char if 'raw' in args else lambda x:self.inline(impt, config, x, True)
            for value in values:
                try:
                    qwq, QAQ = value.split(' ', 1)
                except ValueError:
                    continue
                else:
                    result[qwq] = func(QAQ)
        elif command == 'toc_level':
            try:
                self.toc_level = int(values[0][:1])
            finally:
                return None
        else:
            return None
        return result

    def _get_setting(self, *vs):
        try:
            d = self.settings[vs[0]]
            for v in vs[1:]:
                d = d[v]
        except KeyError:
            d = DEFAULTS[vs[0]]
            for v in vs[1:]:
                d = d[v]
        return d

    @staticmethod
    def _escape_char(text) -> Text:
        return ''.join({'"':'&#34;',
                        '&':'&amp;',
                        '<':'&lt;'}.get(c, c) for c in text)

    @staticmethod
    def _escape_mail(text) -> Text:
        return ''.join(f'&#{ord(c)};' if random() < 0.5 else f'&#x{ord(c):x};' for c in text)

    @staticmethod
    def _hash(text) -> Text:
        return b32encode(blake2s(text.encode(), digest_size=5).digest()).decode()


def cli():
    from argparse import ArgumentParser, RawTextHelpFormatter
    parser = ArgumentParser(
        prog='RAINLotus',
        allow_abbrev=False,
        formatter_class=RawTextHelpFormatter,
        description=r''' ______  _______  _______  _______  _____           __
|   __ \|   _   ||_     _||    |  ||     |_ .-----.|  |_ .--.--..-----.
|      <|       | _|   |_ |       ||       ||  _  ||   _||  |  ||__ --|
|___|__||___|___||_______||__|____||_______||_____||____||_____||_____|''',
        epilog='See https://docs.20x48.net/RAINLotus for documentation.')
    parser.add_argument(metavar='INPUT', dest='r', default=stdin, nargs='?', type=Path, help='''\
File to convert. [Default: <stdin>]
Directory is allowed, recursively convert the files inside
and save to a new directory. (In this way, filename follow super header defined inside)''')
    parser.add_argument('-o', '--out', metavar='OUTPUT', dest='w', default=stdout, type=Path, help='''\
Path to save. [Default: <stdout>]
If `in` is a directory: [Default: "RAINLotus_{YYYY-mm-dd_HH.MM.SS}"]
Whatever `in` is, raise error when `out` is a existed directory.''')
    parser.add_argument('--no-diagram', dest='diagram', action='store_false', help='''\
Disable diagram. [Default: False]
(Powered by mermaid@8.4.8. See https://github.com/mermaid-js/mermaid for details.)''')
    parser.add_argument('--no-formula', dest='formula', action='store_false', help='''\
Disable formulas. [Default: False]
(Powered by mathjax@3. See https://www.mathjax.org/ for details.)''')
    parser.add_argument('--no-highlight', dest='highlight', action='store_false', help='''\
Disable highlight. [Default: False]
(Powered by prismjs@1.19.0. See https://prismjs.com/ for details.)''')
    parser.add_argument('--with-raw', dest='raw', action='store_true', help='Enable raw. [Default: False]')
    parser.add_argument('-e', '--encoding', default='utf-8', help='Specify encoding of file(s). [Default: "utf-8"]')
    parser.add_argument('-s', '--suffix', default=['.lotus'], nargs='+', help='Allowed suffixes. [Default: [".lotus"]] (Leading dot is required)')
    parser.add_argument('-v', '--verbose', dest='verbose', action='count', default=0, help='Logging level.')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode.')
    parser.add_argument('--version', action='version', help='Show version and exit.', version=f'''\
%(prog)s V{__version__}
Copyright (c) 2020, 20x48. Licensed by MIT.''')
    args = parser.parse_args()
    encoding, verbose = args.encoding, args.verbose
    logging.basicConfig(format='[%(msecs)4d] %(levelname)8s :: %(message)s', level=[30, 20, 10][min(verbose, 2)])
    try:
        getencoder(encoding)
    except LookupError:
        logging.critical(f'Bad ENCODING provided: {encoding}')
    r, w, diagram, formula, highlight, raw, suffix, debug = args.r, args.w, args.diagram, args.formula, args.highlight, args.raw, args.suffix, args.debug

    if isinstance(r, Path):
        if not r.exists():
            logging.critical(f'Argument IN points to a non-existent path: {r}')
            exit(1)
        elif r.is_dir():
            if w is stdout:
                w = Path(strftime('RAINLotus_%Y-%m-%d_%H.%M.%S', localtime()))
                logging.warning(f'No output directory specified, use: {w}')
                if w.is_dir():
                    logging.critical(f'So awkward, directory "{w}" is already existed. Try again later please.')
                    exit()
            elif w.is_dir():
                logging.critical(f'Argument OUT points to a existed directory: {w}')
                exit()
            PROVIDE_TextIO = False
        else:
            if isinstance(w, Path):
                if w.is_dir():
                    logging.critical(f'Argument OUT points to a existed directory: {w}')
                    exit()
                elif w.exists():
                    logging.warning(f'Overwrite a already existed file: {w}')
            try:
                r = open(r, encoding=encoding)
            except OSError as e:
                logging.error(f'Failed to open file: {e}')
                exit()
            PROVIDE_TextIO = True
    else:
        PROVIDE_TextIO = True

    if PROVIDE_TextIO:
        if debug:
            if isinstance(w, Path):
                w = open(w, 'w', encoding=encoding)
            s = r.read()
            result = rains(s, {'diagram': diagram, 'formula': formula, 'highlight': highlight, 'raw': raw})
            w.write(fullpage(result, charset=encoding))
        else:
            try:
                if isinstance(w, Path):
                    w = open(w, 'w', encoding=encoding)
                s = r.read()
                result = rains(s, {'diagram': diagram, 'formula': formula, 'highlight': highlight, 'raw': raw})
                w.write(fullpage(result, charset=encoding))
            except OSError as e:
                logging.error(f'Failed to open file: {e}')
            except KeyboardInterrupt:
                print('### Terminated ###')
                exit()
            except UnicodeDecodeError as e:
                logging.error(f'Failed to read file: {e}')
            except Exception as e:
                logging.error(f'Unexpected exception: {e}. Please use `--debug` to process the same data again and copy the input and errors, report to https://github.com/20x48/RAINLotus/issues')
            finally:
                r.close()
                w.close()
    else:
        try:
            mkdir(w)
            r = r.absolute()
            chdir(w)
        except OSError:
            logging.critical(f'Failed to create & change to output directory "{w}". Make sure you do not miss anything.')
            exit()
        lotus = RAINLotus({'diagram': diagram, 'formula': formula, 'highlight': highlight, 'raw': raw})
        suffix = set(suffix)
        succeeded, total = 0, 0
        for root, _, files in walk(r, onerror=lambda e:logging.error(f'Failed to traversing directory: {e}')):
            root = Path(root)
            total += len(files)
            for file in map(lambda x:root/x, files):
                if file.suffix in suffix:
                    logging.debug(f'[+] {file}')
                    if debug:
                        with open(file, encoding=encoding) as rr:
                            ww = Path(f'{file.stem}.html')
                            if ww.is_file():
                                ww = Path(f'{file.stem}({RAINLotus._hash(str(root))}).html')
                                if ww.is_file():
                                    logging.error(f'Bingo! Failed to resolve filename conflict: "{ww}" with a probability of one part per trillion!')
                                    continue
                            result = lotus.parse(rr.read())
                            with open(ww, 'w', encoding=encoding) as www:
                                www.write(fullpage(result, charset=encoding))
                    else:
                        try:
                            with open(file, encoding=encoding) as rr:
                                ww = Path(f'{file.stem}.html')
                                if ww.is_file():
                                    ww = Path(f'{file.stem}({RAINLotus._hash(str(root))}).html')
                                    if ww.is_file():
                                        logging.error(f'Bingo! Failed to resolve filename conflict: "{ww}" with a probability of one part per trillion!')
                                        continue
                                result = lotus.parse(rr.read())
                                with open(ww, 'w', encoding=encoding) as www:
                                    www.write(fullpage(result, charset=encoding))
                        except OSError as e:
                            logging.error(f'Failed to open file "{file}": {e}')
                        except KeyboardInterrupt:
                            print(f'### Terminated: {succeeded} / {total} file(s) succeeded ###')
                            exit()
                        except UnicodeDecodeError as e:
                            logging.error(f'Failed to read file "{file}": {e}')
                        except Exception as e:
                            logging.error(f'Unexpected exception on file "{file}": {e}. Please use `--debug` to process the same data again and copy the input and errors, report to https://github.com/20x48/RAINLotus/issues')
                        else:
                            logging.info(f'[√] {file} -> {ww}')
                            succeeded += 1
                else:
                    logging.debug(f'[-] {file}')
        print(f'### Done: {succeeded} / {total} file(s) succeeded ###')

if __name__ == "__main__":
    cli()