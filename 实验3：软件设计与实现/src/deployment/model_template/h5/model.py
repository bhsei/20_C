from flask import Flask, make_response, Response, json, request
import sys
import os
import tensorflow as tf
import numpy

model = Flask(__name__)

@model.route('/', methods=['POST', 'GET'])
def index():
    resp = make_response()
    resp.status_code = 200
    resp.headers['content-type'] = 'text/plain'
    resp.data = 'Please visit route \'/run_model/\''
    return resp

@model.route('/run_model/', methods=['POST'])
def model_run():
    ### 使用form_data形式发送POST请求
    ### USER_AUTHENTICATION
    user_key = request.form['key']
    #TODO: AUTHENTICATION
    ### DATA_PARSER
    data = request.form['data']
    data_str = str(data)
    try:
        input_data = json.loads(data_str)
    except:
        response = Response("Not Structed Input")
        return response
    ###

    result = None
    try:
        run_result = model_h5.predict(input_data)
        run_result = numpy.asarray(run_result).tolist()
        result = {
            'status': 'success',
            'data': run_result
        }
    except:
        result = {
            'status': 'fail',
            'data': "Model Runtime Error"
        }

    response = Response(json.dumps(result),content_type='application/json',status=200)
    return response

def load_model(model_path):
    ## TODO: Log文件记录
    print("start load model")
    global model_h5
    model_h5 = tf.keras.models.load_model(model_path)
    print("success load model")

if __name__ == '__main__':
    '''
    argv:[
        port_no: flask程序运行端口号,
        model_path: 模型路径,
    ]
    '''
    # 参数个数不匹配
    if len(sys.argv) < 3:
        print("RETURN_CODE", 1)
        exit(1)
    port_no = -1
    try:
        port_no = int(sys.argv[1])
    except:
        # 端口值非整形
        print("RETURN_CODE", 2)
        exit(2)
    # 端口范围非BSD服务器端口范围
    if port_no < 5000 and port_no > 65535:
        print("RETURN_CODE", 3)
        exit(3)
    model_path = sys.argv[2]
    if not os.path.exists(model_path):
        print("RETURN_CODE", 4)
        exit(4)
    load_model(model_path)
    try:
        model.run(host='0.0.0.0', port=port_no)
    except OSError:
        print("RETURN_CODE", 5)
        exit(5)