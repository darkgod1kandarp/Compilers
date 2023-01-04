import docker
import tarfile
import uuid


def main_function(file_name,  folder_name):

    client = docker.from_env()
    container = client.containers.get("py")

    uuid1 = uuid.uuid1()

    container.exec_run("mkdir " + folder_name)

    with tarfile.open(uuid1.hex+".tar", "w") as tar:
        tar.add(file_name, arcname=file_name)
    with open(uuid1.hex+".tar", "rb") as f:
        val = container.put_archive("./"+folder_name, f)

   

    return container

    i = 0
    stack = []

    while True:
        try:

            socket.output._sock.settimeout(5)
            data = socket.output._sock.recv(65000)

            if data.decode() == "":
                stack.append(data.decode())
                if len(stack) == 100:
                    break
            else:
                for i in stack:
                    print(i)
                stack = []
                print(data.decode())
        except:
            f = input("Enter the value in cmd : ")
            val = '{}\n'.format(f)
            val = str.encode(val)
            socket.output._sock.send(val)

        i = i + 1
    socket = container.exec_run('rm ./kandarp/testing.py')
