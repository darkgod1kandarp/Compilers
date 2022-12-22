import docker
import tarfile


client = docker.from_env()
container = client.containers.get("c_")

container.exec_run("mkdir kandarp")


with tarfile.open("file.tar", "w") as tar:
    tar.add("main.c", arcname="main.c")

with open("file.tar", "rb") as f:
    val = container.put_archive("./kandarp", f)


result = container.exec_run("gcc ./kandarp/main.c -o ./kandarp/main")
exit_code = result.exit_code
if exit_code:
    print(result)


socket = container.exec_run(
    "./kandarp/main", stdin=True, socket=True, tty=True)

i = 0
stack = []

while True:
    try:

        socket.output._sock.settimeout(5)
        data = socket.output._sock.recv(16384)

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
socket = container.exec_run('rm ./kandarp/main.c')
socket = container.exec_run('rm ./kandarp/main')
