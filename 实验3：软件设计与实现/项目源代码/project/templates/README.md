根模板-root.html

    |__门户主页-home.html
    |__账户管理
    |   |__登陆页-login.html：用户登陆
    |   |__注册页-regist.html：用户注册
    |   |__注册成功页-share.html：注册成功后反馈页面
    |__主模板-template.html（该模板右上角提供：用户登出）
        |__项目管理
        |   |__项目列表页-index.html：更新项目、删除项目
        |   |__新建项目页-create_project.html：新建项目
        |   |__项目查看页-project.html：查看项目、查看某一项目下所有模型、删除模型
        |__模型管理
        |   |__导入模型页-create_model.html：在项目中导入模型
        |   |__模型部署参数设置页-model_parm.html：对模型部署的参数进行设置
        |__实例管理
            |__模型查看页-model.html：查看模型、启动实例、暂停实例、恢复实例、删除实例