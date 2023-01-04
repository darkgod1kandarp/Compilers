import docker
import uuid

MAX_BUFFER = 65000
client = docker.from_env()


def exec_state(cmd="", container="",  socket=False, tty=False, stdin=False,  stdout=False, workdir="/"):
    if cmd == "" or container == "":
        return ""
    exec_id = client.api.exec_create(
        container=container,  cmd=cmd,  stdout=stdout,  stdin=stdin, workdir=workdir, tty=tty)
    return (client.api.exec_start(exec_id['Id'],  tty=tty, socket=socket), exec_id)


def error_state(container: str, cmd: str, workdir="/"):
    if cmd == "" or container == "":
        return "data  or container  should be there"
    error, _ = exec_state(container=container, cmd=cmd,
                          stdin=True, tty=True, stdout=True, socket=True, workdir=workdir)

    error = error._sock.recv(MAX_BUFFER).decode()
    if error != "":
        return error
    return False


def creating_folder_or_file(container: str, name: str,  folder_t_file_f: bool = True,  workdir="/"):
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
    if folder_t_file_f:
        if not name:
            return "Folder name required"
        cmd = 'rm -r ' + name
    
        return error_state(container=container,  cmd=cmd,  workdir=workdir)
    else:
        cmd = 'rm ' + name
        return error_state(container=container, cmd=cmd,  workdir=workdir)

def writing_file(file_name :str ,data:str  ,  container :  str  ,  workdir :str =  "/" ):
    if file_name=="":
        return "File name should be there"
    socket  ,  _ =  exec_state(cmd  =  "tee " + file_name ,  container  =  container , socket=True  ,  tty  =  True   , stdin =  True  , stdout = True ,  workdir=workdir)
    socket._sock.send(data.encode())
    socket._sock.recv(MAX_BUFFER)
def getting_folder_file(container : str  ,  workdir:str ):
    if workdir =="/":
        return "You can noy access to the particular folder"
    socket  , exec_id  =   exec_state(container =  container  , cmd  =  "find -type d" ,  socket  =  True ,  tty =  True  ,  stdin  =  True  ,  stdout  =  True  , workdir=workdir)
    exit_code = client.api.exec_inspect(exec_id['Id'])
    while exit_code['Running'] == True:
        exit_code = client.api.exec_inspect(exec_id['Id'])
   
    data  = socket._sock.recv(MAX_BUFFER).decode().split("\n")
    val  =   list(map(lambda x  :  x.strip() , data ))
    for  folder  in val[1 :  len(val)- 1]: 
        print('Folder ')
        socket  , exec_id  =  exec_state(container=container , cmd  =  "ls "+folder , socket=True  , tty =  True  , stdin =  True  , stdout  =  True  , workdir=workdir)
        print(socket._sock.recv(1024).decode().strip())
   

 

getting_folder_file(container= "py" , workdir= "/kandarp/")




    
    


# print(creating_folder_or_file(container="py",name  =  "kandarpo" ,    folder_t_file_f=True,  workdir="/"))
# print(creating_folder_or_file(container="py",name  =  "kandarp.py" ,    folder_t_file_f=False,  workdir="/kandarpo"))
# with open('main_python.py' , 'r') as f:
 
#     print(writing_file(file_name="kandarp.py" ,  data =  f.read() ,  container="py" , workdir="/kandarpo"  ))
