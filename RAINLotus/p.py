"""
Uses to parse RAINLotus markup language to BASIC OBJECT
=======================================================
[
    The first value of Array
    ============================
    {   "title": TITLE,
        "config": *{MODULE: *[COMMAND, KWARGS, LINES]},
        "headers": *[HEADER-LEVEL, HEADER],
        "imports": *{MODULE: ALIAS}
    }
    ----------------------------
    KEY, MODULE, COMMAND, ALIAS = IDENTIFIER
    VALUE, LINE, TITLE, HEADER = STRING
    KWARGS = *{KEY, VALUE}
    LINES = *[LINE]
    HEADER-LEVEL = (2-6)

    The aftering values of Array
    ============================
    [   TYPE,
        METHOD ?,
        KWARGS ? TYPE in (3-5),
        CONTENT
    ]
    ----------------------------
    TYPE = (0-5)
    ; 0 - plaintext
    ; 1 - texts include plaintext and inline
    ; 2 - built-in inline
    ; 3 - built-in block
    ; 4 - external inline
    ; 5 - external block
    METHOD = [MODULE, METHOD_] ? TYPE in (4-5)
    METHOD = METHOD_ ? TYPE in (2-3)
    METHOD_, MODULE, KEY = IDENTIFIER
    VALUE = STRING
    KWARGS = *{KEY: VALUE} | NONE
    CONTENT = [...]
]

Attach: Structure of config
============================================
*{MODULE: *[COMMAND, CONTENT]}
--------------------------------------------
MODULE, COMMAND = IDENTIFIER
CONTENT         = *[STRING]

Attach: CONTENT's format of block_*list
============================================
*[LABEL ? METHOD in ("tli", "dli"), CONTENT]
--------------------------------------------
CONTENT = [...]
LABEL   = STRING

Attach: CONTENT's format of block_dialog
============================================
*[TYPE, CONTENT, KWARGS, NAME ? TYPE == 2]
--------------------------------------------
TYPE                = (0-3)
CONTENT             = [...]
KWARGS              = *{KEY: VALUE}
NAME, KEY, VALUE    = STRING
"""
import csv
import json
from re import compile, IGNORECASE
from sys import exc_info
from typing import Any, Dict, Tuple, Union, Iterable, Callable
from warnings import warn
from itertools import repeat, chain, compress, islice
from collections import defaultdict

_idex = r'(?:([\w\-]+)\.)?([\w\-]+)'
_argx = r'(?: +[\w\-]+(?: *= *(?:".*?(?:"".*?)*?"|\S+))?)* *'
_sufx = r'(?:\? +(.+))?'
RE_IDEX = compile(_idex)                                                                # e.g. `extmod.mymark`
RE_ARGX = compile(_argx)                                                                # e.g. `arg1 arg2="the identifier ""20x48"" is me."   `
RE_ARGS = compile(r'([\w\-]+)(?: *= *(?:"(.*?(?:"".*?)*?)"|(\S+)))?')                   # (Uses to fetch all args in ARGX)
RE_SUFX = compile(_sufx)                                                                # e.g. `? [write freely after the question mark]`
RE_SECT = compile(r'([\w\-]+)(?: +(.+))?')                                              # e.g. `aliases: [write freely after the colon sign]`
RE_ALIAS = compile(r'([\w\-]+)(?: *-> *([\w\-]+))?')                                    # e.g. `LayoutLotus -> ui`
RE_TABLE = compile(r'(?: +(quick|csv|json))?(?: +(\d+))?(?: +(rotate))?', IGNORECASE)   # e.g. `JSON 2 ROTATE`
RE_DIALOG = compile(r'(?:(<[\-~$?!])|([\-~$]>)(?:@(.*?(?:@@.*?)*)@)?|(<>))(?: +(.+))?') # = # (Some Example) My speaks: `<- Hello world!`
_hex       = r'[\dA-F]'                                                                     # Your speaks without name: `-> Hi, 20x48~`
_sub_delims = r"[!$?'()*+,;=]"                                                              #    Your speaks with name: `->@ Axx @ That comes me on.`
_unreserved  = r'[\w\-\.~]'                                                                 #              System hint: `<> Someone has been banned for 5 minute(s).`
_pct_encoded  = f'%{_hex}{{2}}'
_char1        = f'(?::|{_sub_delims}|{_unreserved}|{_pct_encoded})'                         # Nearby Regexes refer to RFC 3986
_char2        = f'(?:@|{_char1})'
_char3        = f'(?:{_char2}|[/?])'
_dec_octec    = r'(?:[0-1]?\d{1,2}|2[0-4]\d|25[0-5])'
_dec_65535    = r'(?:[0-5]?\d{1,4}|6[0-4]\d{3}|65[0-4]\d{2}|655[0-2]\d|6553[0-5])'
DomainName    = r'(?:(?!-)[A-Z0-9\-]{0,62}[A-Z0-9]\.)+(?:[A-Z]{2,13}|(?:biz|com?|firm|gen|idv|ind|info|me|net?|nom?|org|re|web)\.[A-Z]{2})'
IPv4address   =rf'(?:{_dec_octec}\.){{3}}{_dec_octec}'                                  # These are all I can find on Godaddy.
_h16          = f'{_hex}{{1,4}}'
_ls32         = f'(?:{_h16}:{_h16}|{IPv4address})'
IPvFuture     =rf'[v]{_hex}+\.(?:{_sub_delims}|{_unreserved}|:)+'
IPv6address   =(f'(?:{_h16}:){{6}}{_ls32}'
                 f'|::(?:{_h16}:){{5}}{_ls32}'
                  f'|(?:{_h16})?::(?:{_h16}:){{4}}{_ls32}'
                   f'|(?:(?:{_h16}:){{0,1}}{_h16})?::(?:{_h16}:){{3}}{_ls32}'
                    f'|(?:(?:{_h16}:){{0,2}}{_h16})?::(?:{_h16}:){{2}}{_ls32}'
                     f'|(?:(?:{_h16}:){{0,3}}{_h16})?::(?:{_h16}:){{1}}{_ls32}'
                      f'|(?:(?:{_h16}:){{0,4}}{_h16})?::{_ls32}'
                       f'|(?:(?:{_h16}:){{0,5}}{_h16})?::{_h16}'
                        f'|(?:(?:{_h16}:){{0,6}}{_h16})?::')
