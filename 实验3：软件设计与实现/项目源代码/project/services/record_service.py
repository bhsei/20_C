from project.models.model import Project,User,SQLAlchemy,Model,File,Record,Project
from project.models import db
import flask_login
from datetime import datetime
# 由model_id返回record
def get_record_detail_by_model(model_id):
    print(model_id)
    # record = Record.query.filter_by(model=model_id).first()
    record = db.session.query(Record).filter_by(model=model_id).first()
    return record

'''# 由model_id返回record_id
def get_record_id_by_model(model_id):
    print(model_id)
    return Record.query.filter_by(model=model_id).first()
'''
# 将port 和url存入数据库
def edit_record(model_id,port,url,key,pid):
    flag  = False
    record = db.session.query(Record).filter_by(model = model_id).first()

    record.url = url
    record.port = port
    record.state = '1'
    record.key = key
    record.pid = pid
    db.session.commit()
    if db.session.query(Record).filter_by(port = port).first():
        flag = True
    return flag


#计数，找该用户所有正在运行的实例个数
def countStat(model_id):
    data = {}
    #先找project_id
    model = db.session.query(Model).filter_by(id=model_id).first()
    project_id = model.project
    print(project_id)

    models = db.session.query(Model).filter_by(project=project_id).all()

    program_pid_list = []
    for m in models:
        program_pid_list.append(m.id)

    user_account = flask_login.current_user.account
    #user_account = '123@123.com'
    print(user_account)
    projects = db.session.query(Project).filter_by(user=user_account).all()
    user_pid_list = []
    for p in projects:
        print(p.id)
        user_pid_list.append(p.id)
    #计数
    count  = db.session.query(User, Project,Model,Record).filter(
            User.account == Project.user,Project.id==Model.project,Model.id==Record.model).filter( User.account == user_account,
            Record.state == '1').count()
    print(count)

    data['count'] = count
    data['user_pid_list'] = user_pid_list
    data['program_pid_list'] = program_pid_list

    return data

#根据模型id找到实例运行状态
def get_Record_State(id): #0未部署 1运行中 2暂停中
    # record = Record.query.filter_by(model=id).first()
    record = db.session.query(Record).filter_by(model=id).first()
    state = record.state
    return state

#根据模型id找到config文件路径
def get_config_file_path(id):
    # model = Model.query.filter_by(id=id).first()
    model = db.session.query(Model).filter_by(id=id).first()
    id = model.file
    # file = File.query.filter_by(id=id).first()
    file = db.session.query(File).filter_by(id=id).first()
    path = file.path
    return path

#删除实例
def delete_record(id):
    record = db.session.query(Record).filter_by(model=id).first()
    db.session.delete(record)
    db.session.commit()

    if db.session.query(Record).filter_by(model=id).first():
        return False
    else:
        return True

# 判断是否已经暂停
def get_record_state(record_id):
    # record = Record.query.filter_by(id = record_id).first()
    record = db.session.query(Record).filter_by(id = record_id).first()
    state = record.state
    state = int(state)
    return state

# 由record_id返回record
def get_record_by_id(record_id):
    # return Record.query.filter_by(id = record_id).first()
    return db.session.query(Record).filter_by(id = record_id).first()
