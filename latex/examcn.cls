\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{examcn}[2026/10/26 Local Chinese examination class for this project]
% This is a project-local class; it is not presented as an official CTAN examcn release.
\newif\ifanswers
\DeclareOption{answers}{\answerstrue}
\DeclareOption*{\PassOptionsToClass{\CurrentOption}{exam}}
\ProcessOptions\relax
\LoadClass[12pt,a4paper]{exam}
\RequirePackage{fontspec}
\RequirePackage{xeCJK}
\setmainfont{Latin Modern Roman}
\setsansfont{Latin Modern Sans}
\setCJKmainfont[Path=fonts/,BoldFont=FandolSong-Bold.otf]{FandolSong-Regular.otf}
\setCJKsansfont[Path=fonts/,BoldFont=FandolHei-Bold.otf]{FandolHei-Regular.otf}
\setCJKmonofont[Path=fonts/]{FandolKai-Regular.otf}
\RequirePackage{amsmath,amssymb,mathtools}
\RequirePackage[margin=17mm,headheight=15pt,headsep=7mm,footskip=9mm]{geometry}
\RequirePackage{tikz}
\usetikzlibrary{calc,angles,quotes,arrows.meta,positioning,decorations.pathreplacing}
\RequirePackage{xcolor,array,booktabs,multicol,enumitem,needspace}
\definecolor{answerred}{HTML}{C21F30}
\definecolor{notegrey}{gray}{0.33}
\setlength{\parindent}{0pt}
\setlength{\parskip}{3pt}
\linespread{1.18}
\pagestyle{headandfoot}
\firstpageheader{}{}{}
\runningheader{\small 四年级数学第二学段核心素养检测}{}{\small\ifanswers 答案版\else 试题版\fi}
\runningheadrule
\footer{}{\small 第\thepage 页，共\numpages 页}{}
\newcommand{\blank}[1][2.0cm]{\underline{\makebox[#1]{}}}
\newcommand{\Ans}[1]{\ifanswers{\color{answerred}#1}\else\phantom{#1}\fi}
\newcommand{\Q}[2]{\par\needspace{3\baselineskip}\noindent\textbf{#1.}\quad #2\par}
\newcommand{\Sol}[1]{\ifanswers\par\begingroup\color{answerred}\small #1\par\endgroup\fi}
\newcommand{\Work}[1]{\ifanswers\else\vspace{#1}\fi}
\newcommand{\Sect}[1]{\par\needspace{4\baselineskip}\vspace{3pt}{\large\sffamily\bfseries #1}\par\vspace{3pt}}
\newcommand{\Title}{\begin{center}{\sffamily\bfseries\fontsize{16}{21}\selectfont 2026--2027学年度第一学期\\四年级数学第二学段核心素养检测}\par\vspace{3pt}{\large\ifanswers 答案版\else 试题版\fi}\end{center}\ifanswers\else 班级：\blank[3cm]\hfill 姓名：\blank[3cm]\hfill 学号：\blank[3cm]\par\fi}
\endinput
