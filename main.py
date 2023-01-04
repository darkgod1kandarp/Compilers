

import socketio
import uvicorn
import docker
from fastapi import FastAPI

app = FastAPI()

sio = socketio.AsyncServer(async_mode="asgi",  cors_allowed_origins='*')
socket_app = socketio.ASGIApp(sio)

storing_socket = {}

client = docker.from_env()
python_container = client.containers.get("py")
c_container = client.containers.get("c_")
java_container = client.containers.get("java")

app.mount("/", socket_app)



MAX_BUFFER = 65000


def exec_state(cmd="", container="",  socket=False, tty=False, stdin=False,  stdout=False, workdir="/"):
    """
    This function will  execute the task like it does in cmd  

    Args:
        cmd (str): [Which command to be executed]. Defaults to "".
        container (str): [In which container command is to be executed]. Defaults to "".
        socket (bool): [Socket attached to command line of the socker interface]. Defaults to False.
        tty (bool): [For any out put you want to see from the command line you have to set it true]. Defaults to False.
        stdin (bool): [If you want to give any input in docket interface command lien you have to use  stdin]. Defaults to False.
        stdout (bool): [If you want output you have to set it true ]. Defaults to False.
        workdir (str): [In which directory you have to work]. Defaults to "/".

    Returns:
        [socket]: [raw socket of python]
        [object]:[dictionary in which key "ID" is there for the particular process]
    """
    if cmd == "" or container == "":
        return ""
    exec_id = client.api.exec_create(
        container=container,  cmd=cmd,  stdout=stdout,  stdin=stdin, workdir=workdir, tty=tty)
    return (client.api.exec_start(exec_id['Id'],  tty=tty, socket=socket), exec_id)


def error_state(container: str, cmd: str, workdir="/"):
    """
    This Function will run the  exec_state which do not require socket 

    Args:
        container (str): [In which container command is to be executed]
        cmd (str): [Which command to be executed]
        workdir (str): [In which directory you have to work]. Defaults to "/".

    Returns:
        [string | boolean]: [If there is error then it will send error and if there is no error then it will send False]
    """
    if cmd == "" or container == "":
        return "data  or container  should be there"
    error, _ = exec_state(container=container, cmd=cmd,
                          stdin=True, tty=True, stdout=True, socket=True, workdir=workdir)

    error = error._sock.recv(MAX_BUFFER).decode()
    if error != "":
        return error
    return False


def creating_folder_or_file(container: str, name: str,  folder_t_file_f: bool = True,  workdir="/"):
    """
    This function  will run the create the folder or file in docker container  
    Args:
        container (str): [In which container command is to be executed]
        name (str): [Name of the file or folder that you want to store ]
        folder_t_file_f (bool): [True For creating Folder and False for Creating File]. Defaults to True.
        workdir (str): [In which directory you have to work]. Defaults to "/".
    Returns:
        [string | boolean]: [If there is error then it will send error and if there is no error then it will send False]
    """
    if folder_t_file_f:
        cmd = 'mkdir ' + name
        error = error_state(container=container,  cmd=cmd, workdir=workdir)
        if error:
            return error
        else:
            return name
    else:
        if not name:
            return 'File name required'
        cmd = 'touch '+name
        return error_state(container=container,  cmd=cmd, workdir=workdir)


def delete_folder_or_file(container: str, name: str,  folder_t_file_f: bool = True,  workdir="/"):
    """
        This Function will delete the folder in docker container 

    Args:
        container (str): [In which container command is to be executed]
        name (str): [Name of the file or folder that you want to store ]
        folder_t_file_f (bool, optional): [description]. Defaults to True.
        workdir (str): [In which directory you have to work]. Defaults to "/".


    Returns:
        [string | boolean]: [If there is error then it will send error and if there is no error then it will send False]
    """
    if folder_t_file_f:
        if not name:
            return "Folder name required"
        cmd = 'rm -r ' + name

        return error_state(container=container,  cmd=cmd,  workdir=workdir)
    else:
        cmd = 'rm ' + name
        return error_state(container=container, cmd=cmd,  workdir=workdir)


def writing_file(file_name: str, data: str,  container:  str,  workdir: str = "/"):
    """
    This FUnction will write  in File in docker container 

    Args:
        file_name (str): [File Name in which we have to write]
        data (str): [Data you have to writein that file]
        container (str): [Container name]
        workdir (str): [In which directory you have to work]. Defaults to "/".

    Returns:
        [string | boolean]: [If there is error then it will send error and if there is no error then it will send False]

    """
    if file_name == "":
        return "File name should be there"
    socket,  _ = exec_state(cmd="tee " + file_name,  container=container,
                            socket=True,  tty=True, stdin=True, stdout=True,  workdir=workdir)
    socket._sock.send(data.encode())
    socket._sock.send(b'n')
    socket._sock.recv(MAX_BUFFER)
    return True



