import docker  
import  tarfile   


client = docker.from_env()
container = client.containers.get("trusting_black")

with tarfile.open("file.tar", "w") as tar:
    tar.add("main.c", arcname="main.c")

with open("file.tar", "rb") as f:
    container.put_archive( ".", f)

result = container.exec_run("gcc main.c -o main")

socket = container.exec_run(
    "./main", stdin=True, socket=True, tty=True  )
print(socket)

i   =  0
stack  = []

while  True:
    try:

        socket.output._sock.settimeout(5)
        data = socket.output._sock.recv(16384)
        
        if  data.decode()=="":
            stack.append(data.decode())
            if len(stack)==100:
                break    
        else:
            for i  in stack:
                print(i)
            stack  =   []
            print(data.decode())
    except:
        f  =  input("Enter the value in cmd : ")
        val  =  '{}\n'.format(f)
        val = str.encode(val)
        socket.output._sock.send(val)
    
    i =  i+ 1
    


 





# socket.output._sock.send(b'efefwfewr')
# data = socket.output._sock.recv(16384)
# print(data)




# exit_code = socket.wait()

# unknown_byte=socket._sock.recv(1024)

# print(socket.__dict__)
# print(unknown_byte)
# socket._sock.sendall(b"kandarp")
# print(socket.__dict__)
# unknown_byte=socket._sock.recv(1024)
# print(unknown_byte)
# print(socket.__dict__)
# stack  =   []
# exit_code = socket.wait()
# print(exit_code)


        
        
   