RE_QUICK_HEAD = compile(r'(={2,6}) +(.+?)')                                                 # e.g. `== header 2`
RE_QUICK_LIST = compile(r'(?:(\.)|(\d+|\?)|([~x\-:+v*]))\.(?: +(.+))?')                     # e.g. `1. item one`
RE_QUICK_ALLS = compile(r'([!"#$&*/:;>@`|~])\1{2}(?: +(.+))?')                              # e.g. `/// content`
RE_ANYTH_INGS = compile(r'('                                                                # AutoURL           | 0
                            r'(?:file|https?|irc[6s]?|ldaps?|rsync|s?ftp)://'               # Scheme://
                            r'(?:'                                                              # Authority
                                f'(?:{_char1}*@)?'                                                  # [Userinfo@]
                               rf'(?:{DomainName}|{IPv4address}|\[(?:{IPv6address}|{IPvFuture})\])' # Host
                                f'(?::{_dec_65535})?)'                                              # [:Port]
                            f'(?:/{_char2}*)*'                                                  # Path
                           rf'(?:\?{_char3}*)?'                                                 # [?Query]
                            f'(?:#{_char3}*)?)'                                                 # [#Fragment]
                        r'|([*+\-/=\\^_~])\2(?=\S)(.*?\S)\2{2}'                             # "Hang Bue Lang"   | 1  2
                        r'|=([A-Z])(\d+)='                                                  # Shield            | 3  4
                        r'|/\*(?=\S)(.*?\S)\*/'                                             # Bitalic           | 5
                        r'|`(?=\S)(.*?\S)`'                                                 # Code              | 6
                        r'|\$\$(.+?)\$\$'                                                   # Formula           | 7
                        r'|\{(\S+?)\}'                                                      # Reuse             | 8
                       fr'|<<{_idex}({_argx}){_sufx}>>'                                     # General           | 9  10 11 12   e.g. `<<ui.test args ? text>>`
                        r'|(?:\[(?:(\\)?([!#]))?(?=\S)(.*?\S)\]<|<)(\S+?)>'                 # Link              | 13 14 15 16
                        r'|\[(#|\^)(?=\S)(.*?\S)\]'                                         # Refer             | 17 18
                       fr'|([\w\-\.+]+)@({DomainName})',                                    # AutoEmail         | 19 20
                        IGNORECASE)

DEFAULT_TITLE = 'RAINLotus'

