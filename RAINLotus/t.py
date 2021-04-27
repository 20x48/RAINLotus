"""
The UNIT TEST for RAINLotus.
For development only.
"""
try:
    from p import Parser, DEFAULT_TITLE
    from r import RendererCore, Renderer, Template
except ImportError:
    from .p import Parser, DEFAULT_TITLE
    from .r import RendererCore, Renderer, Template

from unittest import main, TestCase


parse = Parser()
render = RendererCore()


class Tester(TestCase):
    def test_title(self):
        R= (r'Yes Title',
            r'========='
        ) >> parse
        self.assertEqual(R[0]['title'], 'Yes Title')
        R= (r'Bad Title',
            r' ======= '
        ) >> parse
        self.assertEqual(R[0]['title'], DEFAULT_TITLE)
        self.assertEqual(R[1], (0, 'Bad Title'))
        self.assertEqual(len(R), 2)

    def test_header(self):
        R= (r'= no header 1',
            r'== header 2',
            r'=== header 3',
            r'====bad header 4',
            r'=====  header 5',
        ) >> parse
        self.assertEqual(R[0]['headers'], [(2, 'header 2'), (3, 'header 3'), (5, 'header 5')])
        self.assertEqual(R[1], (0, '= no header 1'))
        self.assertEqual(R[2], [3, 'had', {'lev': 2}, 'header 2'])
        self.assertEqual(R[3], [3, 'had', {'lev': 3}, 'header 3'])
        self.assertEqual(R[4], (0, '====bad header 4'))
        self.assertEqual(R[5], [3, 'had', {'lev': 5}, 'header 5'])
        self.assertEqual(R >> render,
            '<p class="yht">= no header 1</p>'
            f'<h2 class="yhb-had" id="s:{render.calcid("header 2")}">header 2<a href="#s:{render.calcid("header 2")}"></a></h2>'
            f'<h3 class="yhb-had" id="s:{render.calcid("header 3")}">header 3<a href="#s:{render.calcid("header 3")}"></a></h3>'
            '<p class="yht">====bad header 4</p>'
            '<h5 class="yhb-had">header 5</h5>')

    def test_ulist(self):
        R= (r'.. item 1',
            r'.. item 2',
            r'    .. item 2.1',
            r'        content below item 2.1',
            r'    .. item 2.2',
            r'...bad item'
        ) >> parse
        self.assertEqual(R[1], [3, 'lst', {'typ': 'u'}, [
            [(0, 'item 1')],
            [
                (0, 'item 2'),
                [3, 'lst', {'typ': 'u'}, [
                    [
                        (0, 'item 2.1'),
                        (0, 'content below item 2.1')
                    ],
                    [(0, 'item 2.2')]
                ]]
            ]
        ]])
        self.assertEqual(R[2], (0, '...bad item'))
        self.assertEqual(R >> render,
            '<ul class="yhb-lst">'
                '<li>'
                    '<p class="yht">item 1</p>'
                '</li><li>'
                '<p class="yht">item 2</p>'
                    '<ul class="yhb-lst">'
                        '<li>'
                            '<p class="yht">item 2.1</p>'
                            '<p class="yht">content below item 2.1</p>'
                        '</li><li>'
                            '<p class="yht">item 2.2</p>'
                        '</li>'
                    '</ul>'
                '</li>'
            '</ul>'
            '<p class="yht">...bad item</p>')

    def test_olist(self):
        R= (r'?. item 1',
            r'?. item 2',
            r';;;',
            r'314. item 314',
            r'000. item 315'
        ) >> parse
        self.assertEqual(R[1], [3, 'lst', {'typ': 'o', 'sta': 1}, [[(0, 'item 1')], [(0, 'item 2')]]])
        self.assertEqual(R[2], [3, 'lst', {'typ': 'o', 'sta': 314}, [[(0, 'item 314')], [(0, 'item 315')]]])
        self.assertEqual(R >> render,
            '<ol class="yhb-lst">'
                '<li>'
                    '<p class="yht">item 1</p>'
                '</li><li>'
                    '<p class="yht">item 2</p>'
                '</li>'
            '</ol>'
            '<ol class="yhb-lst" start="314">'
                '<li>'
                    '<p class="yht">item 314</p>'
                '</li><li>'
                    '<p class="yht">item 315</p>'
                '</li>'
            '</ol>')

    def test_tlist(self):
        R= (r'*. Achieved',
            r'v. Supported',
            r'+. Added feature',
            r':. Todo / Modified',
            r'-. Removed feature',
            r'x. Unsupported',
            r'~. Mission impossible',
        ) >> parse
        self.assertEqual(R[1], [3, 'lst', {'typ': 't'}, [
            ['*', [(0, 'Achieved')]],
            ['v', [(0, 'Supported')]],
            ['+', [(0, 'Added feature')]],
            [':', [(0, 'Todo / Modified')]],
            ['-', [(0, 'Removed feature')]],
            ['x', [(0, 'Unsupported')]],
            ['~', [(0, 'Mission impossible')]],
        ]])
        self.assertEqual(R >> render,
            '<ul class="yhb-lst_t">'
                '<li class="_7">'
                    '<p class="yht">Achieved</p>'
                '</li><li class="_6">'
                    '<p class="yht">Supported</p>'
                '</li><li class="_5">'
                    '<p class="yht">Added feature</p>'
                '</li><li class="_4">'
                    '<p class="yht">Todo / Modified</p>'
                '</li><li class="_3">'
                    '<p class="yht">Removed feature</p>'
                '</li><li class="_2">'
                    '<p class="yht">Unsupported</p>'
                '</li><li class="_1">'
                    '<p class="yht">Mission impossible</p>'
                '</li>'
            '</ul>')

    def test_dlist(self):
        R= (r'::: Intel',
            r'    牙膏厂。',
            r'::: AMD',
            r'    ＹＥＳ！',
            r'::: Seventeen Cards',
            r'    十七张牌你能秒我？你能秒杀我？！',
            r'    你今天能十七张牌把卢本伟秒了，我！当！场！就把这个电脑屏幕吃掉！！！'
        ) >> parse
        self.assertEqual(R[1], [3, 'lst', {'typ': 'd'}, [
            [((0, 'Intel'),), [(0, '牙膏厂。')]],
            [((0, 'AMD'),), [(0, 'ＹＥＳ！')]],
            [((0, 'Seventeen Cards'),), [
                (0, '十七张牌你能秒我？你能秒杀我？！'),
                (0, '你今天能十七张牌把卢本伟秒了，我！当！场！就把这个电脑屏幕吃掉！！！')
            ]]
        ]])
        self.assertEqual(R >> render,
            '<dl class="yhb-lst_d">'
                '<dt>Intel</dt>'
                    '<dd><p class="yht">牙膏厂。</p></dd>'
                '<dt>AMD</dt>'
                    '<dd><p class="yht">ＹＥＳ！</p></dd>'
                '<dt>Seventeen Cards</dt>'
                    '<dd>'
                        '<p class="yht">十七张牌你能秒我？你能秒杀我？！</p>'
                        '<p class="yht">你今天能十七张牌把卢本伟秒了，我！当！场！就把这个电脑屏幕吃掉！！！</p>'
                    '</dd>'
            '</dl>')

    def test_sep_pgbreak(self):
        R= (r'--',
            r'-----',
            r'%%%'
        ) >> parse
        self.assertEqual(R[1], (0, '--'))
        self.assertEqual(R[2], [3, 'sep', None, None])
        self.assertEqual(R[3], [3, 'pgb', None, None])
        self.assertEqual(R >> render,
            '<p class="yht">--</p>'
            '<hr />'
            '<div style="page-break-after:always"></div>')

    def test_b_note(self):
        R= (r'*** ImpOrTant',
            r'    试试就逝世'
        ) >> parse
        self.assertEqual(R[1], [3, 'not', {'typ': 'important'}, [(0, '试试就逝世')]])
        self.assertEqual(R >> render,
            '<div class="yhb-not _imp"><div>'
                '<p class="yht">试试就逝世</p>'
            '</div></div>')

    def test_b_quote(self):
        R= (r'""" -- Rumi',
            r'    The quieter you become, the more you are able to hear.',
            r'""" ——鲁迅',
            r'    我没说过这话，不过确实在理！',
            r'""" QUOTE WITHOUT AUTHOR',
            r'"""',
            r'    QUOTE AT NEW LINE'
        ) >> parse
        self.assertEqual(R[1], [3, 'quo', {'aut': ((0, 'Rumi'),)}, [(0, 'The quieter you become, the more you are able to hear.')]])
        self.assertEqual(R[2], [3, 'quo', {'aut': ((0, '鲁迅'),)}, [(0, '我没说过这话，不过确实在理！')]])
        self.assertEqual(R[3], [3, 'quo', {'aut': None}, [(0, 'QUOTE WITHOUT AUTHOR')]])
        self.assertEqual(R[4], [3, 'quo', {'aut': None}, [(0, 'QUOTE AT NEW LINE')]])
        self.assertEqual(R >> render,
            '<figure class="yhb-quo">'
                '<blockquote>'
                    '<p class="yht">The quieter you become, the more you are able to hear.</p>'
                '</blockquote>'
                '<figcaption>Rumi</figcaption>'
            '</figure>'
            '<figure class="yhb-quo">'
                '<blockquote>'
                    '<p class="yht">我没说过这话，不过确实在理！</p>'
                '</blockquote>'
                '<figcaption>鲁迅</figcaption>'
            '</figure>'
            '<figure class="yhb-quo">'
                '<blockquote>'
                    '<p class="yht">QUOTE WITHOUT AUTHOR</p>'
                '</blockquote>'
            '</figure>'
            '<figure class="yhb-quo">'
                '<blockquote>'
                    '<p class="yht">QUOTE AT NEW LINE</p>'
                '</blockquote>'
            '</figure>')

    def test_b_table(self):
        R= (r'|||',
            r'    | H1 | H2 | H3',
            r'    |',
            r'    | C1 | >>>',
            r'    | C4 | C5 | >',
            r'    | C7 | C8 | C\|',
            r'||| 2',
            r'    | H1',
            r'    | =',
            r'    | C1',
            r'||| csv 2',
            r'    H1, H2, >',
            r'    H4, >>>',
            r'    =, <<<',
            r'    C1, C2, C3',
            r'    C4, ~~C5~~, C6',
            r'||| Json',
            r'    {'
            r'        "head": [["H1", ">>>"], ["H4", ">>>"]],'
            r'        "align": ["<", "=", ">"],'
            r'        "body": [["C1", ">>>"]]'
            r'    }',
            r'||| jSon',
            r'    {"head": 1, "align": 2, "body": 3}',
            r'||| jsOn',
            r'    {"head": [1], "align": [2], "body": [3]}',
            r'||| jsoN',
            r'    {"head": [[]], "align": [[]], "body": [[[]]]}',
            r'||| JSON RoTaTe',
            r'    [["H1", ">", "H{3}"], [], ["C1", "C2", "C3"]]'
        ) >> parse
        self.assertEqual(R[1], [3, 'tab', {'hei': 1, 'rot': False, 'ali': ['=', '=', '=']}, [
            [[1, ((0, 'H1'),)], [1, ((0, 'H2'),)], [1, ((0, 'H3'),)]],
            [[3, ((0, 'C1'),)]],
            [[1, ((0, 'C4'),)], [2, ((0, 'C5'),)]],
            [[1, ((0, 'C7'),)], [1, ((0, 'C8'),)], [1, ((0, 'C|'),)]]
        ]])
        self.assertEqual(R[2], [3, 'tab', {'hei': 2, 'rot': False, 'ali': ['=', '<', '<']}, [
            [[1, ((0, 'H1'),)], [2, ((0, 'H2'),)]],
            [[3, ((0, 'H4'),)]],
            [[1, ((0, 'C1'),)], [1, ((0, 'C2'),)], [1, ((0, 'C3'),)]],
            [[1, ((0, 'C4'),)], [1, ((2, 'del', ((0, 'C5'),)),)], [1, ((0, 'C6'),)]]
        ]])
        self.assertEqual(R[3], [3, 'tab', {'hei': 2, 'rot': False, 'ali': ['<', '=', '>']}, [
            [[3, ((0, 'H1'),)]],
            [[3, ((0, 'H4'),)]],
            [[3, ((0, 'C1'),)]]
        ]])
        self.assertEqual(R[4], [3, 'tab', {'hei': 1, 'rot': True, 'ali': ['=', '=', '=']}, [
            [[2, ((0, 'H1'),)], [1, ((0, 'H'), (2, 'reu', '3'))]],
            [[1, ((0, 'C1'),)], [1, ((0, 'C2'),)], [1, ((0, 'C3'),)]]
        ]])
        self.assertEqual(R >> render,
            '<table class="yhb-tab">'
                '<thead>'
                    '<tr>'
                        '<th style="text-align:center">H1</th>'
                        '<th style="text-align:center">H2</th>'
                        '<th style="text-align:center">H3</th>'
                    '</tr>'
                '</thead><tbody>'
                    '<tr>'
                        '<td style="text-align:center" colspan="3">C1</td>'
                    '</tr><tr>'
                        '<td style="text-align:center">C4</td>'
                        '<td style="text-align:center" colspan="2">C5</td>'
                    '</tr><tr>'
                        '<td style="text-align:center">C7</td>'
                        '<td style="text-align:center">C8</td>'
                        '<td style="text-align:center">C|</td>'
                    '</tr>'
                '</tbody>'
            '</table>'
            '<table class="yhb-tab">'
                '<thead>'
                    '<tr>'
                        '<th style="text-align:center">H1</th>'
                        '<th style="text-align:center" colspan="2">H2</th>'
                    '</tr><tr>'
                        '<th style="text-align:center" colspan="3">H4</th>'
                    '</tr>'
                '</thead><tbody>'
                    '<tr>'
                        '<td style="text-align:center">C1</td>'
                        '<td style="text-align:left">C2</td>'
                        '<td style="text-align:left">C3</td>'
                    '</tr><tr>'
                        '<td style="text-align:center">C4</td>'
                        '<td style="text-align:left"><del>C5</del></td>'
                        '<td style="text-align:left">C6</td>'
                    '</tr>'
                '</tbody>'
            '</table>'
            '<table class="yhb-tab">'
                '<thead>'
                    '<tr>'
                        '<th style="text-align:center" colspan="3">H1</th>'
                    '</tr><tr>'
                        '<th style="text-align:center" colspan="3">H4</th>'
                    '</tr>'
                '</thead><tbody>'
                    '<tr>'
                        '<td style="text-align:center" colspan="3">C1</td>'
                    '</tr>'
                '</tbody>'
            '</table>'
            '<table class="yhb-tab">'
                '<thead>'
                    '<tr>'
                        '<th style="text-align:center" colspan="2">H1</th>'
                        '<th style="text-align:center">H</th>'
                    '</tr>'
                '</thead><tbody>'
                    '<tr>'
                        '<td style="text-align:center">C1</td>'
                        '<td style="text-align:center">C2</td>'
                        '<td style="text-align:center">C3</td>'
                    '</tr>'
                '</tbody>'
            '</table>')

    def test_b_coll(self):
        R= (r'~~~ OpEn',
            r'    content',
            r'~~~ open More',
            r'    blah blah',
            r'~~~ closed',
            r'    content',
            r'~~~',
            r'    no summary'
        ) >> parse
        self.assertEqual(R[1], [3, 'col', {'opn': True, 'sum': None}, [(0, 'content')]])
        self.assertEqual(R[2], [3, 'col', {'opn': True, 'sum': ((0, 'More'),)}, [(0, 'blah blah')]])
        self.assertEqual(R[3], [3, 'col', {'opn': False, 'sum': ((0, 'closed'),)}, [(0, 'content')]])
        self.assertEqual(R[4], [3, 'col', {'opn': False, 'sum': None}, [(0, 'no summary')]])
        self.assertEqual(R >> render,
            '<details class="yhb-col" open>'
                '<summary></summary>'
                '<div>'
                    '<p class="yht">content</p>'
                '</div>'
            '</details>'
            '<details class="yhb-col" open>'
                '<summary>More</summary>'
                '<div>'
                    '<p class="yht">blah blah</p>'
                '</div>'
            '</details>'
            '<details class="yhb-col">'
                '<summary>closed</summary>'
                '<div>'
                    '<p class="yht">content</p>'
                '</div>'
            '</details>'
            '<details class="yhb-col">'
                '<summary></summary>'
                '<div>'
                    '<p class="yht">no summary</p>'
                '</div>'
            '</details>')

    def test_b_dialog(self):
        R= (r'@@@ title="Chat with 20x48"',
            r'    -> whats your address?',
            r'    <- 173.168.15.10',
            r'    -> no, your local address',
            r'    <- 127.0.0.1',
            r'    -> i mean your physical address',
            r'    <- 29:01:38:62:31:58',
            r'    -> fuck u',
            r'',
            r'@@@ style="wechat" nonexist-argument',
            r'    ~> 60',
            r'    <> 你撤回了一条消息',
            r'    $> 888',
            r'        恭喜发财',
            r'        //rich// text'
            r'',
            r'    <~',
            r'    <>',
            r'',
            r'    <? Sending message',
            r'    <!',
            r'        Failed message',
            r'        /// image src=https://example.com/xxx.jpg',
            r'    ->@ RAINLotus @ Message with name',
            r'    ->@ user@@example.com @ Dual "@" to escape'
        ) >> parse
        self.assertEqual(R[1], [3, 'dia', {'title': 'Chat with 20x48'}, [
            [1, [(0, 'whats your address?')], {}],
            [0, [(0, '173.168.15.10')], {}],
            [1, [(0, 'no, your local address')], {}],
            [0, [(0, '127.0.0.1')], {}],
            [1, [(0, 'i mean your physical address')], {}],
            [0, [(0, '29:01:38:62:31:58')], {}],
            [1, [(0, 'fuck u')], {}]
        ]])
        self.assertEqual(R[2], [3, 'dia', {'style': 'wechat'}, [
            [1, [], {'typ': 'voice', 'val': 60}],
            [3, [(0, '你撤回了一条消息')], {}],
            [1, [(0, '恭喜发财'), [1, [(2, 'ita', ((0, 'rich'),)), (0, ' text')]]], {'typ': 'hongbao', 'val': 88800}],
            [0, [(0, 'Sending message')], {'typ': 'sending'}],
            [0, [(0, 'Failed message'), [3, 'img', {'src': 'https://example.com/xxx.jpg'}, []]], {'typ': 'failed'}],
            [2, [(0, 'Message with name')], {}, 'RAINLotus'],
            [2, [(0, 'Dual "@" to escape')], {}, 'user@example.com']
        ]])
        self.assertEqual(R >> render,
            '<div class="yhb-dia">'
                '<p>Chat with 20x48</p>'
                '<div>'
                    '<div class="_1">'
                        '<div>'
                            '<p class="yht">whats your address?</p>'
                        '</div>'
                    '</div><div class="_0">'
                        '<div>'
                            '<p class="yht">173.168.15.10</p>'
                        '</div>'
                    '</div><div class="_1">'
                        '<div>'
                            '<p class="yht">no, your local address</p>'
                        '</div>'
                    '</div><div class="_0">'
                        '<div>'
                            '<p class="yht">127.0.0.1</p>'
                        '</div>'
                    '</div><div class="_1">'
                        '<div>'
                            '<p class="yht">i mean your physical address</p>'
                        '</div>'
                    '</div><div class="_0">'
                        '<div>'
                            '<p class="yht">29:01:38:62:31:58</p>'
                        '</div>'
                    '</div><div class="_1">'
                        '<div>'
                            '<p class="yht">fuck u</p>'
                        '</div>'
                    '</div>'
                '</div>'
            '</div>'
            '<div class="yhb-dia">'
                '<p>Dialog</p>'
                '<div>'
                    '<div class="_1 _voice">'
                        '<p>1\'0"</p>'
                        '<p></p>'
                    '</div><div class="_3">'
                        '<p>你撤回了一条消息</p>'
                    '</div><div class="_1 _hongbao">'
                        '<p>888.00</p>'
                        '<p>恭喜发财</p>'
                    '</div><div class="_0 _sending">'
                        '<div>'
                            '<p class="yht">Sending message</p>'
                        '</div>'
                    '</div><div class="_0 _failed">'
                        '<div>'
                            '<p class="yht">Failed message</p>'
                            '<figura class="yhb-img">'
                                '<img src="https://example.com/xxx.jpg" />'
                            '</figura>'
                        '</div>'
                    '</div><div class="_1">'
                        '<p>RAINLotus</p>'
                        '<div>'
                            '<p class="yht">Message with name</p>'
                        '</div>'
                    '</div><div class="_1">'
                        '<p>user@example.com</p>'
                        '<div>'
                            '<p class="yht">Dual &#34;@&#34; to escape</p>'
                        '</div>'
                    '</div>'
                '</div>'
            '</div>')

    def test_b_footnote_code(self):
        R= (r'>>> footnote',
            r'    content',
            r'``` C++',
            r'    #include <iostream>',
            r'',
            r'',
            r'    int main() {',
            r'        std::cerr << "fucking the world" << std::endl;',
            r'        return 0;',
            r'    }',
            r'```',
            r'    plsinyrcy'
        ) >> parse
        self.assertEqual(R[1], [3, 'fnt', {'fnt': 'footnote'}, [(0, 'content')]])
        self.assertEqual(R[2], [3, 'cod', {'lan': 'c++'}, [
            '#include <iostream>',
            '', '',
            'int main() {',
            '    std::cerr << "fucking the world" << std::endl;',
            '    return 0;',
            '}',
        ]])
        self.assertEqual(R[3], [3, 'cod', {'lan': 'plaintext'}, ['plsinyrcy']])
        self.assertEqual(R >> render,
            '<div class="yhb-fnt">'
                f'<a class="yhi-lnk" href="#p:{render.calcid("footnote")}" id="q:{render.calcid("footnote")}">footnote</a>'
                '<div>'
                    '<p class="yht">content</p>'
                '</div>'
            '</div>'
            '<pre class="yhb-cod language-c++"><code>'
                '#include &lt;iostream>\n\n\n'
                'int main() {\n'
                '    std::cerr &lt;&lt; &#34;fucking the world&#34; &lt;&lt; std::endl;\n'
                '    return 0;\n'
                '}'
            '</code></pre>'
            '<pre class="yhb-cod language-plaintext"><code>'
                'plsinyrcy'
            '</code></pre>')

    def test_b_raw_diagram_formula(self):
        R= (r'!!! raw',
            r'    <br /> it can be dangerous!',
            r'### diagram',
            r'    content',
            r'$$$ formula',
            r'    content'
        ) >> parse
        self.assertEqual(R[1], [3, 'raw', None, ['raw', '<br /> it can be dangerous!']])
        self.assertEqual(R[2], [3, 'dgr', None, ['diagram', 'content']])
        self.assertEqual(R[3], [3, 'fml', None, ['formula', 'content']])
        self.assertEqual(R >> render,
            'raw\n<br /> it can be dangerous!'
            '<div class="yhb-dgr">diagram\ncontent</div>'
            '<div class="yhb-fml">$$formula\ncontent$$</div>')

    def test_b_general(self):
        R= (r'/// video src = https://example.com/xxx.mp4 autoplay loop nonexist',
            r'    Your browser does not support blah blah.'
        ) >> parse
        self.assertEqual(R[1], [3, 'vid', {'src': 'https://example.com/xxx.mp4', 'autoplay': True, 'loop': True}, [(0, 'Your browser does not support blah blah.')]])
        self.assertEqual(R >> render,
            '<video class="yhb-vid" src="https://example.com/xxx.mp4" autoplay loop>'
                '<p class="yht">Your browser does not support blah blah.</p>'
            '</video>')

    def test_b_general_plus(self):
        R= (r'&&& Extmod -> ext',
            r'',
            r'/// ext.method ? c1',
            r'    /// ext.method ? c2',
            r'        Hello world~',
            r'/// ext.non',
        ) >> Parser({'Extmod': ((lambda x: x == 'method', None), (lambda x: True, None), None)})
        self.assertEqual(R[1],
            [5, ('Extmod', 'method'), {}, [
                (0, 'c1'),
                [5, ('Extmod', 'method'), {}, [
                    (0, 'c2'),
                    (0, 'Hello world~')]]]])
        self.assertEqual(len(R), 2)

    def test_b_config(self):
        R= (r'&&& RAINLotus -> rl',
            r'    nonexist 1',
            r'    alias-code magic_quote `',
            r'    meta-keywords RAINLotus,markup language,',
            r'',
            r'&&& RAINLotus -> yh',
            r'    alias-code',
            r'        magic_print echo `...`',
            r'    alias',
            r'        rich_text Hi, \\RAINLotus\\',
            r'    meta-keywords',
            r'        Markdown,Asciidoc,reStructuredText',
            r'',
            r'&&& RAINLotus',
            r'    dialog-default-style'
        ) >> Parser()
        self.assertEqual(R[0]['config'], {
            'RAINLotus': {
                'alias': {'rich_text': ((0, 'Hi, '), (2, 'sla', ((0, 'RAINLotus'),)))},
                'alias-code': {'magic_quote': '`', 'magic_print': 'echo `...`'},
                'meta-keywords': 'RAINLotus,markup language,Markdown,Asciidoc,reStructuredText',
                'dialog-default-style': ''
            }
        })

    def test_b_config_plus(self):
        def ui_lotus(cmds):
            cfg = {}
            for cmd, ctts in cmds.items():
                if cmd == 'color' and ctts == ['mediumaquamarine']:
                    cfg[cmd] = (0x66, 0xCD, 0xAA)
                elif cmd == 'border-radius' and len(ctts) == 1:
                    cfg[cmd] = int(ctts[0].split('px', 1)[0])
            return cfg
        R= (r'&&& UILotus -> 111',
            r'    color mediumaquamarine',
            r'    nonexist 1',
            r'',
            r'&&& UILotus -> 233',
            r'    border-radius 5px',
            r'',
            r'&&& RAINSakura',
            r'    api https://example.com',
            r'',
            r'&&& RAINSakura',
            r'    api http://example.org',
            r'',
            r'&&& nonexist -> non'
        ) >> Parser({'UILotus': (None, None, ui_lotus), 'RAINSakura': None})
        self.assertEqual(R[0]['imports'], {'UILotus', 'RAINSakura'})
        self.assertEqual(R[0]['config'], {
            'UILotus': {
                'color': (102, 205, 170),
                'border-radius': 5,
            },
            'RAINSakura': {
                'api': [
                    'https://example.com',
                    'http://example.org'
                ]
            }
        })

    def test_b_comment(self):
        self.assertEqual(len(r';;; can not see me~' >> parse), 1)

    def test_i_autourl(self):
        R = ' '.join((
            r'https://[2001:db8::ff00:0.66.131.41]/user/root/',
            r'https://[2001:db8::ff00:42:8329]/favicon.ico',
            r'rsync://user@example.com',
            r'irc6://114.51.41.91:91',
            r'https://[::1]'
        )) >> parse
        self.assertEqual(R[1], [1, [
            (2, 'lnk', ('lnk', ((0, 'https://[2001:db8::ff00:0.66.131.41]/user/root/'),), 'https://[2001:db8::ff00:0.66.131.41]/user/root/')), (0, ' '),
            (2, 'lnk', ('lnk', ((0, 'https://[2001:db8::ff00:42:8329]/favicon.ico'),), 'https://[2001:db8::ff00:42:8329]/favicon.ico')), (0, ' '),
            (2, 'lnk', ('lnk', ((0, 'rsync://user@example.com'),), 'rsync://user@example.com')), (0, ' '),
            (2, 'lnk', ('lnk', ((0, 'irc6://114.51.41.91:91'),), 'irc6://114.51.41.91:91')), (0, ' '),
            (2, 'lnk', ('lnk', ((0, 'https://[::1]'),), 'https://[::1]'))
        ]])
        self.assertEqual(R >> render,
            '<p class="yht">'
                '<a class="yhi-lnk" href="https://[2001:db8::ff00:0.66.131.41]/user/root/">https://[2001:db8::ff00:0.66.131.41]/user/root/</a> '
                '<a class="yhi-lnk" href="https://[2001:db8::ff00:42:8329]/favicon.ico">https://[2001:db8::ff00:42:8329]/favicon.ico</a> '
                '<a class="yhi-lnk" href="rsync://user@example.com">rsync://user@example.com</a> '
                '<a class="yhi-lnk" href="irc6://114.51.41.91:91">irc6://114.51.41.91:91</a> '
                '<a class="yhi-lnk" href="https://[::1]">https://[::1]</a>'
            '</p>')

    def test_i_hangbuelang(self):
        R = r'**Bold//Italic//**' >> parse
        self.assertEqual(R[1], [1, [(2, 'bld', ((0, 'Bold'), (2, 'ita', ((0, 'Italic'),))))]])
        self.assertEqual(R >> render, '<p class="yht"><strong>Bold<i>Italic</i></strong></p>')

    def test_i_shield(self):
        R = r'SCP-2521 =O2=|=o5=|=O2=|=o1=' >> parse
        self.assertEqual(R[1], [1, [
            (0, 'SCP-2521 '),
            (2, 'shl', ('o', 2)), (0, '|'),
            (2, 'shl', ('o', 5)), (0, '|'),
            (2, 'shl', ('o', 2)), (0, '|'),
            (2, 'shl', ('o', 1))
        ]])
        self.assertEqual(R >> render, '<p class="yht">SCP-2521 ●●|●●●●●|●●|●</p>')

    def test_i_bitalic(self):
        R = r'/*Bitalic*/' >> parse
        self.assertEqual(R[1], [1, [(2, 'bit', ((0, 'Bitalic'),))]])
        self.assertEqual(R >> render, '<p class="yht"><i><strong>Bitalic</strong></i></p>')

    def test_i_code(self):
        R = r'`print("Hello world!")`' >> parse
        self.assertEqual(R[1], [1, [(2, 'cod', 'print("Hello world!")')]])
        self.assertEqual(R >> render, '<p class="yht"><code class="yhi-cod">print(&#34;Hello world!&#34;)</code></p>')

    def test_i_formula(self):
        R = r'$$ ax^2+bx+c=0 $$' >> parse
        self.assertEqual(R[1], [1, [(2, 'fml', 'ax^2+bx+c=0')]])
        self.assertEqual(R >> render, '<p class="yht"><span class="yhi-fml">$$ax^2+bx+c=0$$</span></p>')

    def test_i_reuse(self):
        R =(r'&&& RAINLotus',
            r'    alias',
            r'        1 a{2}',
            r'        2 b{3}',
            r'        3 c{1}',
            r'        yh RAINLotus',
            r'',
            r'Love {rl}.',
            r'Miss {yh}.',
            r'{1}',
            r'{2}',
            r'{3}',
        ) >> parse
        self.assertEqual(R[1], [1, [(0, 'Love '), (2, 'reu', 'rl'), (0, '.')]])
        self.assertEqual(R >> render,
            '<p class="yht">Love .</p>'
            '<p class="yht">Miss RAINLotus.</p>'
            '<p class="yht">abc<span class="yhi-err"></span></p>'
            '<p class="yht">bc<span class="yhi-err"></span></p>'
            '<p class="yht">c<span class="yhi-err"></span></p>')

    def test_i_link(self):
        R =(r'[\ALx [deprecated]]<alx://deprecated>'
            r'[#Paragraph]<example.com/article>'
            r'[\#213]<site-213>'
            r'[docs]<docs.20x48.net>'
            r'[!hi]<hello.jpg>'
        ) >> parse
        self.assertEqual(R[1], [1, [
            (2, 'lnk', ('lnk', ((0, '\\ALx [deprecated]'),), 'alx://deprecated')),
            (2, 'lnk', ('cro', 'Paragraph', 'example.com/article')),
            (2, 'lnk', ('lnk', ((0, '#213'),), 'site-213')),
            (2, 'lnk', ('lnk', ((0, 'docs'),), 'docs.20x48.net')),
            (2, 'lnk', ('img', 'hi', 'hello.jpg'))
        ]])
        self.assertEqual(R >> render,
            '<p class="yht">'
                '<a class="yhi-lnk" href="alx://deprecated">\\ALx [deprecated]</a>'
                f'<a class="yhi-lnk" href="example.com/article#s:{render.calcid("Paragraph")}">Paragraph</a>'
                '<a class="yhi-lnk" href="site-213">#213</a>'
                '<a class="yhi-lnk" href="docs.20x48.net">docs</a>'
                '<img class="yhi-img" src="hello.jpg" alt="hi" />'
            '</p>')

    def test_i_refer(self):
        R = r'[^footnote][#Paragraph]' >> parse
        self.assertEqual(R[1], [1, [(2, 'ref', ('fnt', 'footnote')), (2, 'ref', ('inr', 'Paragraph'))]])
        self.assertEqual(R >> render,
            '<p class="yht">'
                f'<sup><a class="yhi-lnk" id="p:{render.calcid("footnote")}" href="#q:{render.calcid("footnote")}">footnote</a></sup>'
                f'<a class="yhi-lnk" href="#s:{render.calcid("Paragraph")}">Paragraph</a>'
            '</p>')

    def test_i_autoemail(self):
        R = r'user@example.com' >> parse
        self.assertEqual(R[1], [1, [(2, 'mal', ('user', 'example.com'))]])
        self.assertEqual(R >> render,
            '<p class="yht">'
                '<span class="yhi-mal">'
                    '<span class="_b">moc</span>'
                    '<span class="_b">elpmaxe</span>'
                    '<span class="_a">resu</span>'
                '</span>'
            '</p>')

    def test_i_general(self):
        R =(r'&&& RAINSakura -> sakura',
            r''
            r'<<sakura.test arg1 arg2 = path? ? It is \\RAINSakura!\\>>'
        ) >> Parser({'RAINSakura': ((None, lambda x: x == 'test'), (None, lambda x: True), None)})
        self.assertEqual(R[1], [1, [(4, ('RAINSakura', 'test'), {'arg1': True, 'arg2': 'path?'}, ((0, 'It is '), (2, 'sla', ((0, 'RAINSakura!'),))))]])

    def test_template(self):
        custom_title = lambda x: ''.join(f'{ord(c):X}' for c in x)
        custom_css = '<link rel="stylesheet" href="rainink.css">'
        R = '' >> parse >> Renderer() >> Template(custom_title, custom_css)
        self.assertIn(custom_title(DEFAULT_TITLE), R)
        self.assertIn(custom_css, R)

main()