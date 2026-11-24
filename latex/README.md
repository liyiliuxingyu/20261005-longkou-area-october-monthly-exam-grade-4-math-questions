# 四年级数学第二学段核心素养检测：高清重排工程

## 文件

- `questions.tex`：试题版入口，首行为 `\documentclass{examcn}`，成品为7页A4。
- `answers.tex`：答案版入口，首行为 `\documentclass[answers]{examcn}`，成品为11页A4。
- `paper.tex`：共用题目和红色答案；答案均写在对应题目下方，应用题给出脱式计算和有意义的不同思路。
- `front_figures.tex`、`back_figures.tex`：所有图形的TikZ矢量源代码。
- `examcn.cls`：本项目自带的中文试卷类，基于 `exam` 类和 `xeCJK`，**并非声称来自某个官方同名发行版**。
- `fonts/`：Fandol宋体、黑体、楷体原始字体及许可。字体未修改，许可见`fonts/COPYING`。
- `xeCJK*.sty`、`xeCJK.cfg`、`xunicode-*`、`ctexhook.sty`、`ctexpatch.sty`：TeX Live 2023最终归档中的兼容依赖，保留原版权说明及LPPL许可。此处xeCJK版本3.9.1、CTEX钩子版本2.5.10，未修改文件内容。

## 编译

安装TeX Live或MiKTeX，使用XeLaTeX，不要使用pdfLaTeX。需有基础LaTeX、`exam`、`fontspec`、`amsmath`、`tikz`、`geometry`、`enumitem`、`needspace`等通常包含于TeX Live的组件。工程已经附带所用中文字体和兼容的中文支持文件，无需在线下载字体。

在此目录执行：

```bash
xelatex -interaction=nonstopmode -halt-on-error questions.tex
xelatex -interaction=nonstopmode -halt-on-error questions.tex
xelatex -interaction=nonstopmode -halt-on-error answers.tex
xelatex -interaction=nonstopmode -halt-on-error answers.tex
```

重复编译用于更新总页数。也可执行`build.sh`。字体路径为相对路径`fonts/`，请不要只复制入口文件。

## 题源与校勘

题源为用户提供的两张照片，含原试卷四页。已重新录入文字、公式和图形；没有把低清照片铺作PDF背景。

1. 口算原卷标“每题1分，共7分”，但实际有8道；第三大题标“共25分”也与8+18不一致。所有题目完整保留，未擅自更改原分值。
2. 花苗表丁香单价暂读38元，仍有可能为36元。表格用`38†`注明。主解得3958元；如果丁香36元，则得3600元。应以清晰原卷核实这一数字。
3. 作图第2题要求量距，但照片无法恢复原纸厘米比例。本重排图设垂线段AH长2厘米；请按100%原尺寸打印，不选“适应页面”。这是本重排版的距离，不是声称原卷就是2厘米。
4. 隧道题“高铁”二字低清，也可能为“高速”，不影响数学条件。
5. 选择第1题的`29+15`上方有横括线，必须保留。历史介绍依原题转录，未作史料核验。
6. 选择第4题按小学常见对称轴对折理解。选择第7题按图形直接呈现的数量关系选D；C也可间接推出单价再相乘，因此原题“能用”措辞不够严密。附加第2题按沿原路返回的通常题意解答。

## 检查

- 全部计算数值经过独立核验。
- 试题版7页、答案版11页，页码完整。
- 最新编译日志无Overfull框、无Missing character。
- 所有图形为TikZ矢量；两版均已逐页渲染检查，避免文字、公式、线条重叠。
