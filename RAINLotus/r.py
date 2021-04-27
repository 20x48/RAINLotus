"""
Uses to simply render BASIC OBJECT into HTML.
"""
try:
    from .v import __version__
except ImportError:
    from v import __version__

from sys import exc_info
from typing import Any, Dict, Tuple, Union, Callable, Iterable
from base64 import urlsafe_b64encode
from hashlib import shake_128
from pathlib import Path
from warnings import warn
from functools import lru_cache


ABSOLUTE = Path(__file__).parent
MINIMIZE = lambda x: ''.join(x.split()).replace('`', ' ')
LAZY_LOAD_FLAG = False

TEMPLATE = MINIMIZE(f'''
    <!DOCTYPE`html>
    {{html}}
        <head>
            <meta`charset="utf-8"`/>
            <meta`name="generator"`content="RAINLotus`{__version__}"`/>
            <meta`name="viewport"`content="width=device-width,initial-scale=.85,user-scalable=no"`/>
            {{meta}}
            {{equiv}}
            <title>{{title}}</title>
            {{css}}
        </head>
        <body>
            <header><h1>{{h1}}</h1></header>
            <aside>{{toc}}</aside>
            <main>{{content}}</main>
            <script`src="https://cdn.jsdelivr.net/npm/prismjs@1.23.0/components/prism-core.min.js"></script>
            <script`src="https://cdn.jsdelivr.net/npm/prismjs@1.23.0/plugins/autoloader/prism-autoloader.min.js"></script>
            <script`src="https://cdn.jsdelivr.net/npm/prismjs@1.23.0/plugins/autolinker/prism-autolinker.min.js"></script>
            <script`src="https://cdn.jsdelivr.net/npm/prismjs@1.23.0/plugins/inline-color/prism-inline-color.min.js"></script>
            <script`src="https://cdn.jsdelivr.net/npm/prismjs@1.23.0/plugins/toolbar/prism-toolbar.min.js"></script>
            <script`src="https://cdn.jsdelivr.net/npm/prismjs@1.23.0/plugins/show-language/prism-show-language.min.js"></script>
            <script`src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
            <script>;mermaid.init(undefined, '.yhb-dgr');</script>
            <script>
                ;MathJax = {{{{
                    tex: {{{{
                        inlineMath: [['$$', '$$']],
                        displayMath: [['$', '$']]}}}},
                        options: {{{{
                            ignoreHtmlClass: '.*',
                            processHtmlClass: 'yh[bi]-fml',
                            enableMenu: false
                        }}}}
                    }}}};;
            </script>
            <script`src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-svg.js"></script>
        </body>
    </html>
''')

CSS_HIGHLIGHT = None
CSS_RAINLOTUS = None

def lazy_load_assets():
    global LAZY_LOAD_FLAG
    if LAZY_LOAD_FLAG:
        return
    LAZY_LOAD_FLAG = True
    global CSS_HIGHLIGHT, CSS_RAINLOTUS
    # PrismJS 1.23.0 Tomorrow Night Theme
    with open(ABSOLUTE / 'prism.min.css', encoding='utf-8') as f:
        CSS_HIGHLIGHT = f.read()
    # Hey!
    with open(ABSOLUTE / 'rainink.min.css', encoding='utf-8') as f:
        CSS_RAINLOTUS = f.read()

DIALOG_STYLE = {'wechat', 'qq', 'default'}

T_RENDERER = Callable[[Any, dict, list], str]


class Template:
    def __init__(self, custom_title: Callable[[str], str]=str, custom_css: str=None):
        self.custom_css = custom_css
        self.custom_title = custom_title

    def __rrshift__(self, data: dict) -> str:
        lazy_load_assets()
        return TEMPLATE.format(
            html=data['html'],
            meta=data['meta'],
            equiv=data['equiv'],
            title=self.custom_title(data['title']),
            css=f'<style>{CSS_RAINLOTUS}{CSS_HIGHLIGHT}</style>' if self.custom_css is None else self.custom_css,
            h1=data['title'],
            toc=data['toc'],
            content=data['content']
        )