ALLOWED_ARGS_NOTE = {       #                            / `help`和`note`的区别：前者是“如果你无法……(could't)”；后者是“如果你想……(want)”。
    'caution', 'warning',   # 安全示警（-> 危险程度）   / 前者帮助你完成最基本的任务，而后者则帮助你锦上添花。
    'tip', 'help', 'note',  # 客观提示（-> ？？程度） </ `tip`则相当于窍门(trick and knack)。
    'idea', 'inspiration',  # 主观想法（-> 实质程度） <- 天马行空就可以用`idea`了（想法的原型）；有点什么实质性的东西再用`inspiration`吧。
    'info', 'important',    # 客观描述（-> 重要程度） <- 区别在于：“知不知道有没有关系？”或是“在不知道的情况下是不是可能会造成不那么好的影响？”
    'good', 'deprecated'    # 客观现状
}
ALLOWED_ARGS_DIALOG = {'title', 'style', 'use-default-name'}    # 批注：默认名称是对于多人聊天使用的。“自动升级”
ALLOWED_ARGS_CONFIG = set.union(
    set(),  # what the hell? why it won't works without a set as the first positional argument?
    (f'toc-{x}' for x in ('level',)),
    (f'html-{x}' for x in ('lang', 'dir')),
    (f'meta-{x}' for x in ('description', 'keywords', 'author')),
    (f'dialog-{x}' for x in ('default-style', 'default-name')),
    (f'http-equiv-{x}' for x in ('refresh', 'content-security-policy', 'content-security-policy-report-only'))
)
ALLOWED_ARGS_CONFIG_ALIASES = {'alias', 'alias-code', 'alias-raw'}

T_FILTER = Callable[[str], bool]

def ARGX2ARGS(Qargx: str, Filter: T_FILTER=lambda x: True) -> Dict[str, Union[bool, str]]:
    return {k: (v.replace('""', '"') if v else y or True) for k, v, y in RE_ARGS.findall(Qargx) if Filter(k)}


