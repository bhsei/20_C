from flask import render_template,request,Blueprint,jsonify,redirect
import flask_login
import datetime
import os
import yaml
import ruamel.yaml
import zipfile
from project.models.model import Model,Record
from project.services.model_service import getVersion,checkAdd,getFile,delete_model,findRecord,edit_param,get_model_detail_by_id,get_model_type,get_config_file_path
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
    res = {}
    try:
        print('ccccccccc')
        pid = request.form.get('pid')
        name = request.form.get('name')
        print(pid)
        print(name)
        if (len(pid) == 0 or len(name) == 0):
            res['code'] = 1005
            res['msg'] = '参数数据缺失'
        else:
            version = getVersion(pid, name) + 1
            res['code'] = 1000
            res['msg'] = '查询成功'
            res['data'] = version
    except:
        res['code'] = 2000
        res['msg'] = '服务器错误，请检查参数'
    return jsonify(res)

@model_bp.route('/addModel/<pid>', methods=['GET', 'POST'])#导入模型
def addModel(pid):
    if request.method == 'GET':
        return render_template('create_model.html', user=flask_login.current_user)
    res = {}
    try:
        name = request.form['name']
        type = request.form['type']
        des = request.form['description']
        version = request.form['version']  # 需要再发一遍回来吧，确认用？
        f = request.files['file']
        if (len(type) == 0 or len(name) == 0 or len(version) == 0 or len(pid) == 0):
            res['code'] = 1005
            res['msg'] = '参数数据缺失'
        elif not f:
            res['code'] = 2016
            res['msg'] = '文件丢失'
        elif not allowed_file(f.filename):
            res['code'] = 2017
            res['msg'] = '文件格式错误'
        else:
            dt = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(name)

            file_dir = os.path.join(os.getcwd(),
                                    'files/' + pid + '/' + name + '_' + version)  # files/5/model_1  （files/项目id/模型名称_版本号
            if not os.path.exists(file_dir):
                os.makedirs(file_dir)
            if f:
                file_path = os.path.join(file_dir, f.filename)  # filename是f的固有属性
                f.save(file_path)  # 保存到指定目录

                if f.filename.endswith('.zip'):  # 如果是zip文件，解压,并获取文件夹路径（没有后缀名
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
                writeConfig(file_dir, file_path, type)
            # file_path多个文件是文件夹路径，单个文件就是该文件路径
            configFile = os.path.join(file_dir, 'config.yml')
            fid = getFile(configFile, name)  # 还是存配置文件地址吧
            print(fid)
            print(pid)
            new_model = Model(project=pid, name=name, type=type, description=des,
                              version=version, create_time=dt, file=fid, state=0)
            db.session.add(new_model)
            db.session.commit()
            flag = checkAdd(pid, name, version)
            if flag:
                model = db.session.query(Model).filter_by(name=name,project = pid,version=version).first()
                res['code'] = 1000
                res['msg'] = '创建成功'
                res['id'] = model.id
            else:
                res['code'] = 1003
                res['msg'] = '创建失败'
    except:
        res['code'] = 2000
        res['msg'] = '服务器错误，请检查参数'
    return jsonify(res)


@model_bp.route('/deleteModel/', methods=['GET', 'POST'])#删除模型
def deleteModel():
    res = {}
    try:
        model_id = request.form['model_id']
        print(model_id)
        if (len(model_id) == 0):
            res['code'] = 1005
            res['msg'] = '参数数据缺失'
        else:
            if db.session.query(Record).filter_by(model=model_id).first() and db.session.query(Record).filter_by(model=model_id).first().state == '1':
                print('cccccccc')
                res['code'] = 2013
                res['msg'] = '实例正在运行，无法删除实例'
            else:
                print('delete')
                flag = delete_model(model_id)
                if flag:
                    res['code'] = 1000
                    res['msg'] = '删除成功'
                else:
                    res['code'] = 1004
                    res['msg'] = '删除失败'
    except:
        res['code'] = 2000
        res['msg'] = '服务器错误，请检查参数'
    return jsonify(res)


