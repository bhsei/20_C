- 部署模块入口为：`instance_impl.py`文件

- `instance`文件夹放置实例运行文件夹，命名方式为

  `program_$program_id$_$timestamp$`   timestamp为实例创建的时间戳

- `model_file`文件夹内存放模型文件

- `model_template`文件夹内存放各类模型的模板

- `config.yml`配置文件与项目对应，内有项目模型的类型及相关参数信息

- `h5_输入样例.txt`文件为MNIST数据集下的模型的输入样例（对应数字7）