class Renderer:
    def __init__(self, ext_renderers: Dict[str, Tuple[T_RENDERER, T_RENDERER]]=None):
        self._core = RendererCore(ext_renderers)

    def __rrshift__(self, data: list) -> Dict[str, Union[str, bool]]:
        shared = data[0]
        # 核心内容
        content = data >> self._core
        # HTML TAG
        html_lang = shared.get('html-lang')
        html_dir = shared.get('html-dir')
        html = f'''<html{
            f' lang="{self._core.escape(html_lang)}"' if html_lang else ''
        }{
            f' dir="{html_dir}"' if html_dir in {'ltr', 'rtl', 'auto'} else ''
        }>'''
        # TOC
        toc_level = shared.get('toc-level')
        if not isinstance(toc_level, int) or not 1 <= toc_level <= 6:
            toc_level = 3
        toc = ''.join(
            f'''<p class="_{
                lev
            }"><a href="#s:{
                self._core.calcid(had)
            }">{
                self._core.escape(had)
            }</a></p>'''
            for lev, had in shared['headers']
            if lev <= toc_level
        )
        # META
        meta_description = shared.get('meta-description')
        meta_keywords = shared.get('meta-keywords')
        meta_author = shared.get('meta-author')
        meta = (
            f'<meta name="description" content="{self._core.escape(meta_description)}">' if meta_description else ''
            f'<meta name="keywords" content="{self._core.escape(meta_keywords)}">' if meta_keywords else ''
            f'<meta name="author" content="{self._core.escape(meta_author)}">' if meta_author else ''
        )
        # EQUIV
        equiv_refresh = shared.get('http-equiv-refresh')
        equiv_csp = shared.get('http-equiv-content-security-policy')
        equiv_csp_ro = shared.get('http-equiv-content-security-policy-report-only')
        equiv = (
            f'<meta http-equiv="refresh" content="{self._core.escape(equiv_refresh)}">' if equiv_refresh else ''
            f'<meta http-equiv="content-security-policy" content="{self._core.escape(equiv_csp)}">' if equiv_csp else ''
            f'<meta http-equiv="content-security-policy-report-only" content="{self._core.escape(equiv_csp_ro)}">' if equiv_csp_ro else ''
        )
        # 返回
        return {
            'content': content,
            'html': html,
            'title': self._core.escape(shared['title']),
            'toc': toc,
            'meta': meta,
            'equiv': equiv
        }

