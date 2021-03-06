# 基于Flask的深度学习自动化部署系统
&emsp;&emsp;本软件为2020春季学期软件工程综合实验小组C组的实验项目，本软件旨在通过自动化部署深度模型，降低算法研究人员实际部署模型的门槛，提高深度学习模型迭代研发和部署的效率。 \
&emsp;&emsp;项目采用基于Python语言的轻量级Web框架Flask和容器技术作为实际的模型部署工具，自动化部署系统包括了网站前端页面，网站后端模块和模型部署模块。用户通过Web界面完成模型的上传和部署，并在随后通过Web界面获得访问该模型的REST API。在完成模型的部署之后，用户可在需要使用该模型的场景下调用此REST API，把待识别的图片发送至服务器，服务器将通过HTTP响应返回图片的识别结果。

## 项目部署地址
http://39.97.219.243:4998

## 快速使用指南
1. 访问系统：通过Firefox，Chrome，或Microsoft Edge浏览器访问项目地址；
2. 注册账号：点击右上角的注册按钮，注册一个新的账号；
3. 创建项目：登录账号，点击新建项目，输入项目信息，创建项目；
4. 上传神经网络模型文件：点击上传模型文件，选择一个已训练好的神经网络模型文件，若手头没有现成模型，可从***实验4：软件测试 - 测试样例及结果***文件夹下载模型样例；
5. 启动模型实例：点击启动模型实例按钮，获得访问该模型实例的REST API；
6. 发送待识别图片：通过postman等HTTP调试工具，向步骤5获得的REST API发送HTTP的POST请求，请参考***实验4：软件测试 - 测试样例及结果***文件夹里的结果截图，填写POST请求的data字段和key字段，其中data字段为待识别图片的灰度矩阵，key字段为步骤5获得的key字符串；
7. 获取识别结果：POST请求发送后，服务器将在稍后通过HTTP数据报返回识别结果，可以从HTTP调试工具中看到相应数据报。
\
\
Tips:\
&emsp;&emsp;关于***实验4：软件测试 - 测试样例及结果***的文件夹内容说明，请点击链接[测试所用的神经网络模型说明](实验4：软件测试/测试样例及结果/README.md)，或直接查看该文件夹的README.md。
\
&emsp;&emsp;由于服务器硬件简陋（我们只租得起便宜的学生服务器T^T），麻烦各位测试的同学不要同时启动多个模型实例，可暂停某个模型实例后再运行下一个，不然服务器内存不够用。如在测试过程中有遇到任何问题，请联系C组组长聂磊 :) 


## 小组成员
+ 崔昕宇
+ 李坤浩
+ 聂磊
+ 许京爽
+ 张利鹏
+ 张文斌
+ 张竹君