class Parser:
    def __init__(self, ext_modules: Dict[str, Tuple[Tuple[T_FILTER, T_FILTER], Tuple[T_FILTER, T_FILTER], Callable[[Dict[str, Tuple[str]]], Any]]]=None):
        """
        方法过滤[block, inline], 递归模式[block, inline], 配置整合
        """
        self.ext_modules = ext_modules or {}

    def __rrshift__(self, text: Union[str, Iterable[str]]) -> list:
        self.headers = []
        self.config = defaultdict(list)
        self.imports = {}
        self.imported = {'RAINLotus'}
        self.lines = text.splitlines() if isinstance(text, str) else text
        self.lines_length = len(self.lines)

        try:
            title, qwq = self.lines[:2]
        except ValueError:
            title = DEFAULT_TITLE
            title_offset = 0
        else:
            if (not title or title.isspace()) or (not qwq or qwq.count('=') != len(qwq.rstrip())):
                title = DEFAULT_TITLE
                title_offset = 0
            else:
                title_offset = 2

        result = self._love_you_forever(title_offset)
        config = self._config_integrate()

        return [{'title': title.strip(),
                 'config': config,
                 'headers': self.headers,
                 'imports': self.imported - {'RAINLotus'}}] + result

    def _love_you_forever(self, start=0, status=1, indent=0) -> Union[int, Tuple[int, list], list]:
        jump = 0
        index = start   # 为什么需要这行语句呢？因为程序可能他妈根本就不经过下面这个for循环！
        result = []
        if status == 2:         # 对于内部不解析的块，尤其是`block:code`，需要记录它们的空白行；
            more = 0

        for index, line in enumerate(self.lines[start:], start):
            # 掠过行
            if jump:
                jump -= 1
                continue    # 忽略已经被解析过的行。
            line = line.rstrip()
            if not line:
                if status == 2:
                    more += 1   # 记录内部不解析的块的空白行。
                continue    # 忽略空白行
            # 探寻缩进等级
            pos = 0         # 当前缩进空格数
            back = False    # 标记：是否要打回去（往回缩进）
            while pos < len(line) and line[pos] == ' ':
                pos += 1
            if status == 2:         # 对于内部不解析的块：
                pos_ = indent * 4
                if pos < pos_:      # 如果实际缩进小于目标缩进，那么打回去；
                    back = True
                else:               # 否则，超过目标缩进的空格原样保留。
                    pos = pos_
            else:
                div, mod = divmod(pos, 4)
                if div < indent:                # 实际缩进小于目标缩进，打回去；
                    back = True
                elif mod != 0 or div > indent:  # 实际缩进大于目标缩进，*忽略该行*。
                    continue
            # 错误缩进的处理
            if back:
                index -= 1
                if status == 0:
                    return index            # 注释不需要CONTENT（RESULT），
                else:
                    return index, result    # 其它则都需要。
            # ０: 注释
            if status == 0:
                continue    # 直接忽略注释。
            # 以下是非注释
            if pos:
                line = line[pos:]
            prefix = line[0]        # 获取行首字符，优化运算。
            # １: 常规
            if status == 1:
                # List
                if prefix in '.0123456789?~x-:+v*':
                    Axx = RE_QUICK_LIST.fullmatch(line)
                    if Axx:
                        if Axx.group(1):
                            Qtype, Qstatus = 'u', 3
                        elif Axx.group(2):
                            Qtype, Qstatus = 'o', 4
                        elif Axx.group(3):
                            Qtype, Qstatus = 't', 5
                        Qindex, Qcontent = index, []
                        while Qindex < self.lines_length:
                            Qindex, Qresult = self._love_you_forever(Qindex, Qstatus, indent)
                            if Qresult:
                                Qcontent.append(Qresult)
                            else:
                                break
                        result.append([3, 'lst', {'typ': Qtype, 'sta': 1 if prefix == '?' else int(Axx.group(2))} if Qtype == 'o' else {'typ': Qtype}, Qcontent])
                        jump = Qindex - index
                        continue
                # Header
                if prefix == '=':
                    Axx = RE_QUICK_HEAD.fullmatch(line)
                    if Axx:
                        Qtype, Qheader = Axx.groups()
                        Qtype = len(Qtype)
                        # 其正确长度由正则表达式保护
                        result.append([3, 'had', {'lev': Qtype}, Qheader])
                        # 非顶层header不加入headers
                        if not indent:
                            self.headers.append((Qtype, Qheader))
                        continue
                # Separator & page break
                elif prefix in "%-" and 3 <= len(line) == line.count(prefix):
                    # % 100101
                    # - 101101
                    result.append([3, ['pgb', 'sep'][(ord(prefix)>>3)&1], None, None])
                    continue
                # Anything
                else:
                    Axx = RE_QUICK_ALLS.fullmatch(line)
                    if Axx:
                        Quick = Axx.group(2)
                        # Config
                        if prefix == '&' and indent == 0 and Quick:
                            Axx = RE_ALIAS.fullmatch(Quick)
                            if Axx:
                                Qmodule, Qalias = Axx.groups()
                                if Qmodule in self.ext_modules or Qmodule == 'RAINLotus':
                                    if Qmodule != 'RAINLotus':
                                        if Qalias and (Qmodule not in self.imports):
                                            # 如果一个模块设置了多个别名，那么应该只使用第一次设置的那个。
                                            self.imports[Qalias] = Qmodule
                                        self.imported.add(Qmodule)
                                    Qindex, Qresult = self._love_you_forever(index+1, 7, indent+1)
                                    self.config[Qmodule].extend(Qresult)
                                    jump = Qindex - index
                        # General
                        elif prefix == '/' and Quick:
                            Qidex = RE_IDEX.match(Quick)
                            if Qidex:
                                Qalias, Qmethod = Qidex.groups()
                                if Qalias:
                                    # 过滤掉所有未导入的模块
                                    if Qalias in self.imports:
                                        Qmodule = self.imports[Qalias]
                                    elif Qalias in self.imported:
                                        Qmodule = Qalias
                                    else:
                                        continue
                                    try:
                                        if not self.ext_modules[Qmodule][0][0](Qmethod):
                                            continue
                                    except Exception:
                                        continue
                                    try:
                                        Qstatus = 1 if self.ext_modules[Qmodule][1][0](Qmethod) else 2
                                    except Exception:
                                        Qstatus = 2
                                elif Qmethod in {'image', 'audio', 'video'}:
                                    Qmodule = None
                                    Qstatus = 1
                                else:
                                    continue
                                Qargx = RE_ARGX.match(Quick, Qidex.end())
                                if Qmodule:
                                    Qargs = ARGX2ARGS(Qargx.group(0))
                                else:
                                    Qargs = ARGX2ARGS(Qargx.group(0), {
                                        'image': lambda x: x in {'src', 'alt'},
                                        'audio': lambda x: x in {'src', 'autoplay', 'loop', 'muted', 'preload'},
                                        'video': lambda x: x in {'src', 'autoplay', 'loop', 'muted', 'preload'}
                                    }[Qmethod])
                                Qsufx = RE_SUFX.fullmatch(Quick, Qargx.end())
                                Qtext = Qsufx.group(1) if Qsufx else None
                                Qindex, Qresult = self._love_you_forever(index+1, Qstatus, indent+1)
                                if Qalias:
                                    result.append([5, (Qmodule, Qmethod), Qargs, self._combin(Qtext, Qresult, Qstatus==2)])
                                else:
                                    result.append([3, {
                                        'image': 'img',
                                        'audio': 'aud',
                                        'video': 'vid'
                                    }[Qmethod], Qargs, self._combin(Qtext, Qresult)])
                                jump = Qindex - index
                        # Note
                        elif prefix == '*' and Quick:
                            Quick = Quick.lower()
                            if Quick in ALLOWED_ARGS_NOTE:
                                Qindex, Qresult = self._love_you_forever(index+1, 1, indent+1)
                                result.append([3, 'not', {'typ': Quick}, Qresult])
                                jump = Qindex - index
                        # Quote
                        elif prefix == '"':
                            Qindex, Qresult = self._love_you_forever(index+1, 1, indent+1)
                            if Quick and Quick[:2] in {'--', '——'}:
                                result.append([3, 'quo', {'aut': self._mesilf(Quick[2:].strip(), True)}, Qresult])
                            else:
                                result.append([3, 'quo', {'aut': None}, self._combin(Quick, Qresult)])
                            jump = Qindex - index
                        # Definition-list
                        elif prefix == ':' and Quick:
                            Qindex, Qcontent = index, []
                            while Qindex < self.lines_length:
                                Qindex, Qresult = self._love_you_forever(Qindex, 6, indent)
                                if Qresult:
                                    Qcontent.append(Qresult)
                                else:
                                    break
                            result.append([3, 'lst', {'typ': 'd'}, Qcontent])
                            jump = Qindex - index
                        # Table
                        elif prefix == '|':
                            Qmode, Qheight, Qrotate = RE_TABLE.fullmatch(f' {Quick}').groups() if Quick else (None, None, None)
                            # Qmode: 表格模式
                            # Qheight: 表格头部高度
                            # Qrotate: 是否旋转表格
                            Qindex, Qtable = self._love_you_forever(index+1, 2, indent+1)
                            Qtable = filter(bool, Qtable)
                            ### 解析表格 ###
                            mod = Qmode.lower() if Qmode else 'quick'
                            hei = int(Qheight) if Qheight else 1
                            fai = False
                            # 统一数据格式
                            if mod == 'quick':
                                fresh = map(lambda x: x[1:], csv.reader(
                                    Qtable,
                                    delimiter='|',
                                    escapechar='\\',
                                    quoting=csv.QUOTE_NONE
                                ))
                            elif mod == 'csv':
                                fresh = csv.reader(Qtable)
                            else:
                                try:
                                    fresh = json.loads(
                                        ''.join(Qtable),
                                        parse_int=str,
                                        parse_float=str,
                                        parse_constant=str
                                    )
                                except json.JSONDecodeError:
                                    fai = True
                                if isinstance(fresh, dict):
                                    try:
                                        head, align, body = fresh['head'], fresh['align'], fresh['body']
                                    except KeyError:
                                        fai = True
                                    else:
                                        if any(map(
                                            lambda x: not isinstance(x, list) or any(map(
                                                lambda y: any(map(
                                                    lambda z: not isinstance(z, str),
                                                    y)),
                                                x)),
                                            (head, [align], body)
                                        )):
                                            fai = True
                                        else:
                                            hei = len(head)
                                            fresh = []
                                            fresh.extend(head)
                                            fresh.append(align)
                                            fresh.extend(body)
                                elif isinstance(fresh, list):
                                    if any(map(
                                        lambda x: not isinstance(x, list) or any(map(
                                            lambda y: any(map(
                                                lambda z: not isinstance(z, str),
                                                y)),
                                            x)),
                                        fresh
                                    )):
                                        fai = True
                                else:
                                    fai = True
                            if fai:
                                jump = Qindex - index
                                continue
                            if mod != 'json':
                                fresh = tuple(map(lambda x: tuple(map(lambda y: y.strip(), x)), fresh))
                            # 查找表格宽度及安全性保护及对齐控制文本
                            wid = 0
                            ava = []
                            ali = []
                            for i, row in enumerate(fresh):
                                # 对齐控制行
                                if i == hei:
                                    ava.append(False)
                                    if not row: # for json
                                        ali = repeat('=')
                                        continue
                                    for j, sign in enumerate(row, 1):
                                        if sign in {'<', '=', '>'}:
                                            ali.append(sign)
                                            if j == len(row):
                                                if 0 < wid != len(row):
                                                    fai = True
                                                    break
                                                else:
                                                    wid = len(row)
                                        elif j == len(row):
                                            if sign in {'<<<', '===', '>>>'}:
                                                ali = chain(ali, repeat(sign[0]))
                                            elif not sign: # for quick
                                                ali = repeat('=')
                                            else:
                                                fai = True
                                                break
                                        else:
                                            fai = True
                                            break
                                    if fai:
                                        break
                                    continue
                                # 空行
                                if not row:
                                    ava.append(False)
                                    continue
                                # 常规行
                                if row[-1] in {'<<<', '===', '>>>'}:
                                    ava.append(len(row) != 1)
                                else:
                                    ava.append(True)
                                    if 0 < wid != len(row):
                                        fai = True
                                        break
                                    else:
                                        wid = len(row)
                            if fai or not ali or wid == 0:
                                jump = Qindex - index
                                continue
                            # 逐单元格计算
                            table = []
                            for row in compress(fresh, ava):
                                span = 1
                                cache = None
                                rowing = []
                                for i, cell in enumerate(row, 1):
                                    if cell in {'>', '>>>'}:
                                        if not cache:
                                            fai = True
                                            break
                                        elif cell == '>':
                                            span += 1
                                            continue
                                        elif i == len(row):
                                            span += wid - i + 1
                                            break
                                    if cache:
                                        rowing.append([span, cache])
                                        cache = self._mesilf(cell, True)
                                        span = 1
                                    else:
                                        cache = self._mesilf(cell, True)
                                if fai:
                                    break
                                if cache:
                                    rowing.append([span, cache])
                                table.append(rowing)
                            if fai:
                                jump = Qindex - index
                                continue
                            ### 这才是最终要传递的 ###
                            result.append([
                                3, 'tab', {
                                    'hei': hei,
                                    'rot': bool(Qrotate),
                                    'ali': list(islice(ali, wid))
                                }, table
                            ])
                            jump = Qindex - index
                        # Collapse
                        elif prefix == '~':
                            if Quick:
                                try:
                                    Qopen, Qsummary = Quick.split(' ', 1)
                                    if Qopen.lower() != 'open':
                                        Qopen, Qsummary = False, self._mesilf(Quick, True)
                                    else:
                                        Qopen, Qsummary = True, self._mesilf(Qsummary, True)
                                except ValueError:
                                    if Quick.lower() == 'open':
                                        Qopen, Qsummary = True, None
                                    else:
                                        Qopen, Qsummary = False, self._mesilf(Quick, True)
                            else:
                                Qopen, Qsummary = False, None
                            # Qopen: 是否默认展开
                            # Qsummary: 摘要
                            Qindex, Qresult = self._love_you_forever(index+1, 1, indent+1)
                            result.append([3, 'col', {'opn': Qopen, 'sum': Qsummary}, Qresult])
                            jump = Qindex - index
                        # Dialog
                        elif prefix == '@':
                            Qargx = RE_ARGX.fullmatch(f' {Quick}')
                            if Qargx:
                                Qargs = ARGX2ARGS(Qargx.group(0), lambda x: x in ALLOWED_ARGS_DIALOG)
                            else:
                                Qargs = {}
                            Qindex, Qresult = self._love_you_forever(index+1, 10, indent+1)
                            result.append([3, 'dia', Qargs, Qresult])
                            jump = Qindex - index
                        # Footnote
                        elif prefix == '>' and Quick:
                            Qindex, Qresult = self._love_you_forever(index+1, 1, indent+1)
                            result.append([3, 'fnt', {'fnt': Quick}, Qresult])
                            jump = Qindex - index
                        # Code
                        elif prefix == '`':
                            Qindex, Qresult = self._love_you_forever(index+1, 2, indent+1)
                            result.append([3, 'cod', {'lan': Quick.lower() if Quick else 'plaintext'}, Qresult])
                            jump = Qindex - index
                        # Raw & Diagram & Formula
                        elif prefix in '!#$':
                            # ! 100001
                            # # 100011
                            # $ 100100
                            prefix = ord(prefix) >> 1 & 3
                            Qindex, Qresult = self._love_you_forever(index+1, 2, indent+1)
                            result.append([3, ['raw', 'dgr', 'fml'][prefix], None, [Quick]+Qresult if Quick else Qresult])
                            jump = Qindex - index
                        # Comment
                        elif prefix == ';':
                            Qindex = self._love_you_forever(index+1, 0, indent+1)
                            jump = Qindex - index
                        continue
            # ３４５: 无序/有序/Todos 列表
            elif 3 <= status <= 5:
                Axx = RE_QUICK_LIST.fullmatch(line)
                if Axx:
                    *ovo, text = Axx.groups()
                    Qstatus = tuple(map(bool, ovo)).index(True) + 3
                    if status == Qstatus:
                        Qindex, Qresult = self._love_you_forever(index+1, 1, indent+1)
                        Qcontent = self._combin(text, Qresult)
                        return Qindex+1, (Qcontent if status != 5 else [Axx.group(3), Qcontent])
                return index-1, None
            # ６: 定义列表
            elif status == 6:
                if prefix == ':':
                    Axx = RE_QUICK_ALLS.fullmatch(line)
                    if Axx:
                        Qdefinition = Axx.group(2)  # 列表项标号后的文本
                        if Qdefinition:
                            Qindex, Qresult = self._love_you_forever(index+1, 1, indent+1)
                            return Qindex+1, [self._mesilf(Qdefinition, True), Qresult]
                return index-1, None
            # ７: 配置解析
            elif status == 7:
                Axx = RE_SECT.fullmatch(line)
                if Axx:
                    Qcommand, Qtext = Axx.groups()
                    Qindex, Qresult = self._love_you_forever(index+1, 2, indent+1)
                    result.append([Qcommand, self._combin(Qtext, Qresult, True)])
                    jump = Qindex - index
                continue
            # 10: Dialog
            elif status == 10:
                # 0: 自己的话
                # 1: 对方的话
                # 2: 对方的话 - 指定名字
                # 3: 系统提示
                # 批注：但实际上渲染出来，2和1是会合并的。
                Axx = RE_DIALOG.fullmatch(line)
                if Axx:
                    Qme, Qyou, Qname, Qsys, Qmessage = Axx.groups()
                    if Qme:
                        Qtype = 0
                        Qfeat = Qme[1]
                    elif Qyou:
                        Qname = Qname and Qname.strip().replace('@@', '@')
                        Qtype = bool(Qname) + 1
                        Qfeat = Qyou[0]
                    elif Qsys:
                        Qtype = 3
                        Qfeat = None
                    else:
                        continue
                    Qargs = {}
                    if Qtype < 3 and Qfeat != '-':
                        # $!~?
                        Qargs['typ'] = ('hongbao',
                                        'failed',
                                        'voice',
                                        'sending')[ord(Qfeat)&3]
                        if Qfeat in {'~', '$'}:
                            try:
                                Qvalue = int(Qmessage) if Qfeat == '~' else int(float(Qmessage) * 100)
                            except (TypeError, ValueError):
                                continue
                            else:
                                if (Qtype == '~' and not 2 <= Qvalue <= 60) \
                                or (Qtype == '$' and not 0 <= Qvalue): continue
                                Qargs['val'] = Qvalue
                    Qindex, Qresult = self._love_you_forever(index+1, 1, indent+1)
                    if Qfeat not in {'~', '$'}:
                        Qresult = self._combin(Qmessage, Qresult)
                        if not Qresult:
                            continue
                    result.append([Qtype, Qresult, Qargs] + ([Qname] if Qname else []))
                    jump = Qindex - index
                continue
            # ２: 不解析
            if status == 2:
                result.extend(repeat('', more))
                result.append(line)
                more = 0
            # ？: 没有什么特色块
            else:
                result.append(self._mesilf(line))
        if status == 0:
            return index            # *注释状态*调用，只需返回新索引
        elif indent == 0:
            return result           # 表明这是顶层调用，返回结果
        else:
            return index, result    # 表明这是内部调用，返回结果和新索引

    def _combin(self, text: str, result: list, keep: bool=False) -> list:
        if text:
            qwq = text if keep else self._mesilf(text)
            return [qwq] + result
        return result

    def _mesilf(self, text: str, inner: bool=False) -> list:
        last = 0
        result = []
        anything = RE_ANYTH_INGS.search(text)
        if not anything:
            return ((0, text),) if inner else (0, text)
        while anything:
            frag = text[last:anything.start()]
            if frag:
                result.append((0, frag))
            ant = anything.groups()
            if ant[0]:      # AutoURL
                result.append((2, 'lnk', ('lnk', ((0, ant[0]),), ant[0])))
            elif ant[1]:
                result.append((2, {'*': 'bld', '+': 'mak', '-': 'dim',
                                   '/': 'ita', '=': 'sha', '^': 'sup',
                                   '_': 'sub', '~': 'del', '\\':'sla'}[ant[1]], self._mesilf(ant[2], True)))
            elif ant[3]:    # HangBueLang
                result.append((2, 'shl', (ant[3].lower(), int(ant[4]))))
            elif ant[5]:    # Shield
                result.append((2, 'bit', ((0, ant[5]),)))
            elif ant[6]:    # Code
                result.append((2, 'cod', ant[6]))
            elif ant[7]:    # Formula
                result.append((2, 'fml', ant[7].strip()))
            elif ant[8]:    # Reuse
                result.append((2, 'reu', ant[8]))
            elif ant[10]:   # General
                Qalias = ant[9]
                if Qalias:
                    Qmodule = None
                    if Qalias in self.imports:
                        Qmodule = self.imports[Qalias]
                    elif Qalias in self.imported:
                        Qmodule = Qalias
                    if Qmodule:
                        try:
                            if not self.ext_modules[Qmodule][0][1](ant[10]):
                                raise NotImplementedError
                        except Exception:
                            ...
                        else:
                            Qargs = ARGX2ARGS(ant[11])
                            try:
                                mod = bool(self.ext_modules[Qmodule][1][1](ant[10]))
                            except Exception:
                                mod = False
                            result.append((4, (Qmodule, ant[10]), Qargs, self._mesilf(ant[12], True) if mod else ant[12]))
            elif ant[16]:   # Link
                tyq = ant[13]
                typ = ant[14]
                tit = ant[15]
                lnk = ant[16]
                if not typ or tyq:
                    tit = (tyq if tyq and not typ else '') + (typ if tyq else '') + (tit or '')
                    typ = '.'
                if not (typ == '#' and not tit):
                    result.append((2, 'lnk', ({'!': 'img',
                                               '#': 'cro',
                                               '.': 'lnk'}[typ], (self._mesilf(tit, True) if tit else ((0, lnk),)) if typ == '.' else (tit or lnk), lnk)))
            elif ant[17]:   # Refer
                result.append((2, 'ref', ({'^': 'fnt', '#': 'inr'}[ant[17]], ant[18])))
            elif ant[19]:   # AutoEmail
                result.append((2, 'mal', (ant[19], ant[20])))
            else:
                # 也许应该发出一条警告？
                typ, val, _ = exc_info()
                warn(f'mismatched inline "{text}": {typ.__name__}: {val}', RuntimeWarning)
            last = anything.end()
            anything = RE_ANYTH_INGS.search(text, last)
        frag = text[last:]
        if frag:
            result.append((0, frag))
        return tuple(result) if inner else [1, result]

    def _config_integrate(self) -> dict:
        classify = defaultdict(lambda:defaultdict(list))
        for module, commands in self.config.items():
            for command, content in commands:
                classify[module][command].extend(content)
        config = {}
        for module, commands in classify.items():
            if module != 'RAINLotus':
                try:
                    config[module] = self.ext_modules[module][2](commands)
                except Exception:
                    config[module] = commands
                continue
            RAINLotus = {}
            aliases = defaultdict(dict)
            alias_existed = set()
            for command, content in commands.items():
                if command in ALLOWED_ARGS_CONFIG_ALIASES:
                    for alias in content:
                        try:
                            left, right = alias.split(maxsplit=1)
                        except ValueError:
                            ...
                        else:
                            if left not in alias_existed:
                                alias_existed.add(left)
                                if command == 'alias':
                                    aliases[command][left] = self._mesilf(right, True)
                                else:
                                    aliases[command][left] = right
                elif command in ALLOWED_ARGS_CONFIG:
                    RAINLotus[command] = ''.join(content)
            RAINLotus.update(aliases)
            config['RAINLotus'] = RAINLotus
        return config