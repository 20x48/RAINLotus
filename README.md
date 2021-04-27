# RAINLotus

<details>
<summary>What would it look like if this page were written in RAINLotus.</summary>

    RAINLotus
    =========

    &&& RAINLotus
        alias
            rl  RAINLotus
            why Why am I designed this?

    A //tranquilac// lightweight markup language with nearly 40 syntaxes.
    The only reason I developed her is because I like her.
    I do not want to replace anyone.
    But she seems to have some advantages that other languages ​​do not.

    == For Writers

    1. Ignore all blank lines (even if padding with non-printable ASCII characters).

    2. Here are only `block`, `paragraph` and `inline`.

    3. Keep all line breaks: each non-blank line (if not recognized as a `block`) is treated as a `paragraph`.

        This means you cannot "one line per 80 characters width" anymore. Please let the editor help you wrap the lines automatically.

        ~~~ {why}
            For an OCD (this word has different meanings in Chinese pop culture), since I have the determination to "maintain 80 characters width"... When the paragraph starts to be a bit long, after some additions, deletions and changes, I believe that it will not take too short to maintain this rule manually.
            If you say "let the editor solve this problem": automatic line wrapping is available even on the wrost `notepad.exe`.
            If you say "control paragraph length": if the paragraph is short enough, no one wants to wrap; which monitor does not have a width of hundreds of characters now?
            Resolutely do NOT change this design.

    4. `inline` will only appear in `paragraph`.

    5. Use indentation to control text nesting structure. Per **4 spaces** as an indentation level, cannot be changed.

        ~~~ {why}
            I thought I might repeat the mistake of YAML (its complex indentation formatting); but after a few seconds, I no longer worry about this problem:
            For other languages that cannot be nested, don't you still use them well?

    6. A `block` always starts with `prefix`.

        1. `text` after `prefix` is usually `arguments`, sometimes belong to `content`.

        2. At least **1 space** between `prefix` and `text`.

        3. After this line, *look down* and find all lines whose (indentation) level: greater than this level (until it less than or equal to this level); they all belong to this `block`'s `content`.

    7. //She has a birthday, it is `1557417600`.//

    == For Programmers

    (Python version requirement: `>=3.6`; Module requirement: None)

    === Module

    ``` python
        from RAINLotus import Parser, Renderer, Template

        parser = Parser()
        renderer = Renderer()
        template = Template(custom_title=lambda x: x + ' ~ 20x48.net', custom_css='<link rel="stylesheet" href="rainink.css">')

        with open('output.html', 'w', encoding='utf-8') as f:
            f.write(
                (
                    'Hello World!',
                    '============',
                    '',
                    '...'
                ) >> parser >> renderer >> template
            )   # Yes, I overloaded their right shift operator, so they look like C++ `<iostream>` ;P

    Here are `Parser`, `RendererCore`, `Renderer` and `Template`.

    A `Parser` uses to parse text written in {rl} to Python basic object.

    A `Renderer???` uses to render "basic object" to HTML. Their difference:

    .. `RendererCore`: Render only `<body>`, return a `str`. Rarely use.
    .. `Renderer`: Call `RendererCore`, get `<body>` then render `<head>`, return a `dict`.

    A `Template` uses to combine a `dict` from `Renderer` to a complete HTML with embedded JS (non-removable) and/or CSS (customable) and customable title (via lambda).

    === CLI

    ``` shell
        $> python -m RAINLotus --help

        usage: RAINLotus [-h] [-o OUTPUT] [-e ENCODING] [-j] [-O] [-q] [-V] INPUT [INPUT ...]

        positional arguments:
          INPUT                 File(s) to process; "-" means read from STDIN.

        optional arguments:
          -h, --help            show this help message and exit
          -o OUTPUT, --output OUTPUT
                                Path to save processed file(s); "-" means write to STDOUT.
                                If multiple input files are specified, this must be a directory.
                                If the directory not existing, program will create one.
          -e ENCODING, --encoding ENCODING
                                Specify the encoding of READING file(s). [Default: "utf-8"]
                                CANNOT specify the encoding of WRITING file(s), because utf-8 can solve all problems.
          -j, --parse-only      Output JSON instead of HTML. [Default: False]
          -O, --overwrite       If file already exists, whether to overwrite it. [Default: False]
          -q, --quiet           Disable terminal information output. [Default: False]
          -V, --version         Show version info then exit.

    == License

    Licensed under [MIT]<./LICENSE>.

