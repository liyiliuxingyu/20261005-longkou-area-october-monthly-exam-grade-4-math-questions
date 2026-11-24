# 逐题讲解动画PPT源码说明

成品为58页，覆盖原卷45个小题讲解单元，含158次单击、681项原生动画效果和5条运动路径。每次单击按步骤显示讲解。第20、37、38、39、40页含火车或三角板运动。折痕、画线、施工长度采用擦除等动画逐步显示。

## 文件与目录

保留本文件，以及：

- `build_deck.mjs`：当前最终版页面、几何图和动画清单构建器。
- `content.json`：已校正的58页正文及公式，内容以此文件为准。
- `render_formulas.py`：把公式以LaTeX编译为SVG。
- `formulas/*.svg`：现成的123幅公式矢量图，无需重跑LaTeX即可构建。
- `name_formula_images.py`：按源SVG精确字节比对补全公式图片对象名。
- `animate_pptx.py`：写入原生OOXML逐击、擦除、运动路径等动画。
- `fix_slide5_label_bounds.py`：最终边界修正，已同步到构建器，也可重复安全执行。
- `animation_plan.json`：最终58页动画清单，构建器会再生成同内容清单。
- `coverage.json`、`讲解目录.txt`：页面索引。

另保留同级项目根目录下 `deps/fandol/FandolHei-Regular.otf`、`FandolHei-Bold.otf`、`FandolKai-Regular.otf`。PPT正文使用Fandol楷体、标题使用Fandol黑体。用户在电脑上安装这三份字体可保持与预览一致的字形。

不需保留早期 `make_content.py`，它不是最终校正数据来源。公式子目录中的 `.aux/.log/.pdf/.tex` 为临时编译件，可不打包。`previews`、`.proto.json`及审核报告是内部验证材料。

## 构建依赖

构建器使用本次Codex运行环境提供的 `@oai/artifact-tool` 与 `@napi-rs/canvas`，并不保证在普通Node.js环境中直接运行。需要可解析这两个包的Node.js环境。Python脚本需要`lxml`。重新生成公式还需要TeX Live中的`pdflatex`、`standalone`、`amsmath`、`amssymb`、`xcolor`以及Poppler的`pdftocairo`。

项目目录应为：

```
项目根目录/
  ppt_work/本README及上述脚本、数据
  ppt_work/formulas/123份SVG
  deps/fandol/三份字体
  output/
```

`build_deck.mjs`和`render_formulas.py`已按脚本所在目录定位项目，不依赖本次工作区绝对路径。

## 构建顺序

从项目根目录执行。若SVG已保留，可跳过第一步。

```bash
python3 ppt_work/render_formulas.py
node ppt_work/build_deck.mjs
python3 ppt_work/name_formula_images.py ppt_work/draft.pptx ppt_work/content.json ppt_work/formulas ppt_work/named_draft.pptx
python3 ppt_work/animate_pptx.py ppt_work/named_draft.pptx ppt_work/animation_plan.json ppt_work/animated_candidate.pptx --report ppt_work/animation_injection_report.json
python3 ppt_work/fix_slide5_label_bounds.py ppt_work/animated_candidate.pptx ppt_work/corrected_candidate.pptx
```

`corrected_candidate.pptx`包含当前成品的正文、图形和动画，可另存为所需文件名。每次构建对象标识和ZIP元数据可能不同，因此不承诺文件哈希相同。

## 成品前的修复与核验

1. 所有公式按源SVG宽高等比例缩放，防止短公式横向拉长或长公式压窄。
2. 修复前题线条关系、路线折线、C选项等分标记、三角板平移目标、花苗原表及计分/模糊数据说明。
3. 图片对象命名时逐个核对PPTX内嵌SVG与本地源SVG完全一致，共123幅。
4. `bldP`只引用带有效文本的形状，图片与纯线条直接用`spTgt`动画；运动路径小数统一补前导零。
5. 第5页`a`标签文本框宽度由默认120px收为45px，修复无实际文字裁切但文本框超界的警告。这一修复已写入当前构建器，补丁脚本为幂等兼容步骤。
6. 最终成品通过包完整性、字体与几何布局检查，零问题、零警告。58页均作过全尺寸静态检查。
7. LibreOffice实际导入并转为ODP后，每页单击组和效果数量与清单逐项一致。最终PPTX重新统计为58页、158次单击、681项效果、5条运动路径，且其全部`p:timing`节点与导入核验候选完全一致。

未在桌面PowerPoint中实播检查。静态编辑画面或PDF预览会显示全部步骤；动画需进入幻灯片放映模式。
