# RAINLotus

> RAINLotus，雨荷。

* [English](README.md)

## What is RAINLotus?

1. 我所设计的一种新的标记语言。
2. 这个程序，用于将使用RAINLotus语法写作的文本转换为HTML。

## Why RAINLotus (markup language)?

> 有一天，我忽然发现Markdown、Asciidoc、reStructuredText……它们通通满足不了我！
>
> ……于是，RAINLotus就被我设计出来了。

* 😀简洁语法
* ✅任意扩展
* 🔄无限嵌套~~（禁 止 套 娃）~~
* 🎨丰富的内联标记
    * （最基本的）**粗体**、*斜体*、***粗斜体***、~~删除线~~、上标、下标、减淡（后三项无法在GFM当中体现）
    * 自带刮刮条！
    * 还有屏蔽条（“████”这种）
    * 插入图片、音频和视频（会考虑针对单个视频网站进行优化）
    * 链接、引用、脚注等
* 🎉丰富的预定义块标记
    * 各式各样的列表（无序、有序、Todos、定义列表）
    * 标记块和引语块（NOTE & QUOTE）
    * 支持CSV & JSON的表格（虽然现在单元格只能水平合并，但将来会想办法改进的）
    * 代码块、脚注、公式块、图表支持……
* ✨特色
    * 模仿聊天栏~~（中 门 对 狙）~~
    * 三色Todos列表（提供了**五种**有用的状态）
    * 丰富的“标记块”等级：TIP、NOTE、IMPORTANT、CAUTION、WARNING（像Asciidoc那样）
    * 自带折叠（使用`<details>`标签；将内容折叠起来以节省空间）

## How About RAINLotus (this script)?

* 🚀非常快
* 🧬仅生成核心内容，完整的HTML代码应由上层应用整合
    * 保证最小化的HTML代码
    * 在前端使用[mermaid](https://mermaidjs.github.io/)绘制图表
    * 在前端使用[mathjax](https://www.mathjax.org/)渲染公式
    * 在前端使用[prismjs](https://prismjs.com/)高亮代码（真的，pygments太慢了，它能够拖慢RAINLotus一半的速度）
* 🤔说是这么说；但是为了方便，还是提供了一个能够生成完整HTML的函数；附带JS和简单的CSS
    * （我CSS写的不好别捶我(ノДＴ)！）

---

***RAINLotus——不论是标记语言还是这个脚本，目前都正处于开发阶段。语法和API可能会有部分变更。***

## Let's start!

文档地址：<https://docs.20x48.net/RAINLotus>

## License

在`MIT`许可下发布，详见[License](https://github.com/20x48/RAINLotus/blob/master/LICENSE)