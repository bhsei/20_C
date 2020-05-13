import sys
import time
import os
import subprocess
import yaml
import re
from hashlib import md5

base_port = 5001
port_range = 10000
base_url = "39.97.219.243:"
TORCH_TEMPLATE_DIR = "/root/model_deployment/model_template/torch"
CPKT_TEMPLATE_DIR = "/root/model_deployment/model_template/cpkt"
PB_TEMPLATE_DIR = "/root/model_deployment/model_template/pb"
H5_TEMPLATE_DIR = "/root/model_deployment/model_template/h5"
SERVER_MEM = 2000
MEM_LIMIT_INSTANCE_PROGRAM = 512
MEM_LIMIT_INSTANCE_USER = 2560
MEM_LIMIT_INSTANCE = 0

def get_insnum_by_model_id(par):
    return 1
    pass

def get_insnum_by_user_id(par):
    return 1
    pass

def getAvailablePort():
    port = hash(time.time()) % port_range + base_port
    for _ in range(port_range):
        pid_result = os.popen("netstat -tunlp | grep " + str(port)).readlines()
        if len(pid_result) == 0:
            break
        port = ((port + 1) - base_port) % port_range + base_port
    return port

def getPIDByPort(port):
    cnt = 0
    pid = None
    while cnt < 10:
        time.sleep(1)
        try:
            pid_line = os.popen("netstat -anp | grep :" + str(port)).readlines()[0]
            pid = re.sub(".+?LISTEN", "", pid_line)
            pid = re.findall("\d{4,5}", pid)[0]
            break
        except:
            cnt += 1
    return pid

def getRC(log_path):
    cnt = 0
    return_code = None
    while (cnt < 10):
        time.sleep(1)
        print(os.path.exists(log_path))
        if os.path.exists(log_path):
            f = open(log_path)
            lines = f.readlines()
            for line in lines:
                if 'RETURN_CODE' in line:
                    return_code = line.replace("RETURN_CODE", "").strip()
                    break
            f.close()
            break
        cnt += 1

    return return_code

def memoryCheck(pid_list, limit):
    _sum = 0.
    for _pid in pid_list:
        mem_line = os.popen("ps aux | grep "+str(_pid)).readlines()[0]
        mem_arr = re.split(" {1,10}",mem_line)[3]
        mem_float = float(mem_arr)
        _sum += mem_float
    if _sum/100*SERVER_MEM >= limit:
        return False
    return True

