from project.models.model import Project,User,SQLAlchemy,Model,File,Record
from project.models import db
from datetime import datetime

def getVersion(pid,name):#项目id和模型名称
    print(name)
    print(pid)
    count = db.session.query(Model).filter_by(state=0,name=name,project = pid).count()
    print(count)
    return count

def checkAdd(pid,name,version):
    flag = False
    if db.session.query(Model).filter_by(name=name,project = pid,version=version).first():
        flag = True
    print(flag)
    return flag

#找到模型文件id
def getFile(url,name):
    dt = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    new_file = File(create_time=dt, update_time=dt,name = name,path=url,type=1,state=0)

    db.session.add(new_file)
    db.session.commit()
    fid = db.session.query(File).filter_by(path=url, name =name).first().id
    return fid

#删除模型
def delete_model(id):
    if db.session.query(Record).filter_by(model=id).first():
        record = db.session.query(Record).filter_by(model=id).first()
        db.session.delete(record)
        db.session.commit()

    model = db.session.query(Model).filter_by(id=id).first()
    db.session.delete(model)
    db.session.commit()
    if db.session.query(Model).filter_by(id=id).first():
        return False
    else:
        return True
#检查是否有这个实例
def findRecord(id):
    flag = False
    if db.session.query(Record).filter_by(model = id).first():
        flag = True
    return flag
#检查修改参数是否成功
def edit_param(id,memory,input,output):
    flag = False
    rec = db.session.query(Record).filter_by(model=id).first()

    rec.memory = memory
    rec.input = input
    rec.output = output
    db.session.commit()

    if db.session.query(Record).filter_by(model = id,memory=memory,input=input,output=output).first():
        flag = True
    print('cccc')
    print(flag)
    return flag

#根据id找到config文件路径
def get_config_file_path(id):
    model = db.session.query(Model).filter_by(id=id).first()
    id = model.file
    file = db.session.query(File).filter_by(id=id).first()
    path = file.path
    return path

#获取模型类别
def get_model_type(id):
    model = db.session.query(Model).filter_by(id = id).first()
    type = model.type
    return type
# 由项目id模型列表
def model_list(pro_id):
    list = db.session.query(Model).filter_by(state=0, project=pro_id).all()
    data = []
    for l in list:
        d = {}
        d['name'] = l.name
        d['type'] = l.type
        d['create_time'] = str(l.create_time)
        if l.update_time:
            d['update_time'] = str(l.update_time)
        else:
            d['update_time'] = ''
        d['id'] = l.id
        if l.algorithm:
            d['algorithm']=l.algorithm
        else:
            d['algorithm'] =''
        if l.RTengine:
            d['RTengine']=l.RTengine
        else:
            d['RTengine'] =''
        if l.description:
            d['description']=l.description
        else:
            d['description'] =''
        d['version']=l.version
        if l.assessment:
            d['assessment']=l.assessment
        else:
            d['assessment'] =''
        # d['file']=l.file
        # d['project']=l.project
        data.append(d)
    # print(data)
    return data


# 由model id得到model信息
def get_model_detail_by_id(model_id):
    l = db.session.query(Model).filter_by(state=0, id=model_id).first()
    d = {}
    d['name'] = l.name
    d['type'] = l.type
    d['create_time'] = str(l.create_time)
    d['update_time'] = str(l.update_time)
    d['id'] = l.id
    d['algorithm'] = l.algorithm
    d['RTengine'] = l.RTengine
    d['description'] = l.description
    d['version'] = l.version
    d['assessment'] = l.assessment
    d['project'] = l.project
    file = get_file_detail_by_id(l.file)
    d['file']=file['path']
    return d


# 由file id 得到file detail
def get_file_detail_by_id(file_id):
    f = db.session.query(File).filter_by(id=file_id).first()
    data = {}
    data['name']=f.name
    data['path']=f.path
    data['type']=f.type
    data['create_time']=f.create_time
    data['update_time']=f.update_time
    return data
