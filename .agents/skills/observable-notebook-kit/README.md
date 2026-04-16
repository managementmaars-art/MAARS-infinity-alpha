# How to generate this skill

* https://github.com/observablehq/notebook-kit @ c199ce8
* build docs
* convert all generated docs from html to md, by pandoc
  * `pandoc -o ?.md ?`
* copy *.md to docs/md
* use opencode with below text
* done 🪄

```text
当前目录下，是observeable notebook kit 的说明文档，根目录中有一些 *.html 是文档主要部分，可适当读取一些作为参考（不要读取太多）。
另外，md/ 目录下是这些 html 文档经过 notebook kit 渲染之后生成的静态html，通过pandoc转换成md的结果文件。

请主要根据这些md/文件（notebook kit主要文档），来生成一个agent skill，存放到 ./skill 目录。skill创建方式见 skill-creator。

注意：*.html 是notebook kit格式，并不是真正的html，可以适当读取一些当作参考。不用读取太多。
注意2: 因为md/ 文档是生成+提取的，在生成skill时，请做清理和简化，使得llm能看懂又清晰为善。
```
