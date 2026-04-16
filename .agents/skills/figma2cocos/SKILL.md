---
name: figma2cocos
description: 在用户提供CSS样式且包含 width / height / left / top 4个属性时使用figma2cocos技能
---

# 背景知识
figma中设计分辨率是w1080 h2340
figma中坐标都是以左上角为0,0
cocos中是以屏幕中心为0,0

一个例子
用户输入css 其实是某个figma节点的属性
width: 68;
height: 68;
top: 438px;
left: 968px;

这个节点在cocos中的计算是
x = left - 1080/2 + 68/2
y = 2340/2 - top - 68/2

# 按以下步骤完成任务
1.进行计算
x = 968 - 1080/2 + 68/2 = 968 - 540 + 34 = 462
y = 2340/2 - 438 - 68/2 = 1170 - 438 - 34 = 698

2.再次重算核对结果

3.给用户返回计算出的x和y的值

4.如果包含 font-size 属性,给用户返回加上 字体大小是xx

注意：其余属性忽视