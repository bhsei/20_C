from flask import render_template,request,Blueprint,jsonify,redirect
import flask_login
import datetime
import os
import yaml
import zipfile
from project.models.model import Model,Record
from project.services.model_service import getVersion,checkAdd,getFile,delete_model,findRecord,edit_param,get_model_detail_by_id
from project.services.record_service import get_record_detail_by_model
from project.models import db
model_bp = Blueprint('model', __name__, url_prefix='/model')
# 对项目模型的各种操作

ALLOWED_EXTENSIONS = set(['pb', 'h5', 'pt', 'py', 'zip'])

# 用于判断文件后缀，可调用
def allowed_file(file):
    return '.' in file and file.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@model_bp.route('/checkVersion/',methods=['GET', 'POST'])
def checkVersion():#检查版本
    if request.method == 'GET':
        return render_template('create_model.html', user=flask_login.current_user)
    res = {}
    try:
        pid = request.form['pid']
        name = request.form['name']

        if (len(pid) == 0 or len(name) == 0):
            res['code'] = '100x'
            res['msg'] = '参数数据缺失'
        else:
            version = getVersion(pid, name) + 1
            res['code'] = 1000
            res['msg'] = '查询成功'
            res['data'] = version
    except:
        res['code'] = '100x'
        res['msg'] = '服务器错误，请检查参数'
    return jsonify(res)

@model_bp.route('/addModel/', methods=['GET', 'POST'])#导入模型
def addModel():
    if request.method == 'GET':
        return render_template('create_model.html', user=flask_login.current_user)
    res = {}
    try:
        name = request.form['name']
        type = request.form['type']
        des = request.form['description']
        version = request.form['version']  # 需要再发一遍回来吧，确认用？
        f = request.files['file']
        pid = request.form['project_id']
        if (len(type) == 0 or len(name) == 0 or len(version)==0 or len(pid)==0):
            res['code'] = '100x'
            res['msg'] = '参数数据缺失'
        elif not f:
            res['code'] = '100x'
            res['msg'] = '文件丢失'
        elif not allowed_file(f.filename):
            res['code'] = '100x'
            res['msg'] = '文件格式错误'
        else:
            dt = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(name)

            file_dir = os.path.join(os.getcwd(), 'files/'+pid+'/'+name+'_'+version)  #files/5/model_1  （files/项目id/模型名称_版本号
            if not os.path.exists(file_dir):
                os.makedirs(file_dir)
            if f:
                file_path = os.path.join(file_dir, f.filename)  # filename是f的固有属性
                f.save(file_path)  # 保存到指定目录

                if f.filename.endswith('.zip'):# 如果是zip文件，解压,并获取文件夹路径（没有后缀名
                    print(f.filename.endswith('.zip'))

                    zip_file = zipfile.ZipFile(file_path)
                    zip_list = zip_file.namelist()  # 得到压缩包里所有文件

                    for f in zip_list:
                        zip_file.extract(f, file_dir)  # 循环解压文件到指定目录

                    zip_file.close()  # 关闭文件，必须有，释放内存
                    # 重新确定文件夹路径
                    (path, tempfilename) = os.path.split(file_path)
                    (filename, extension) = os.path.splitext(tempfilename)
                    print((filename, extension))
                    file_path = os.path.join(path, filename)
                    writeConfig(file_dir, file_path,type)
            #file_path多个文件是文件夹路径，单个文件就是该文件路径
            configFile = os.path.join(file_dir,'config.yml')
            fid = getFile(configFile,name)#还是存配置文件地址吧
            new_model = Model(project=pid, name=name, type=type, description=des,
                          version=version, file=fid, create_time=dt, update_time=dt,state=0)
            db.session.add(new_model)
            db.session.commit()
            flag = checkAdd(pid, name, version)
            if flag:
                res['code'] = 1000
                res['msg'] = '创建成功'
            else:
                res['code'] = 1004
                res['msg'] = '创建失败'
    except:
        res['code'] = '100x'
        res['msg'] = '服务器错误，请检查参数'
    return jsonify(res)


@model_bp.route('/deleteModel/', methods=['GET', 'POST'])#删除模型
def deleteModel():
    if request.method == 'GET':
        return render_template('create_model.html', user=flask_login.current_user)
    res = {}
    try:
        id = request.form['model_id']
        if (len(id) == 0):
            res['code'] = '100x'
            res['msg'] = '参数数据缺失'
        else:
            flag = delete_model(id)
            if flag:
                res['code'] = 1000
                res['msg'] = '删除成功'
            else:
                res['code'] = 1004
                res['msg'] = '删除失败'
    except:
        res['code'] = '100x'
        res['msg'] = '服务器错误，请检查参数'
    return jsonify(res)