def deploy_impl(model_id, model_settings_file_path):
    # torch模型所需参数：端口、模型路径、模型图文件（拷贝至flask文件夹下）
    # cpkt模型所需参数：端口、模型文件夹、模型图文件、（输入节点名、输出节点名）
    # pb模型所需参数：端口、模型路径、（输入节点名、输出节点名）
    # h5模型所需参数：端口、模型路径
    pid = -1
    result = {
        "status": 4036,
        "url": "",
        "pid": pid
    }

    ### get conf ###
    conf_path = model_settings_file_path
    try:
        conf_file = open(conf_path, 'r', encoding="utf-8")
        conf = yaml.load(conf_file.read(), Loader=yaml.FullLoader)
        conf_file.close()
        MODEL_TYPE = conf['CURRENT_MODEL_TYPE']
        MEM_LIMIT_INSTANCE = conf['mem_limit']
    except:
        return 4033
    ### get conf ###

    key = md5((str(time.time())+str(model_id)).encode("utf8")).hexdigest()
    if MODEL_TYPE == "TORCH":
        model_path, model_graph_file_path = conf[MODEL_TYPE]['model_path'], conf[MODEL_TYPE]['model_graph_file_path']
        model_folder = "model_" + str(model_id) + "_" + str(int(time.time()))
        new_folder = os.path.join("instance", model_folder)
        os.popen("cp -r " + TORCH_TEMPLATE_DIR + " " + new_folder)
        time.sleep(1)
        os.popen("cp " + model_graph_file_path + " " + new_folder)
        # TODO: 异常处理 return 4036
        port = getAvailablePort()
        ### start deploy ###
        flask_run_file = str(os.path.join("/", "root", "model_deployment", new_folder, "model.py"))
        instance = os.popen("nohup python " + flask_run_file + " " + str(
            port) + " " + model_path + " " + key + " >" + model_folder + "_nohup_process.log &")
        rc = getRC(model_folder + "_nohup_process.log")
        print("RC", rc)
        if rc == 1:
            os.popen("rm -rf " + new_folder)
            return 4034
        elif rc == 2 or rc == 3:
            os.popen("rm -rf " + new_folder)
            return 4033
        elif rc == 4:
            os.popen("rm -rf " + new_folder)
            return 4031
        elif rc == 5:
            os.popen("rm -rf " + new_folder)
            return 4034
        else:
            pid = getPIDByPort(port)
            result["status"] = 0
            result["pid"] = getPIDByPort(port)
            result["key"] = key
            result["url"] = base_url + str(port) + "/run_model/"
    elif MODEL_TYPE == "CPKT":
        model_dir, model_graph_file_path, input_node_name, output_node_name = conf[MODEL_TYPE]['model_directory'], \
                                                                              conf[MODEL_TYPE][
                                                                                  'model_graph_file_path'], \
                                                                              conf[MODEL_TYPE]['input_node_name'], \
                                                                              conf[MODEL_TYPE]['output_node_name']
        model_folder = "model_" + str(model_id) + "_" + str(int(time.time()))
        new_folder = os.path.join("instance", model_folder)
        os.popen("cp -r " + CPKT_TEMPLATE_DIR + " " + new_folder)
        time.sleep(1)
        # TODO: 异常处理 return 4036
        port = getAvailablePort()
        ### start deploy ###
        flask_run_file = str(os.path.join("/", "root", "model_deployment", new_folder, "model.py"))
        if input_node_name == None:
            input_node_name = ""
        if output_node_name == None:
            output_node_name = ""
        instance = os.popen("nohup python " + flask_run_file + " " + str(
            port) + " " + model_dir + " " + model_graph_file_path + " " + key + " " + input_node_name + " " + output_node_name + " >" + model_folder + "_nohup_process.log &")
        rc = getRC(model_folder + "_nohup_process.log")
        print("RC", rc)
        if rc == 1:
            os.popen("rm -rf " + new_folder)
            return 4034
        elif rc == 2 or rc == 3:
            os.popen("rm -rf " + new_folder)
            return 4033
        elif rc == 4 or rc == 5:
            os.popen("rm -rf " + new_folder)
            return 4031
        elif rc == 6:
            os.popen("rm -rf " + new_folder)
            return 4034
        else:
            result["status"] = 0
            result["pid"] = getPIDByPort(port)
            result["key"] = key
            result["url"] = base_url + str(port) + "/run_model/"
    elif MODEL_TYPE == "PB":
        model_path, input_node_name, output_node_name = conf[MODEL_TYPE]['model_path'], \
                                                        conf[MODEL_TYPE]['input_node_name'], \
                                                        conf[MODEL_TYPE]['output_node_name']
        model_folder = "model_" + str(model_id) + "_" + str(int(time.time()))
        new_folder = os.path.join("instance", model_folder)
        os.popen("cp -r " + PB_TEMPLATE_DIR + " " + new_folder)
        time.sleep(1)
        # TODO: 异常处理 return 4036
        port = getAvailablePort()
        ### start deploy ###
        flask_run_file = str(os.path.join("/", "root", "model_deployment", new_folder, "model.py"))
        if input_node_name == None:
            input_node_name = ""
        if output_node_name == None:
            output_node_name = ""
        instance = os.popen("nohup python4tf1 " + flask_run_file + " " + str(
            port) + " " + model_path + " " + key + " " + input_node_name + " " + output_node_name + " >" + model_folder + "_nohup_process.log &")
        rc = getRC(model_folder + "_nohup_process.log")
        print("RC", rc)
        if rc == 1:
            os.popen("rm -rf " + new_folder)
            return 4034
        elif rc == 2 or rc == 3:
            os.popen("rm -rf " + new_folder)
            return 4033
        elif rc == 4:
            os.popen("rm -rf " + new_folder)
            return 4031
        elif rc == 5:
            os.popen("rm -rf " + new_folder)
            return 4034
        else:
            result["status"] = 0
            result["pid"] = getPIDByPort(port)
            result["key"] = key
            result["url"] = base_url + str(port) + "/run_model/"
    elif MODEL_TYPE == "H5":
        model_path = conf[MODEL_TYPE]['model_path']
        model_folder = "model_" + str(model_id) + "_" + str(int(time.time()))
        new_folder = os.path.join("instance", model_folder)
        os.popen("cp -r " + H5_TEMPLATE_DIR + " " + new_folder)
        time.sleep(1)
        # TODO: 异常处理 return 4036
        port = getAvailablePort()
        ### start deploy ###
        flask_run_file = str(os.path.join("/", "root", "model_deployment", new_folder, "model.py"))
        instance = os.popen("nohup python " + flask_run_file + " " + str(
            port) + " " + model_path  + " " + key + " >" + model_folder + "_nohup_process.log &")
        rc = getRC(model_folder + "_nohup_process.log")
        print("RC", rc)
        if rc == 1:
            os.popen("rm -rf " + new_folder)
            return 4034
        elif rc == 2 or rc == 3:
            os.popen("rm -rf " + new_folder)
            return 4033
        elif rc == 4:
            os.popen("rm -rf " + new_folder)
            return 4031
        elif rc == 5:
            os.popen("rm -rf " + new_folder)
            return 4034
        else:
            result["status"] = 0
            result["pid"] = getPIDByPort(port)
            result["key"] = key
            result["url"] = base_url + str(port) + "/run_model/"
    else:
        return 4033

    return result

