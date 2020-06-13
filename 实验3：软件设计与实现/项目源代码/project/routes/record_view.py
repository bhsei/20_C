from project.models.model import User,Record
from flask import Flask, redirect, url_for,render_template,request,Blueprint,jsonify
from project.models import db
import flask_login
import datetime
from project.services.record_service import get_record_detail_by_model,get_record_state,get_record_by_id
record_bp = Blueprint('record', __name__, url_prefix='/record')
from project.services.record_service import countStat,get_Record_State,get_config_file_path,delete_record,edit_record
from project.deployment.instance_impl import deploy,delete,pause,restart

@record_bp.route('/startModel/',methods=['GET', 'POST'])
def startModel():#模型部署
    res = {}
    try:
        model_id = request.form['model_id']
        if (len(model_id) == 0):
            res['code'] = 1005
            res['msg'] = '参数数据缺失'
        else:
            #检查实例是否存在

            if not db.session.query(Record).filter_by(model=model_id).first():
                #res['code'] = 2016
                #res['msg'] = '实例不存在'
                create_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                new_record = Record(model=model_id, state = '0',url='/url',create_time = create_time)
                db.session.add(new_record)
                db.session.commit()

            #先查部署的模型有没有超过10

            data = countStat(model_id)
            print('hhhhhhhhhhh')
            if data['count']>=10:
                res['code'] = 2016
                res['msg'] = '运行实例数达到上限'
            elif get_Record_State(model_id)=='1':
                res['code'] = 2015
                res['msg'] = '该模型已经在运行状态'
            else:
                model_setting_file_path = get_config_file_path(model_id)
                print(model_setting_file_path)
                user_pid_list = data['user_pid_list']
                print(user_pid_list)
                program_pid_list = data['program_pid_list']
                print(model_id,model_setting_file_path,user_pid_list,program_pid_list) 
                result = deploy(model_id,model_setting_file_path,user_pid_list,program_pid_list)  #部署系统返回的代码
                print("result", result)
                #result = 4033
                if result == 4031 or result == 4036 or result == 4033 or result == 4034 or result == 4038:
                    res['code'] = 2011
                    res['msg'] = '部署失败'

                else:
                    #获得pid port和url和时间，存到数据库
                    port = result['port']
                    url = result['url']
                    key = result['key']
                    pid = result['pid']
                    flag = edit_record(model_id,port,url,key,pid)
                    if flag:
                        res['code'] = 1000
                        res['msg'] = '部署成功'
                        res['port'] = port
                        res['url'] = url
                        res['key'] = key
                    else:
                        res['code'] = 2011
                        res['msg'] = '部署失败'
    except:
        res['code'] = 2000
        res['msg'] = '服务器错误，请检查参数'
    return jsonify(res)
#states，pid，url，key


@record_bp.route('/deleteRecord/',methods=['GET', 'POST'])
def deleteRecord():#删除实例
    model_id = request.form['model_id']
    res={}
    if (len(model_id) == 0):
        res['code'] = 1005
        res['msg'] = '参数数据缺失'
    elif not db.session.query(Record).filter_by(model=model_id).first():
        res['code'] = 2020
        res['msg'] = '实例不存在'
    elif get_Record_State(model_id)=='1':
        res['code'] = 2013
        res['msg'] = '实例在运行状态，不能删除'
    else:
        record = db.session.query(Record).filter_by(model=model_id).first()
        pid = record.pid
        code = delete(pid)
        #code = '4044'
        if code == 4044:
            flag = delete_record(model_id)
            if flag:
                res['code'] = 1000
                res['msg'] = '删除成功'
            else:
                res['code'] = 1004
                res['msg'] = '删除失败'
        elif code == 4041:
            res['code'] = 2020
            res['msg'] = '服务器不存在该实例'
        else:
            res['code'] = 1004
            res['msg'] = '删除实例失败'
    return jsonify(res)


# 暂停运行中实例
@record_bp.route('/pauseModel/',methods=['GET','POST'])
def pauseModel():
    res = {}
    model_id = request.form['model_id']
    print(model_id)
    record = get_record_detail_by_model(model_id)

    # record = get_record_by_id(record_id)
    # 判断查询是否成功
    if not record:
        code = 2012
        msg = '服务未启动'
        res['code']=code
        res['msg']=msg
        return jsonify(res)

    port = record.port
    pid = record.pid
    record_id = record.id
    state = get_record_state(record_id)
    print('state',state,type(state))
    # 判断实例状态
    # 2 暂停中
    if state == 2:
        res['code'] = 2014
        res['msg'] = '实例已在暂停状态'
        return jsonify(res)
    # 0 未部署
    elif state == 0:
        code = 2012
        msg = '服务未启动'
        res['code'] = code
        res['msg'] = msg
        return jsonify(res)
    else:
        #  调用pause(record_id,port) 返回ans
        ans = pause(pid,port)
        print("pause:",ans)
        # ans = False
        if ans:
            res['code'] = 1000
            res['msg'] = '实例暂停成功'
            record.state = 2
            db.session.commit()
        else:
            res['code'] = 2000
            res['msg'] = '实例暂停失败'
        return jsonify(res)


# 重启暂停后的实例
@record_bp.route('/restartModel/',methods=['GET', 'POST'])
def restartModel():
    res = {}
    model_id = request.form['model_id']
    print('model_id',model_id)
    record = get_record_detail_by_model(model_id)
    # record = get_record_by_id(record_id)
    # 判断查询是否成功
    if not record:
        code = 2012
        msg = '服务未启动'
        res['code'] = code
        res['msg'] = msg
        return jsonify(res)

    port = record.port
    pid = record.pid
    record_id = record.id
    state = get_record_state(record_id)
    print(state, type(state))
    # 判断实例状态
    # 1 运行中
    if state == 1:
        res['code'] = 2015
        res['msg'] = '实例已在运行状态'
        return jsonify(res)
    # 0 未部署
    elif state == 0:
        code = 2012
        msg = '服务未启动'
        res['code'] = code
        res['msg'] = msg
        return jsonify(res)
    else:
        #  调用restart(record_id,port) 返回ans
        ans = restart(pid,port)
        print('restart:',ans)
        if ans:
            res['code'] = 1000
            res['msg'] = '实例恢复成功'
            record.state = 1
            db.session.commit()
        else:
            res['code'] = 2000
            res['msg'] = '实例恢复失败'
        return jsonify(res)


# 测试数据库修改
@record_bp.route('/addtest/', methods=['GET', 'POST'])
def addrecord():
    if request.method == 'GET':
      return render_template('create_project.html',user = flask_login.current_user)
    model = request.form['model']
    url = request.form['url']
    output = request.form['output']
    input = request.form['input']
    key = request.form['key']
    port = request.form['port']
    create_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(model, url, output,input,key,port,create_time)
    new_record = Record(model = model, url = url, output = output, input = input,key = key, port=port,create_time=create_time)
    db.session.add(new_record)
    db.session.commit()
    dic  = {}
    msg = 'true'
    dic['msg']=msg
    return jsonify(dic)
