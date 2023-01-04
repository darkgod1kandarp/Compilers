import socketio

# create a socketio client
sio = socketio.Client()


sio.connect("http://0.0.0.0:3000")

sio.emit('create_folder_file' , {'container' : 'py'  ,'folder_t_file_f':True  ,'workdir':'/', 'name':"kandarp" } )

sio.emit('create_folder_file' , {'container' : 'py'  ,'folder_t_file_f':True  ,'workdir':'/kandarp', 'name':"utils" } )
sio.emit('create_folder_file' , {'container' : 'py'  ,'folder_t_file_f':False  ,'workdir':'/kandarp/utils', 'name':"convertingFiletoDataUri.py" } )
sio.emit('create_folder_file' , {'container' : 'py'  ,'folder_t_file_f':False  ,'workdir':'/kandarp', 'name':"testing.py" } )



# send a message to the socketio server
with open('utils/convertingFiletoDataUri.py' ,'r'  ) as  f:
    val  =  f.read()
    sio.emit("writing_file", {'file_name' :"convertingFiletoDataUri.py" ,  "data":  val ,'container' : 'py' ,  "workdir"  :  "/kandarp/utils" })
with open("testing.py" , 'r') as f1:
    val  =  f1.read()
    sio.emit("writing_file", {'file_name' :"testing.py" ,  "data":  val ,'container' : 'py' ,  "workdir"  :  "/kandarp" })



# For java  
# import socketio

# # create a socketio client
# sio = socketio.Client()


# sio.connect("http://0.0.0.0:3000")

# sio.emit('create_folder_file' , {'container' : 'java'  ,'folder_t_file_f':True  ,'workdir':'/', 'name':"kandarp" } )

# sio.emit('create_folder_file' , {'container' : 'java'  ,'folder_t_file_f':True  ,'workdir':'/kandarp', 'name':"utils" } )
# sio.emit('create_folder_file' , {'container' : 'java'  ,'folder_t_file_f':False  ,'workdir':'/kandarp/utils', 'name':"convertingFiletoDataUri.py" } )
# sio.emit('create_folder_file' , {'container' : 'java'  ,'folder_t_file_f':False  ,'workdir':'/kandarp', 'name':"main.java" } )



# # send a message to the socketio server
# with open('utils/convertingFiletoDataUri.py' ,'r'  ) as  f:
#     val  =  f.read()
#     sio.emit("writing_file", {'file_name' :"convertingFiletoDataUri.py" ,  "data":  val ,'container' : 'py' ,  "workdir"  :  "/kandarp/utils" })
# with open("main.java" , 'r') as f1:
#     val  =  f1.read()
#     sio.emit("writing_file", {'file_name' :"main.java" ,  "data":  val ,'container' : 'java' ,  "workdir"  :  "/kandarp" })





# # disconnect from the socketio server
# sio.disconnect()


# For C 
# import socketio

# # create a socketio client
# sio = socketio.Client()


# sio.connect("http://0.0.0.0:3000")

# sio.emit('create_folder_file' , {'container' : 'c_'  ,'folder_t_file_f':True  ,'workdir':'/', 'name':"kandarp" } )
# sio.emit('create_folder_file' , {'container' : 'c_'  ,'folder_t_file_f':False  ,'workdir':'/kandarp', 'name':"main.c" } )


# with open("main.c" , 'r') as f1:
#     val  =  f1.read()
#     sio.emit("writing_file", {'file_name' :"main.c" ,  "data":  val ,'container' : 'c_' ,  "workdir"  :  "/kandarp" })

# sio.disconnect()