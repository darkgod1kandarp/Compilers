
import utils.convertingDatauritoFile as convert
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import socketio
import uvicorn
import docker
import tarfile
import uuid
import os

app = FastAPI()

sio = socketio.AsyncServer(async_mode="asgi",  cors_allowed_origins='*')
socket_app = socketio.ASGIApp(sio)

storing_socket = {}

client = docker.from_env()
python_container = client.containers.get("py")
c_container = client.containers.get("c_")
java_container = client.containers.get("java")

app.mount("/", socket_app)


def storing_file_in_docker_container(data, container, type):
    """

    Args:
        data (string):file data 
        container (docker container): particular language container

    Returns:
        (file_name :str ,file_data :str , folder_name:str)
    """
    file_name, file_data, folder_name = uuid.uuid1(
    ).hex + type,  data, uuid.uuid1().hex + "_folder"

    convert.converting_data_uri_file(file_data,  file_name)

    uuid1 = uuid.uuid1()

    container.exec_run("mkdir " + folder_name)

    with tarfile.open(uuid1.hex+".tar", "w") as tar:
        tar.add(file_name, arcname=file_name)
    with open(uuid1.hex+".tar", "rb") as f:
        container.put_archive("./"+folder_name, f)
    os.system('rm ' + uuid1.hex+".tar")
    os.system('rm ' + file_name)
    return file_name,  file_data,  folder_name

def exec_state(cmd  =  "" , container  =  "" ,  socket  = False  , tty =  False  , stdin   = False  ,  stdout  =  False  , workdir  =  "/"  ):
    if cmd=="" or container ==  "":
        return "" 
    exec_id  =   client.api.exec_create(container  = container  ,  cmd =  cmd  ,  stdout   =  stdout  ,  stdin =  stdin , workdir =  workdir , tty =  tty  )
    return (client.api.exec_start(exec_id['Id'] ,  tty =  tty , socket  =  True) , exec_id)




@sio.on("python_file")
async def python_file(sid, data):
    """

    Args:
        sid ([type]): socket object
        data ([String]): file data thta needs to run

    Returns:

    """

    file_name,  file_data,  folder_name = storing_file_in_docker_container(
        data,  python_container, ".py")
    socket ,exec_id  = exec_state( container = "py" , cmd= "python3 ./" + folder_name+"/"+file_name, stdin=True, socket=True, tty=True , stdout=True)
    print(socket)
    storing_socket[file_name] = socket
    return await sio.emit("file_exec",  {"file_name":  file_name,  'folder_name': folder_name, 'container_type':   "py" , 'id' : exec_id['Id']})


@sio.on("java_file")
async def java_file(sid, data):

    file_name,  file_data,  folder_name = storing_file_in_docker_container(
        data,  java_container, ".java")
    

    error , _  = exec_state(container="java"  ,cmd  =  "javac ./"+folder_name+"/"+file_name, stdin=True, tty=True , stdout=True)
    error =  error._sock.recv(65000).decode()
    if error != "":
        return await sio.emit("compile_error",  {'error': error})

    finding_class_file_decoded , _ = exec_state(cmd   = "ls " + folder_name  ,  container="java" , socket=True  ,  tty=True  , stdin=True  , stdout=True )
    finding_class_file_decoded =  finding_class_file_decoded._sock.recv(65000).decode()
   
    splitting_files = finding_class_file_decoded.split("  ")

    if splitting_files[0].split(".")[1] == "class":
        compile_file_name = splitting_files[0].split(".")[0]
    else:
        compile_file_name = splitting_files[1].rstrip().split(".")[0]

    command = "java " + compile_file_name

    socket ,exec_id = exec_state(cmd  =  command , container="java" ,  stdin=True  , stdout=True  ,  workdir="/"+folder_name , tty=True  , socket=True)

    storing_socket[file_name] = socket
    return await sio.emit("file_exec",  {"file_name":  file_name,  'folder_name': folder_name, 'container_type':   "java" , 'id' : exec_id['Id']})


@sio.on("c_file")
async def c_file(sid, data):

    """

    Args:
        sid ([type]): socket object
        data ([String]): file data thta needs to run

    Returns:

    """

    file_name,  file_data,  folder_name = storing_file_in_docker_container(
        data,  c_container, ".c")
    
    compile_data  , _= exec_state(container="c_", cmd = "gcc ./" + folder_name+"/"+file_name +
                                        " -o " + folder_name+"/"+folder_name, stdin=True, tty=True, socket=True , stdout= True)
    error = compile_data._sock.recv(65000).decode()
    if error != "":
        return await sio.emit("compile_error", {'error': error})

    socket   , exec_id = exec_state( container = "c_" , cmd="./" + folder_name+"/"+folder_name, stdin=True, socket=True, tty=True  , stdout=True)
    storing_socket[file_name] = socket

    return await sio.emit("file_exec",  {"file_name":  file_name,  'folder_name': folder_name, 'container_type':   "c", 'id' : exec_id['Id']})


@sio.on("give_me_data")
async def python_recieve_data(sid, data):

    socket = storing_socket[data['file_name']]
    try:
        exit_code = client.api.exec_inspect(data['id'])
        
        socket._sock.settimeout(2)
        data = socket._sock.recv(65000)
        await sio.emit("sending_data",  data.decode())
        if exit_code['Running']==False:
            return  await sio.emit('file_ended')
        
    except Exception as e:
        print(e)
        await sio.emit("waiting_input")


@sio.on("deleteing_file")
async def file_deletion_from_continer(sid, data):
    container_type,  folder_name = data['container_type'], data['folder_name']
    if container_type == "py":
        python_container.exec_run("rm -rf " + folder_name)
    elif container_type == "c":
        c_container.exec_run("rm -rf " + folder_name)
    await sio.emit("deleted")


@sio.on("input_data")
async def python_sending_data(sid, data):
    socket = storing_socket[data['file_name']]

    val = '{}\n'.format(data['data'])
    val = str.encode(val)

    socket._sock.send(val)
    await sio.emit("data_recv")


if __name__ == "__main__":
    uvicorn.run("main:app", host="192.168.0.108", port=3000)
