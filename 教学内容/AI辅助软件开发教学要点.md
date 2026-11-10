# 一、工作环境准备

## 1. 安装opencode及相关插件

- 以opencode为例演示AI工具参与软件开发。也可以使用其他AI工具（Trae, WorkBuddy, ChatGPT等）。

- 首先安装opencode CLI，这是一个基于命令行的AI工具。

opencode安装好之后首先需要连接大语言模型，opencode提供了许多免费的大语言模型：

![](D:\workspace\softengineering\教学内容\images\免费的大语言模型.png)

- opencode自带了2个智能体（Agent）：build和plain，为了能提高Agent的工作效率，编排任务的执行，我们需要安装一个插件omo-slim（在opencode 1.x的版本中，插件是oh-my-opencode；在opencode2.x的版本中使用omo-slim）。omo-slim完整的Agent团队包括7个SubAgent：

  - **Orchestrator**（编排器）：主 Agent，负责规划任务、调度和协调其他专家。
  - **Explorer**（探索者）：子 Agent，负责侦察代码库。
  - **Oracle**（先知）：子 Agent，负责查询最新文档或进行深度分析。
  - **Council**（议会）：子 Agent，可以并行运行多个模型来对比答案。
  - **Librarian**（图书管理员）：子 Agent，负责检索信息。
  - **Designer**（设计师）：子 Agent，负责处理 UI 相关的工作。
  - **Fixer**（修复者）：子 Agent，负责执行具体的代码修改任务。

- 成功安装omo-slim后，在opencode命令行中调用/agents，可以看到：

  ![](D:\workspace\softengineering\教学内容\images\agents.png)

  默认情况下，使用orchestrator主Agent，由它自主调度其它的SubAgents。

- 然后安装一下其他你觉得需要的插件和技能。为了本课程的进行，需要2个必备的插件：draw.io和nt。

draw.io插件用于绘制软件工程中各种模型图；nt用于蒸馏知识。

### 1.1 安装omo-slim
在opencode命令行输入：
```prompt
安装omo-slim插件
```

### 1.2 安装draw.io插件
在opencode命令行输入：
```prompt
安装draw.io插件
```

### 1. 3 安装蒸馏插件“nt"

### 方式一

- 从 https://githhub.com/navbytes/nt/releases/tag/v0.31.0 下载 nt

- 为opencode安装nt插件，在命令行运行：

  ```prompt
  nt opencode install
  ```


### 方式二

在opencode的命令行里输入

```prompt
安装蒸馏插件“nt”
```

备注：其实，所有的插件和技能都可以直接在opencode命令行里提要求，由AI自动安装。优点是省心，缺点是耗Token

## 2. 蒸馏知识库

准备好要蒸馏的资料到一个文件夹下如“资料库"

```prompt
我要蒸馏文件夹 @资料库\ 下的所有文档资料，告诉我如何做的步骤，待我确认后再执行。
```

AI会向你确认，如：

![image-20261103134156150](D:\workspace\softengineering\教学内容\images\image-20261103134156150.png)

![](D:\workspace\softengineering\教学内容\images\fig2.png)

# 二、 AI辅助软件建模

## 1. 创建技能
提示词：

```prompt
根据知识库创建uml建模的技能"uml-modeling"，使得能根据需求分析创建用例图和用例文档，然后根据用例图和用例文档创建对象图、类图、时序图、协作图、活动图、状态图、实体关系图等模型。如果这个技能你觉得太大，你可以分别为每个模型创建一个技能，技能命名的规则是在"uml-modeling"后加上模型的名字。
```

## 2. 案例演示
### 2.1 从需求文档到用例模型
```prompt
用uml-modeling为下面的需求创建用例模型；开发一个博客系统，其中有一项功能：浏览帖子，具体描述如下：对于会员和未注册游客，均拥有根据帖子标题进行检索，阅读帖子的详细内容的功能，帖子的详细内容包括标题、内容、作者、发表时间、评论信息等；系统在展示帖子的评论信息时按每页20条信息展示，可前后翻页查看；浏览帖子时，可以对帖子进行回复信息，系统自动判定用户是否已经登录，已登录的会员可回复帖子，否则系统提示先登录才能回复帖子。调用draw.io绘制出用例图。
```
输出的结果：![](D:\workspace\softengineering\教学内容\images\fig3.png)
```prompt
在用例图中，你把"阅读帖子详细内容"与"浏览评论"两个用例之间的关系建模为"include",我认为应该是"extend"，你怎么看？
```

AI回答：

![image-20261104093650593](C:\Users\lwz\AppData\Roaming\Typora\typora-user-images\image-20261104093650593.png)

<img src="D:\workspace\softengineering\教学内容\images\fig5.png" style="zoom:200%;" />

```prompt
我觉得"回复帖子"与"阅读帖子详细内容"之间的关系是”extend,你如何评判？
```

![](D:\workspace\softengineering\教学内容\images\fig6.png)

```prompt
选A
```

![](D:\workspace\softengineering\教学内容\images\fig7.png)

```prompt
为前面生成的用例图编写用例规格说明
```

### 2.2用时序图实现用例模型

```prompt
针对需求已经建立用例模型和用例规格说明，见 @uml/01-usecase.drawio 和 @uml/02-usecase-specs.md .你运用 @uml-modeling 技能对每个用例使用时序图实现，每个时序图使用 @drawio 技能绘制，输出时序图文件命名规则"用例名称-sequence.drawio".
```

```prompt
在这些时序图中，"alt"似乎可以在表示分支和循环时都是相同的，我认为在知识库中"ECP"这个示例中时序图表示分支和循环的方式更好，你是否认同我的观点，你不需要讨好我，以客观的态度评价。
```

```prompt
我阅读了模型的时序图，在uml目录下所有形式如"*-sequence.drawio"的文件。我发现在时序图中，建立了控制器对象，那是不是可以认为此时已经默认系统将使用MVC模式，这在系统分析阶段合适吗？这一阶段主要是分析系统的类和对象模型，还不涉及实现架构吧？你对此如何评价？你只做评述，不修改已有文件，你要保持客观的立场作出评述。
```

### 2.3 软件分析与设计

具体与AI交互的提示词和AI输出见文件 “AI辅助软件分析与设计案例.md”





