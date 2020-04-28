# RAINLotus

> RAINLotus，雨荷。

* [简体中文](https://github.com/20x48/RAINLotus/blob/master/README_zh.md)

## What is RAINLotus?

1. A new markup language I designed.
2. This program, used to convert text written using RAINLotus to HTML.

## Why RAINLotus (markup language)?

> One day, I suddenly found that Markdown, Asciidoc, reStructuredText ... they can't satisfy me!
>
> ... So, RAINLotus was designed by me.

* 😀Concise grammar
* ✅Expand easily
* 🔄Infinite nesting
* 🎨Rich inline markup (named "symbol")
    * (the most basic) **Bold**, *Italic*, ***Bold Italic***, ~~Strike~~, Superscript, Subscript, Dim (the last three items cannot be reflected in GFM)
    * comes with "刮刮条" (a piece of text with the same foreground and background, move the mouse over it will display the original content. Just call it "shady")
    * there is also "shield" (like "████")
    * insert pictures, audio and video (will consider optimization for a single video website)
    * links, refers, footnotes, etc.
* 🎉Rich predefined block marks (named "marks")
    * Various lists (unordered, ordered, Todos, definition list)
    * Note & quote
    * Supports CSV & JSON tables (although the cells can only be merged horizontally now, I will try to improve them in the future)
    * Code, footnote, formula, diagram...
* ✨Features
    * Imitating the chat
    * Three-color Todos list (provides **five** useful states)
    * Abundant levels of "note": TIP, NOTE, IMPORTANT, CAUTION, WARNING (Asciidoc like)
    * comes with folding (use the `<details>` tag; fold the content to save space)

## How About RAINLotus (this script)?

* 🚀 Ultra fast
* 🧬 Only the core content is generated, the complete HTML code will be integrated by the upper application
    * HTML code guaranteed to be minimized
    * Use [mermaid](https://mermaidjs.github.io/) to draw diagrams at the front end
    * Use [mathjax](https://www.mathjax.org/) rendering formula at the front end
    * Use [prismjs](https://prismjs.com/) highlighting code at the front end (really, pygments are too slow, it can slow down half of RAINLotus)
* 🤔 Despite this, but for convenience, a function that can generate complete HTML is provided; with JS and simple CSS
    * (My ugly CSS! Don't blame me(ノДＴ)!)

---

***RAINLotus -- Whether markup language or this script, it is currently in the development stage. The syntax and API may be partially changed.***

## Let's start!

Documentation: <https://docs.20x48.net/RAINLotus>

## License

Follow `MIT`, see [License](https://github.com/20x48/RAINLotus/blob/master/LICENSE) for details