@sio.on('writing_file')
async def file_writing(sid, data):
    """
    This emit method will execute the writtg

    Args
        sid ([socket]): [raw socket for emitting the data ]
        data ([Object]): [Object{file_name :str , data:str , container :enum("c_" , "java" , "py") , workdir:str}]
    """
    writing_file(file_name=data['file_name'],  data=data['data'],
                 container=data['container'],  workdir=data['workdir'])
    await sio.emit("file_writing_done")



@sio.on('running_file')
async def running_file(sid, data):
    """
    This emit method  will run the file 

    Args:
        sid ([socket]): [raw socket for emitting the data ]

        data ([Object]): [Object{container:str  ,  file_name:str  , folder_path :str}]
    """
    CMD = {'py':  'python3 ',  'java': 'java ',  'c_':  './'}

    if data['container'] == "java":
        compile_cmd = 'javac ' + data['file_name']
        compile_sock, exec_id = exec_state(
            cmd=compile_cmd, container="java", socket=True, tty=True, stdin=True,  stdout=True, workdir=data['folder_path'])
        exit_code = client.api.exec_inspect(exec_id['Id'])
        while exit_code['Running'] == True:
            exit_code = client.api.exec_inspect(exec_id['Id'])

        ls_sock, _ = exec_state(cmd='find . -name "*.class"', container="java",
                                socket=True, tty=True, stdin=True,  stdout=True, workdir=data['folder_path'])
        ls_data = ls_sock._sock.recv(1024).decode()
        # print(data ,  data.split(".class")[0].split("./")[1])
        compiled_file = ls_data.split(".class")[0].split("./")[1]

        data['file_name'] = compiled_file
    elif data['container'] == "c_":
        machine_file = data['file_name'].split(".")[0]
        compile_cmd = 'gcc ' + "./" + data['file_name'] + ' -o ' + machine_file
        compile_sock, exec_id = exec_state(
            cmd=compile_cmd, container="c_", socket=True, tty=True, stdin=True,  stdout=True, workdir=data['folder_path'])
        exit_code = client.api.exec_inspect(exec_id['Id'])
        while exit_code['Running'] == True:
            exit_code = client.api.exec_inspect(exec_id['Id'])
        data['file_name'] = machine_file
        


    using_cmd = CMD[data['container']]
    using_cmd = using_cmd + data['file_name']
    socket, exec_id = exec_state(
        cmd=using_cmd,  container=data['container'],  socket=True,  tty=True,  stdin=True, stdout=True,  workdir=data['folder_path'])
    storing_socket[data['folder_path'] + data['file_name']] = socket
    return await sio.emit('file_is_running', {'file_name': data['file_name'],  'folder_path': data['folder_path'],  'id': exec_id['Id'], 'container': data['container']})


@sio.on("create_folder_file")
async def create_file_folder(sid, data):

    """
    This listener method will run Create_folder_file 

    Args:
        sid ([socket]): [raw socket for emitting the data ]
        data ([Object]) ::[Object({folder_t_file_f:bool   ,  workdir:str  , name :str })]
    """
    error = creating_folder_or_file(
        container=data['container'],  folder_t_file_f=data['folder_t_file_f'],  workdir=data['workdir'], name=data['name'])
    return await sio.emit("file_created_not",  error)


@sio.on('delete_folder')
async def delete_file_folder(sid, data):
    """

    This listener method will run delete folder Function  

    Args:
        sid ([socket]): [raw socket for emitting the data ]
        data ([Object]): [Object({folder_t_file_f:bool   , workdir  :str , name  :str})]

 
    """
    error = delete_folder_or_file(
        container=data['container'],  folder_t_file_f=data['folder_t_file_f'],  workdir=data['workdir'],  name=data['name'])
    return await sio.emit("file_deleted_not", error)


@sio.on("give_me_data")
async def python_recieve_data(sid, data):
    """
     This listener will run the the required file 

    Args:
        sid ([socket]): [raw socket for emitting the data ]
        data ([Object]): [Object({folder_path :str  ,  file_name  :str })]

   
    """

    socket = storing_socket[data['folder_path'] + data['file_name']]
    try:
        exit_code = client.api.exec_inspect(data['id'])

        socket._sock.settimeout(2)
        recv_data = socket._sock.recv(MAX_BUFFER)
        await sio.emit("sending_data",  recv_data.decode())
        if exit_code['Running'] == False:
            container_type,  folder_name = data['container'], data['folder_path']
            if data['container']!="py":
                deleteing_file,  _ = exec_state(
                    cmd="rm -r " + data['file_name'] + ".class", container=container_type,  socket=True,  tty=True, stdin=True, stdout=True, workdir=data['folder_path'])
                deleteing_file,  _ = exec_state(
                    cmd="rm -r " + data['file_name'], container=container_type,  socket=True,  tty=True, stdin=True, stdout=True, workdir=data['folder_path'])
            return await sio.emit('file_ended')

    except Exception as e:
   
        await sio.emit("waiting_input")


@sio.on("input_data")
async def python_sending_data(sid, data):
    socket = storing_socket[data['folder_path'] + data['file_name']]

    val = '{}\n'.format(data['data'])
    val = str.encode(val)

    socket._sock.send(val)
    await sio.emit("data_recv")


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=3000, reload=True)