</details>

A *tranquilac* lightweight markup language with nearly 40 syntaxes.

The only reason I developed her is because I like her.

I do not want to replace anyone.

But she seems to have some advantages that other languages ​​do not.

## For Writers

1. Ignore all blank lines (even if padding with non-printable ASCII characters).

2. Here are only `block`, `paragraph` and `inline`.

3. Keep all line breaks: each non-blank line (if not recognized as a `block`) is treated as a `paragraph`.

    This means you cannot "one line per 80 characters width" anymore. Please let the editor help you wrap the lines automatically.

    <details>
    <summary>Why am I designed this?</summary>

    > For an OCD (this word has different meanings in Chinese pop culture), since I have the determination to "maintain 80 characters width"... When the paragraph starts to be a bit long, after some additions, deletions and changes, I believe that it will not take too short to maintain this rule manually.
    >
    > If you say "let the editor solve this problem": automatic line wrapping is available even on the wrost `notepad.exe`.
    >
    > If you say "control paragraph length": if the paragraph is short enough, no one wants to wrap; which monitor does not have a width of hundreds of characters now?
    Resolutely do NOT change this design.
    </details>

4. `inline` will only appear in `paragraph`.

5. Use indentation to control text nesting structure. Per **4 spaces** as an indentation level, cannot be changed.

    <details>
    <summary>Why am I designed this?</summary>

    > I thought I might repeat the mistake of YAML (its complex indentation formatting); but after a few seconds, I no longer worry about this problem:
    >
    > For other languages that cannot be nested, don't you still use them well?
    </details>

6. A `block` always starts with `prefix`.

    1. `text` after `prefix` is usually `arguments`, sometimes belong to `content`.

    2. At least **1 space** between `prefix` and `text`.

    3. After this line, *look down* and find all lines whose (indentation) level: greater than this level (until it less than or equal to this level); they all belong to this `block`'s `content`.

7. *She has a birthday, it is `1557417600`.*

## For Programmers

(Python version requirement: `>=3.6`; Module requirement: None)

### Module

``` python
from RAINLotus import Parser, Renderer, Template

parser = Parser()
renderer = Renderer()
template = Template(custom_title=lambda x: x + ' ~ 20x48.net', custom_css='<link rel="stylesheet" href="rainink.css">')

with open('output.html', 'w', encoding='utf-8') as f:
    f.write(
        (
            'Hello World!',
            '============',
            '',
            '...'
        ) >> parser >> renderer >> template
    )   # Yes, I overloaded their right shift operator, so they look like C++ `<iostream>` ;P
```

Here are `Parser`, `RendererCore`, `Renderer` and `Template`.

A `Parser` uses to parse text written in {rl} to Python basic object.

A `Renderer???` uses to render "basic object" to HTML. Their difference:

- `RendererCore`: Render only `<body>`, return a `str`. Rarely use.
- `Renderer`: Call `RendererCore`, get `<body>` then render `<head>`, return a `dict`.

A `Template` uses to combine a `dict` from `Renderer` to a complete HTML with embedded JS (non-removable) and/or CSS (customable) and customable title (via lambda).

### CLI

``` shell
$> python -m RAINLotus --help

usage: RAINLotus [-h] [-o OUTPUT] [-e ENCODING] [-j] [-O] [-q] [-V] INPUT [INPUT ...]

positional arguments:
  INPUT                 File(s) to process; "-" means read from STDIN.

optional arguments:
  -h, --help            show this help message and exit
  -o OUTPUT, --output OUTPUT
                        Path to save processed file(s); "-" means write to STDOUT.
                        If multiple input files are specified, this must be a directory.
                        If the directory not existing, program will create one.
  -e ENCODING, --encoding ENCODING
                        Specify the encoding of READING file(s). [Default: "utf-8"]
                        CANNOT specify the encoding of WRITING file(s), because utf-8 can solve all problems.
  -j, --parse-only      Output JSON instead of HTML. [Default: False]
  -O, --overwrite       If file already exists, whether to overwrite it. [Default: False]
  -q, --quiet           Disable terminal information output. [Default: False]
  -V, --version         Show version info then exit.
```

## License

Licensed under [MIT](./LICENSE).