@model_bp.route('/editParam/<model_id>', methods=['GET', 'POST'])#设置参数   是不是直接写文件就可以？
def editParam(model_id):
    if request.method == 'GET':
        #查找表单信息并返回
        res = {}
        model = db.session.query(Model).filter_by(id=model_id).first()
        if db.session.query(Record).filter_by(model = model_id).first():
            record = db.session.query(Record).filter_by(model=model_id).first()
            if record.memory==None:
                res['memory'] = ''
            else:
                res['memory'] = record.memory
            if record.input==None:
                res['input'] = ''
            else:
                res['input'] = record.input
            if record.output==None:
                res['output'] = ''
            else:
                res['output'] = record.output

            print(res)
        else:
            res['memory'] = ''
            res['input'] = ''
            res['output'] = ''
        res['type'] = model.type
        return render_template('model_parm.html', user=flask_login.current_user,res = res)
    res = {}
    try:
        flag = findRecord(model_id)
        print(flag)
        if flag:
            record  = db.session.query(Record).filter_by(model = model_id).first()
            if not record.state == '0' :
                print('cccccccc')
                res['code'] = 2019
                res['msg'] = '模型已部署，不能修改参数'
                return jsonify(res)
        else:
            print('xinzen1')
            new_Record = Record(model=model_id, url='/url', state='0')
            db.session.add(new_Record)
            db.session.commit()
            flag = True

        print('hhhhhhhhhhhh')
        type = get_model_type(model_id)
        file_path = get_config_file_path(model_id)

        if type == 'CPKT' or type == 'PB':
            print('pb')
            input = request.form['input']
            output = request.form['output']
            mem = request.form['mem']
            if mem == 'true':
                memory = request.form['memory']
            else:
                memory = 0
            # 编辑config.yml文件
        else:
            mem = request.form['mem']
            if mem == 'true':
                memory = request.form['memory']
            else:
                memory = 0
            input = ''
            output = ''
            # 编辑config.yml文件
        int(memory)
        editConfig(input, output, memory, file_path, type)

        print(flag)
        if edit_param(model_id, memory, input, output):
            res['code'] = 1000
            res['msg'] = '操作成功'
        else:
            res['code'] = 1006
            res['msg'] = '修改失败'

    except:
        res['code'] = 2000
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
    basic['pid'] = list['project']
    if record:
        # deploy['env']= record.RTenvironment
        # deploy['cpu']=record.cpu
        deploy['record_id'] = record.id
        deploy['mem']=record.memory if record.memory else ''
        deploy['url']=record.url if record.url else ''
        deploy['state']=record.state
        deploy['input'] = record.input if record.input else ''
        deploy['output'] = record.output if record.output else ''
        deploy['key'] = record.key if record.key else ''
        deploy['port'] = record.port if record.port else ''
    else:
        # deploy['env']=''
        # deploy['cpu']=''
        deploy['record_id'] = ''
        deploy['mem']=''
        deploy['url']=''
        deploy['state']=0
        deploy['input'] =""
        deploy['output'] = ""
        deploy['key'] = ""
        deploy['port'] = ""
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
    if type =='H5':#无文件夹
        data = {
            'CURRENT_MODEL_TYPE': 'H5',
            'H5' : {'model_path': file_path,'mem_limit': 0}
        }
    elif type == 'PB':#无文件夹
        data = {
            'CURRENT_MODEL_TYPE': 'PB',
            'PB' : {'model_path': file_path,
                    'input_node_name': '',
                    'output_node_name': '',
                    'mem_limit': 0
                    }
        }
    elif type == 'TXT':  # 找.txt
        # 此时file_path是文件夹
        model_graph_file_path = ''
        for file in os.listdir(file_path):
            if os.path.splitext(file)[1] == '.txt':
                model_graph_file_path = os.path.join(file_path,file)

        data = {
            'CURRENT_MODEL_TYPE': type,
            type: {'model_path': file_path, 'model_graph_file_path': model_graph_file_path,'cc':'hhhhhhhhhhh'}
        }
    elif type == 'CPKT':#找.meta
        #此时file_path是文件夹
        model_graph_file_path = ''
        for file in os.listdir(file_path):
            if os.path.splitext(file)[1] == '.meta':
                model_graph_file_path = os.path.join(file_path,file)
        data = {
            'CURRENT_MODEL_TYPE': 'CPKT',
            'CPKT': {'model_directory': file_path,
                     'model_graph_file_path':model_graph_file_path,
                     'input_node_name':'',
                     'output_node_name':'',
                     'mem_limit':0}
        }
    else:#PYTORCH 找 .pt .py文件
        model_path = ''
        model_graph_file_path = ''
        for file in os.listdir(file_path):
            if os.path.splitext(file)[1] == '.pt' or os.path.splitext(file)[1] == '.pth':
                model_path = os.path.join(file_path,file)
        for file in os.listdir(file_path):
            if os.path.splitext(file)[1] == '.py':
                model_graph_file_path = os.path.join(file_path,file)
        data = {
            'CURRENT_MODEL_TYPE': 'TORCH',
            'TORCH': {'model_path': model_path, 'model_graph_file_path': model_graph_file_path,'mem_limit': 0}
        }
    # 写入到yaml文件
    with open(yaml_path, "w", encoding="utf-8") as f:
        yaml.dump(data, f)
        f = open(yaml_path)
        x = yaml.load(f)
        print(x)
'''
@model_bp.route('/editFile/', methods=['GET', 'POST']) #测试修改yml文件参数
def editFIle():
    input = request.form['input']
    output = request.form['output']
    memory = request.form['memory']
    model_id = request.form['id']
    type = 'PB'
    # 编辑config.yml文件
    res ={}
    file_path = get_config_file_path(model_id)
    editConfig(input, output, memory, file_path,type)
    f = open(file_path, 'r', encoding='utf-8')
    x = f.read()
    print(x)
    return x    
'''

def editConfig(input_node_name,output_node_name,mem_limit,file_path,type):  #修改配置文件参数
    if type =='CPKT' or type == 'PB':#有input output name 参数
        with open(file_path, encoding="utf-8") as f:
            content = ruamel.yaml.safe_load(f)
            content[type]['input_node_name'] = input_node_name
            content[type]['output_node_name'] = output_node_name
            content[type]['mem_limit'] = mem_limit
            with open(file_path, 'w', encoding="utf-8") as nf:
                yaml.dump(content, nf, default_flow_style=False, allow_unicode=True)
    else:
        with open(file_path, encoding="utf-8") as f:
            content = ruamel.yaml.safe_load(f)
            content[type]['mem_limit'] = mem_limit
            with open(file_path, 'w', encoding="utf-8") as nf:
                yaml.dump(content, nf, default_flow_style=False, allow_unicode=True)
    return 0


