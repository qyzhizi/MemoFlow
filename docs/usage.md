## 使用方法
以本地启动为例，启动服务后，访问：`http://localhost:6060/v1/diary-log`
，可得到页面:

Desktop web client             |  Mobile web client
:-------------------------:|:-------------------------:
![](https://qyzhizi.cn/img/202405071900184.png)  |  ![](https://qyzhizi.cn/img/202405071900655.png)

相同的卡片笔记在 Logseq(或Obsidian) 显示的内容：

Logseq 显示的卡片笔记内容|Obsidian 显示的卡片笔记内容
:-------------------------:|:-------------------------:
![](https://qyzhizi.cn/img/202405071911371.png)  |  ![](https://qyzhizi.cn/img/202405071915390.png)

本项目的网页客户端的输入框保留空格、换行符和其他空白字符，支持tab与shift+tab 缩进。当你提交输入的内容后，后台会自动添加时间戳标题，后台使用字符串匹配来识别卡片笔记的标签、子块与todo等功能。

另外数据会在数据库sqlite中保留一份，然后通过异步方式向远程同步文件发送一份（插入到文件最上面），由于采用异步发送方式，所以感受不到延迟。@todo 考虑后台发送任务失败时，给出页面提示。

## 卡片笔记示例
记录卡片笔记，可以围绕一个问题(#que 标记)来进行：
当你在输入框输入：
```
#key1 #key2
#que 如何使用一个简单的自定义规则实现卡片笔记
#ans
就像这样, 这是一个例子
--todo 代办事项1
--todo 代办事项2
```

在线页面与远程同步文件中内容：
```
- ## 2023/5/16 08:36:48:
	- #key1 #key2
	  #que 如何使用一个简单的自定义规则实现卡片笔记
	- #ans
	  就像这样, 这是一个例子
	- TODO 代办事项1
	- TODO 代办事项2      
```
最终在logseq本地markdown 渲染效果是：

<img src="https://qyzhizi.cn/img/202307201143114.png" width="60%" height="60%">

## 规则解释
```
#key1 表示关键字标签 
#que 表示问题标签
#ans 表示答案标签
关键字与问题在一个子块，块（block）是logseq中的核心概念，表示一个段落
答案单独作为一个子块
--todo 表示代办事项
```