class RendererCore:
    def __init__(self, ext_renderers: Dict[str, Tuple[T_RENDERER, T_RENDERER]]=None):
        self.ext_renderers = ext_renderers or {}

    def __rrshift__(self, data: list) -> str:
        ## globally
        self._shared = data[0]
        ## inline
        # reuse
        self._reuse_cache = {}      # 缓存
        self._reuse_path = set()    # 从顶层至现在经过的路径，判断是否发生循环引用
        return self.block(data[1:])

    def block(self, chunks: Iterable[list]) -> str:
        result = []
        for chunk in chunks:
            typ = chunk[0]
            if typ == 0:
                result.append(f'<p class="yht">{self.escape(chunk[1])}</p>')
            elif typ == 1:
                result.append(f'<p class="yht">{self.inline(chunk[1])}</p>')
            elif typ == 3:
                try:
                    result.append({
                        'had': self.yhb_header,
                        'lst': self.yhb_list,
                        'pgb': self.yhb_pagebreak,
                        'sep': self.yhb_separator,
                        'not': self.yhb_note,
                        'quo': self.yhb_quote,
                        'tab': self.yhb_table,
                        'col': self.yhb_collapse,
                        'dia': self.yhb_dialog,
                        'fnt': self.yhb_footnote,
                        'cod': self.yhb_code,
                        'raw': self.yhb_raw,
                        'dgr': self.yhb_diagram,
                        'fml': self.yhb_formula,
                        'img': self.yhb_image,
                        'aud': self.yhb_audio,
                        'vid': self.yhb_video,
                    }[chunk[1]](chunk[2], chunk[3]))
                except Exception:
                    typ, val, _ = exc_info()
                    warn(f'exception during rendering block "{chunk[1]}": {typ.__name__}: {val}', RuntimeWarning)
            elif typ == 5:
                try:
                    result.append(self.ext_renderers[chunk[1][0]][0](self, chunk[1][1], chunk[2], chunk[3]))
                except Exception:
                    ...
        return ''.join(result)

    def inline(self, lines: Iterable[tuple]) -> str:
        result = []
        for line in lines:
            typ = line[0]
            if typ == 0:
                result.append(self.escape(line[1]))
            elif typ == 2:
                try:
                    result.append({
                        'lnk': self.yhi_link,
                        'bld': self.yhi_bold,
                        'mak': self.yhi_mark,
                        'dim': self.yhi_dim,
                        'ita': self.yhi_italic,
                        'sha': self.yhi_shady,
                        'sup': self.yhi_superscript,
                        'sub': self.yhi_subscript,
                        'del': self.yhi_delete,
                        'sla': self.yhi_slash,
                        'shl': self.yhi_shield,
                        'bit': self.yhi_bitalic,
                        'cod': self.yhi_code,
                        'fml': self.yhi_formula,
                        'reu': self.yhi_reuse,
                        'ref': self.yhi_refer,
                        'mal': self.yhi_email
                    }[line[1]](line[2]))
                except Exception:
                    typ, val, _ = exc_info()
                    warn(f'exception during rendering inline "{line[1]}": {typ.__name__}: {val}', RuntimeWarning)
            elif typ == 4:
                try:
                    result.append(self.ext_renderers[line[1][0]][0](self, line[1][1], line[2], line[3]))
                except Exception:
                    ...
        return ''.join(result)

    def yhb_header(self, cfg: dict, header: str) -> str:
        lev = cfg['lev']
        try: self._toc_level
        except AttributeError:
            try:
                lev_ = int(self._shared['config']['RAINLotus']['toc-level'])
                self._toc_level = lev_ if lev_ <= 6 else 3
            except Exception:
                self._toc_level = 3
        vid = lev <= self._toc_level
        if vid:
            wid = f's:{self.calcid(header)}'
        return f'''<h{lev} class="yhb-had"{
                f' id="{wid}"' if vid else ''
            }>{self.escape(header)}{
                f'<a href="#{wid}"></a>' if vid else ''
            }</h{lev}>'''

    def yhb_list(self, cfg: dict, content: list) -> str:
        typ = cfg['typ']
        if typ == 'u':
            return f'''<ul class="yhb-lst">{
                    ''.join(
                        map(lambda chunks: f"""<li>{
                            self.block(chunks)
                        }</li>""", content)
                    )
                }</ul>'''
        elif typ == 'o':
            return f'''<ol class="yhb-lst"{
                    f' start="{cfg["sta"]}">' if cfg['sta'] != 1 else '>'
                }{
                    ''.join(
                        map(lambda chunks: f"""<li>{
                            self.block(chunks)
                        }</li>""", content)
                    )
                }</ol>'''
        elif typ == 't':
            return f'''<ul class="yhb-lst_t">{
                    ''.join(
                        map(lambda t_chunks: f"""<li class="_{
                            '~x-:+v*'.find(t_chunks[0]) + 1
                        }">{
                            self.block(t_chunks[1])
                        }</li>""", content)
                    )
                }</ul>'''
        elif typ == 'd':
            return f'''<dl class="yhb-lst_d">{
                    ''.join(
                        map(lambda t_chunks: f"""<dt>{
                            self.inline(t_chunks[0])
                        }</dt><dd>{
                            self.block(t_chunks[1])
                        }</dd>""", content)
                    )
                }</dl>'''

    def yhb_pagebreak(self, _a, _b) -> str:
        return '<div style="page-break-after:always"></div>'

    def yhb_separator(self, _a, _b) -> str:
        return '<hr />'

    def yhb_note(self, cfg: dict, content: list) -> str:
        return f'<div class="yhb-not _{cfg["typ"][:3]}"><div>{self.block(content)}</div></div>'

    def yhb_quote(self, cfg: dict, content: list) -> str:
        aut = cfg['aut']
        return f'''<figure class="yhb-quo"><blockquote>{
                self.block(content)
            }</blockquote>{
                f'<figcaption>{self.inline(aut)}</figcaption>' if aut else ''
            }</figure>'''

    def yhb_table(self, cfg: dict, content: list) -> str:
        hei = cfg['hei']
        ali = cfg['ali']
        tag = 'th'
        result = [[], []]
        for i, row in enumerate(content):
            rowing = []
            span_count = -1
            if i == hei:
                tag = 'td'
            for span, cell in row:
                span_count += span
                rowing.append(
                    f'''<{tag} style="text-align:{
                        'center' if span != 1 else {
                            '<': 'left',
                            '=': 'center',
                            '>': 'right'
                        }[ali[span_count]]
                    }"{
                        f' colspan="{span}"' if span != 1 else ''
                    }>{self.inline(cell)}</{tag}>'''
                )
            result[i >= hei].append(f'<tr>{"".join(rowing)}</tr>')
        return f'<table class="yhb-tab"><thead>{"".join(result[0])}</thead><tbody>{"".join(result[1])}</tbody></table>'

    def yhb_collapse(self, cfg: dict, content: list) -> str:
        opn, sun =  cfg['opn'], cfg['sum']
        return f'''<details class="yhb-col"{
                ' open>' if opn else '>'
            }<summary>{
                self.inline(sun) if sun else ''
            }</summary><div>{
                self.block(content)
            }</div></details>'''

    def yhb_dialog(self, cfg: dict, content: list) -> str:
        title = cfg.get('title')
        if not title:
            title = 'Dialog'
        else:
            title = self.escape(title)
        style = cfg.get('style')
        if not isinstance(style, str) or style not in DIALOG_STYLE:
            try: self._dialog_d_style
            except AttributeError:
                try:
                    style_ = self._shared['config']['RAINLotus']['dialog-default-style']
                    self._dialog_d_style = style_ if style_ in DIALOG_STYLE else 'default'
                except Exception:
                    self._dialog_d_style = 'default'
            style = self._dialog_d_style
        dname = cfg.get('use-default-name')
        if dname == True:
            try: self._dialog_d_name
            except AttributeError:
                try:
                    dname_ = self._shared['config']['RAINLotus']['dialog-default-name']
                    if dname_:
                        self._dialog_d_name = self.escape(dname_)
                    else:
                        self._dialog_d_name = None
                except Exception:
                    self._dialog_d_name = None
            dname = self._dialog_d_name
        elif isinstance(dname, str):
            dname = self.escape(dname)
        result = []
        for typ, msg, arg, *name in content:
            if typ == 2:
                typ = 1
                with_name = True
                if name:
                    name = self.escape(name[0])
                elif dname is not None:
                    name = dname
                else:
                    with_name = False
            else:
                with_name = False
            sub = arg.get('typ')
            if typ == 3:
                tag = 'p'
                ctn = self.inline(filter(lambda x: x[0] < 3, msg))
            elif sub in {'voice', 'hongbao'}:
                tag = 'p'
                val = arg['val']
                ctn = self.inline(filter(lambda x: x[0] < 3, msg))
            else:
                tag = 'div'
                ctn = self.block(msg)
            result.append(
                f'''<div class="_{typ}{
                    f' _{sub}' if sub else ''
                }">{
                    f"""<p>{
                        (f'{val}"' if val < 60 else f"{val//60}'"f'{val%60}"') if sub == 'voice' else
                        f'{val//100}.{val%100:02}' if sub == 'hongbao' else name
                    }</p>""" if sub in {'voice', 'hongbao'} or with_name else ''
                }<{tag}>{ctn}</{tag}></div>'''
            )
        return f'''<div class="yhb-dia"><p>{title}</p><div>{''.join(result)}</div></div>'''

    def yhb_footnote(self, cfg: dict, content: list) -> str:
        fnt = cfg['fnt']
        cid = self.calcid(fnt)
        return f'''<div class="yhb-fnt"><a class="yhi-lnk" href="#p:{cid}" id="q:{cid}">{self.escape(fnt)}</a><div>{
                self.block(content)
            }</div></div>'''

    def yhb_code(self, cfg: dict, content: list) -> str:
        lan = self.escape(cfg['lan'])
        return f'''<pre class="yhb-cod language-{lan}"><code>{self.escape("""
""".join(content))}</code></pre>'''

    def yhb_raw(self, _cfg: None, content: list) -> str:
        return '\n'.join(content)

    def yhb_diagram(self, _cfg: None, content: list) -> str:
        return f'''<div class="yhb-dgr">{self.escape("""
""".join(content))}</div>'''

    def yhb_formula(self, _cfg: None, content: list) -> str:
        return f'''<div class="yhb-fml">$${self.escape("""
""".join(content))}$$</div>'''

    def yhb_image(self, cfg: dict, content: list) -> str:
        src = cfg.get('src')
        if src:
            src = self.escape(src)
        else:
            return ''
        alt = cfg.get('alt')
        return f'''<figura class="yhb-img"><img src="{
                self.escape(src)
            }"{
                f' alt="{self.escape(alt)}"' if alt else ''
            } />{
                f'<figcaption>{self.block(content or alt)}</figcaption>' if content or alt else ''
            }</figura>'''

    def yhb_audio(self, cfg: dict, content: list) -> str:
        src = cfg.get('src')
        if src:
            src = self.escape(src)
        else:
            return ''
        opt = ' '.join(o for o in cfg.keys() if o != 'src')
        return f'''<audio class="yhb-aud" src="{src}"{
                f' {opt}' if opt else ''
            }>{
                self.block(content)
            }</audio>'''

    def yhb_video(self, cfg: dict, content: list) -> str:
        src = cfg.get('src')
        if src:
            src = self.escape(src)
        else:
            return ''
        opt = ' '.join(o for o in cfg.keys() if o != 'src')
        return f'''<video class="yhb-vid" src="{src}"{
                f' {opt}' if opt else ''
            }>{
                self.block(content)
            }</video>'''

    def yhi_link(self, content: list) -> str:
        typ, tit, lnk = content
        lnk = self.escape(lnk)
        if typ == 'lnk':    # 注意`tit`的类型差异
            return f'<a class="yhi-lnk" href="{lnk}">{self.inline(tit)}</a>'
        elif typ == 'cro':
            return f'<a class="yhi-lnk" href="{lnk}#s:{self.calcid(tit)}">{self.escape(tit)}</a>'
        else:   # 'img'
            return f'''<img class="yhi-img" src="{lnk}"{
                f' alt="{self.escape(tit)}"' if tit else ''
            } />'''

    def yhi_bold(self, content: list) -> str:
        return f'<strong>{self.inline(content)}</strong>'

    def yhi_mark(self, content: list) -> str:
        return f'<mark class="yhi-mak">{self.inline(content)}</mark>'

    def yhi_dim(self, content: list) -> str:
        return f'<span class="yhi-dim">{self.inline(content)}</span>'

    def yhi_italic(self, content: list) -> str:
        return f'<i>{self.inline(content)}</i>'

    def yhi_shady(self, content: list) -> str:
        return f'<span class="yhi-sha">{self.inline(content)}</span>'

    def yhi_superscript(self, content: list) -> str:
        return f'<sup>{self.inline(content)}</sup>'

    def yhi_subscript(self, content: list) -> str:
        return f'<sub>{self.inline(content)}</sub>'

    def yhi_delete(self, content: list) -> str:
        return f'<del>{self.inline(content)}</del>'

    def yhi_slash(self, content: list) -> str:
        return f'<span class="yhi-sla">{self.inline(content)}</span>'

    def yhi_shield(self, content: list) -> str:
        sign, lent = content
        return {'b': '█',
                'x': '×',
                'o': '●'}.get(sign, '＊') * lent

    def yhi_bitalic(self, content: list) -> str:
        return f'<i><strong>{self.inline(content)}</strong></i>'

    def yhi_code(self, content: str) -> str:
        return f'<code class="yhi-cod">{self.escape(content)}</code>'

    def yhi_formula(self, content: str) -> str:
        return f'<span class="yhi-fml">$${self.escape(content)}$$</span>'

    def yhi_reuse(self, query: str) -> str:
        # 循环引用检测
        if query in self._reuse_path:
            return '<span class="yhi-err"></span>'
        # 尝试查缓存
        try: return self._reuse_cache[query]
        except KeyError: ...
        # Go deeper
        self._reuse_path.add(query)
        # 多次尝试（如果有更多，那么还需要写更多）
        try:
            alias = self._shared['config']['RAINLotus']['alias'][query] # 实际上只有这一个才可能会产生循环引用
        except Exception:
            try:
                alias = self._shared['config']['RAINLotus']['alias-code'][query]
            except Exception:
                try:
                    alias = self._shared['config']['RAINLotus']['alias-raw'][query]
                except Exception:
                    alias = ''
                else:
                    alias = self.escape(alias)
            else:
                alias = self.yhi_code(alias)
        else:
            alias = self.inline(alias)
        self._reuse_path.remove(query)
        # 写缓存
        self._reuse_cache[query] = alias
        # 返回结果
        return alias

    def yhi_refer(self, content: list) -> str:
        typ, tit = content
        cid = self.calcid(tit)
        if typ == 'fnt':
            return f'<sup><a class="yhi-lnk" id="p:{cid}" href="#q:{cid}">{self.escape(tit)}</a></sup>'
        else:   # 'cro'
            return f'<a class="yhi-lnk" href="#s:{cid}">{self.escape(tit)}</a>'

    def yhi_email(self, content: list) -> str:
        user, domain = content
        return f'''<span class="yhi-mal">{
                ''.join(
                    f'<span class="_b">{sub[::-1]}</span>'
                    for sub in domain.split('.')[::-1]
                )
            }{
                f'<span class="_a">{self.escape(user)[::-1]}</span>'
            }</span>'''

    @staticmethod
    @lru_cache
    def calcid(text: str) -> str:
        text = text.lower()
        return urlsafe_b64encode(shake_128(''.join(
                c for c in text if 'a' <= c <= 'z' or '0' <= c <= '9' or c > '\xFF'
            ).encode()).digest(6)).decode()

    @staticmethod
    def escape(text: str) -> str:
        return ''.join({'"':'&#34;',
                        '&':'&amp;',
                        '<':'&lt;'}.get(c, c) for c in text)