@model_bp.route('/editParam/', methods=['GET', 'POST'])#设置参数
def editParam():
    if request.method == 'GET':
        return render_template('create_model.html', user=flask_login.current_user)
    res = {}
    try:
        id = request.form['model_id']
        RTenvironment = request.form['RTenvironment']
        cpu = request.form['cpu']
        memory = request.form['memory']
        if (len(id) == 0 or len(RTenvironment) ==0 or len(cpu)==0 or len(memory)==0):
            res['code'] = '100x'
            res['msg'] = '参数数据缺失'
        else:
            flag = findRecord(id)
            print(flag)
            if flag:   #已经有了，修改
                if edit_param(id,RTenvironment,cpu,memory):
                    res['code'] = '1000'
                    res['msg'] = '操作成功'
                else:
                    res['code'] = '1004'
                    res['msg'] = '修改失败'
            else:   #还没有，新增
                dt = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                new_Record = Record(model=id, RTenvironment=RTenvironment, cpu=cpu, url='/url',memory=memory,
                                   state = 0,load=0,create_time=dt)
                print(dt)
                db.session.add(new_Record)
                db.session.commit()
                if findRecord(id):
                    res['code'] = '1000'
                    res['msg'] = '操作成功'
                else:
                    res['code'] = '1004'
                    res['msg'] = '添加失败'
    except:
        res['code'] = '100x'
        res['msg'] = '服务器错误，请检查参数'
    return jsonify(res)


# 查看模型
@model_bp.route('/view/<model_id>', methods=['GET', 'POST'])
def viewModel(model_id):
    print(model_id)
    if not flask_login.current_user:
        return render_template('login.html',user=flask_login.current_user)
    list = get_model_detail_by_id(model_id)
    record = get_record_detail_by_model(model_id)
    info = {}
    basic={}
    deploy={}
    basic['name']=list['name']
    basic['type']=list['type']
    basic['version']=list['version']
    basic['file']=list['file']
    basic['description']=list['description']
    if record:
        deploy['env']= record.RTenvironment
        deploy['cpu']=record.cpu
        deploy['mem']=record.memory
        deploy['url']=record.url
        deploy['state']=record.state
    else:
        deploy['env']=''
        deploy['cpu']=''
        deploy['mem']=''
        deploy['url']=''
        deploy['state']=0
    info['basic']=basic
    info['deploy']=deploy
    print(info)
    return render_template('model.html', user=flask_login.current_user, model_info=info)

'''
@model_bp.route('/upFile/', methods=['GET', 'POST'])#测试文件上传和路径,生成配置文件
def upFile():
    f = request.files['file']
    name = request.form['name']
    version  = request.form['version']
    pid = request.form['pid']
    type = request.form['type']

    file_dir = os.path.join(os.getcwd(), 'files/' + pid + '/' + name + '_' + version)

    if not os.path.exists(file_dir):
        os.makedirs(file_dir)
    if f:
        file_path = os.path.join(file_dir, f.filename)  # filename是f的固有属性
        f.save(file_path)  # 保存到指定目录
        print(f.filename)
        print(file_path)
        print(allowed_file(f.filename))
        print(f.filename.endswith('.txt'))
        if(f.filename.endswith('.zip')):
            zip_file = zipfile.ZipFile(file_path)
            zip_list = zip_file.namelist()  # 得到压缩包里所有文件

            for f in zip_list:
                zip_file.extract(f, file_dir)  # 循环解压文件到指定目录

            zip_file.close()  # 关闭文件，必须有，释放内存
            (filepath, tempfilename) = os.path.split(file_path)
            print(file_path)
            (filename, extension) = os.path.splitext(tempfilename)
            print((filename, extension))
            file_path = os.path.join(filepath, filename)
        print(file_path)
        writeConfig(file_dir,file_path,type)
    res = {}
    return res
'''
def writeConfig(file_dir,file_path,type):  #file_dir是保存到的文件地址(到模型名_版本号，file_path多个文件到文件夹，无后缀名，单个文件到文件，有后缀名

    #file_path两个单文件类型可以直接存，有文件夹的还需要再找
    #file_dir+config.yml是配置文件所在路径
    yaml_path = os.path.join(file_dir, 'config.yml')
    if type =='H5' or type == 'PB':#无文件夹
        data = {
            'CURRENT_MODEL_TYPE': type,
            type : {'model_path': file_path}
        }
    elif type == 'TXT':  # 找.txt
        # 此时file_path是文件夹
        model_graph_file_path = ''
        for file in os.listdir(file_path):
            if os.path.splitext(file)[1] == '.txt':
                model_graph_file_path = os.path.join(file_path,file)

        data = {
            'CURRENT_MODEL_TYPE': type,
            type: {'model_path': file_path, 'model_graph_file_path': model_graph_file_path}
        }
    elif type == 'CPKT':#找.meta
        #此时file_path是文件夹
        model_graph_file_path = ''
        for file in os.listdir(file_path):
            if os.path.splitext(file)[1] == '.meta':
                model_graph_file_path = os.path.join(file_path,file)
        data = {
            'CURRENT_MODEL_TYPE': type,
            type: {'model_path': file_path,'model_graph_file_path':model_graph_file_path}
        }
    else:#TORCH 找 .pt .py文件
        model_path = ''
        model_graph_file_path = ''
        for file in os.listdir(file_path):
            if os.path.splitext(file)[1] == '.pt':
                model_path = os.path.join(file_path,file)
        for file in os.listdir(file_path):
            if os.path.splitext(file)[1] == '.py':
                model_graph_file_path = os.path.join(file_path,file)
        data = {
            'CURRENT_MODEL_TYPE': type,
            type: {'model_path': model_path, 'model_graph_file_path': model_graph_file_path}
        }
    # 写入到yaml文件
    with open(yaml_path, "w", encoding="utf-8") as f:
        yaml.dump(data, f)
        f = open(yaml_path)
        x = yaml.load(f)
        print(x)



