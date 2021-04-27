"""
The parser & renderer of RAINLotus markup language.
Github: https://github.com/20x48/RAINLotus

================================================================================

MIT License

Copyright (c) 2020-2021 20x48

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
# 不要责怪我言简意赅的包命名，要怪就怪Python的包管理`taste like shit`好了。

# 好，我现在是他妈彻底被恶心到了。怎么会有这么傻逼的东西？？
# 前面不加点，调用已安装的分发包时会逼逼ModuleNotFound；
# 前面加点，开发的时候又他妈告诉我ImportError。

# 于是乎，妙哉，StackOverflow告诉了我这个好东西。
try:
    from .p import Parser
    from .r import RendererCore, Renderer, Template
    from .v import __version__
except ImportError:
    from p import Parser
    from r import RendererCore, Renderer, Template
    from v import __version__

# 真的是他妈的脑淤血，我要是再用Python“开发轮子”，我就不做人了。
__author__ = '20x48'