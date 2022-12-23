
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

app.mount("/", socket_app)


def storing_file_in_docker_container(data, container):
    """

    Args:
        data (string):file data 
        container (docker container): particular language container

    Returns:
        (file_name :str ,file_data :str , folder_name:str)
    """
    file_name, file_data, folder_name = uuid.uuid1(
    ).hex + ".c",  data, uuid.uuid1().hex + "_folder"

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


@sio.on("python_file")
async def python_file(sid, data):
    """

    Args:
        sid ([type]): socket object
        data ([String]): file data thta needs to run

    Returns:

    """

    file_name,  file_data,  folder_name  =  storing_file_in_docker_container(data ,  python_container)
    socket = python_container.exec_run("python3 ./" + folder_name+"/"+file_name, stdin=True, socket=True, tty=True)
    storing_socket[file_name] = socket
    return await sio.emit("file_exec",  {"file_name":  file_name,  'folder_name': folder_name, 'container_type':   "py"})


@sio.on("c_file")
async def python_file(sid, data):

    """

    Args:
        sid ([type]): socket object
        data ([String]): file data thta needs to run

    Returns:

    """

    file_name,  file_data,  folder_name =  storing_file_in_docker_container(data ,  c_container)
    compile_data = c_container.exec_run("gcc ./" + folder_name+"/"+file_name + " -o " + folder_name+"/"+folder_name, stdin=True, tty=True, socket=True)
    error = compile_data.output._sock.recv(65000).decode()
    if error != "":
        return await sio.emit("compile_error", {'error': error})

    socket = c_container.exec_run("./" + folder_name+"/"+folder_name, stdin=True, socket=True, tty=True)
    storing_socket[file_name] = socket

    return await sio.emit("file_exec",  {"file_name":  file_name,  'folder_name': folder_name, 'container_type':   "c"})


@sio.on("give_me_data")
async def python_recieve_data(sid, data):

    socket = storing_socket[data['file_name']]

    try:
        socket.output._sock.settimeout(2)
        data = socket.output._sock.recv(65000)

        await sio.emit("sending_data",  data.decode())
    except Exception as e:

        await sio.emit("waiting_input")


@sio.on("deleteing_file")
async def file_deletion_from_continer(sid, data):
    print(data)
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

    socket.output._sock.send(val)
    await sio.emit("data_recv")


if __name__ == "__main__":

    uvicorn.run("main:app", host="192.168.0.108", port=3000)