def deploy(model_id, model_settings_file_path, user_pid_list, program_pid_list):
    if not memoryCheck(user_pid_list, MEM_LIMIT_INSTANCE_USER) or not memoryCheck(program_pid_list, MEM_LIMIT_INSTANCE_PROGRAM):
        return 4038

    deploy_result = deploy_impl(model_id, model_settings_file_path)
    ### 生成实例前的内存限制 传入参数：用户下的pid list 和 该模型所属项目下的pid list ###
    try:
        int(deploy_result)
        return deploy_result
    except:
        ### 生成实例后的内存限制####
        pid = deploy_result["pid"]
        if not memoryCheck([pid], MEM_LIMIT_INSTANCE):
            delete(pid)
            return 4038

        new_user_pid_list = user_pid_list.append(pid)
        new_prog_pid_list = program_pid_list.append(pid)
        if not memoryCheck(new_user_pid_list, MEM_LIMIT_INSTANCE_USER) or not memoryCheck(new_prog_pid_list, MEM_LIMIT_INSTANCE_PROGRAM):
            delete(pid)
            return 4038
        else:
            conf["KEY"] = deploy_result["key"]
            file_yml = open(model_settings_file_path, "w")
            yaml.dump(conf, file_yml)
            file_yml.close()
            return deploy_result

def delete(pid):
    status_code = 4044
    result_code = os.system("kill -9 {}".format(str(pid)))
    if result_code != 0:
        status_code = 4041
    return result_code


def pause(pid, port):
    process_result = os.popen("netstat -tunlp | grep " + str(port)).readlines()
    if len(process_result) == 0:
        return False
    port_pid = int(process_result[0].split()[6].split('/')[0])
    if port_pid != pid:
        return False
    pause_result = os.system("iptables -A INPUT -p tcp --dport {} -j DROP".format(str(port)))
    if pause_result != 0:
        return False
    return True


def restart(pid, port):
    process_result = os.popen("netstat -tunlp | grep " + str(port)).readlines()
    if len(process_result) == 0:
        return False
    port_pid = int(process_result[0].split()[6].split('/')[0])
    if port_pid != pid:
        return False
    pause_result = os.system("iptables -A INPUT -p tcp --dport {} -j ACCEPT".format(str(port)))
    if pause_result != 0:
        return False
    return True


if __name__ == "__main__":
    user_pid_list = []
    program_pid_list = []
    print(deploy(3,"/root/model_deployment/config.yml", user_pid_list, program_pid_list))
    #delete(2405)
    #pause(2450, 11477)
    #restart(2450, 11477)
