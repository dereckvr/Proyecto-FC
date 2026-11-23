"""Se importan librerías"""
import tkinter,socket

"""IP y puerto de la conexión con la ras"""
ip_ras="192.168.4.1"
puerto=5000

server=None

"""Función para realizar la conexión"""
def conexion():
    global server
    try:
        server=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        server.settimeout(3)
        server.connect((ip_ras,puerto))
        lab_est.config(text="Conectado")
    except:
        lab_est.config(text="Desconectado")
        print("Error de conexión")

def desconectar():
    if server:
        try:
            server.sendall("salir\n".encode('utf-8'))
            server.close()
        except:
            pass
    ventana.destroy()
        
"""Función para enviar intrucciones con valores no booleanos"""
def coman_gen(coman,var):
    global server
    var=var.get()
    if server is None:
        return
    try:
        mensaje=f"{coman}:{var}\n"
        server.sendall(mensaje.encode('utf-8'))
    except:
        server=None
        print("Error de conexión")

"""Función para ewnviar intrucciones con valores booleanos"""
def coman_bool(coman,var):
    global server
    var=var.get()
    if server is None:
        return
    try:
        if var:
            mensaje=f"{coman}:1\n"
            server.sendall(mensaje.encode('utf-8'))
        else:
            mensaje=f"{coman}:0\n"
            server.sendall(mensaje.encode('utf-8'))
    except:
        server=None
        print("Error de conexión")


"""Crear ventana de tkinter"""
ventana=tkinter.Tk()
ventana.title("Control del carro")
ventana.geometry("1000x900")
ventana.resizable(False,False)
"""Hacer una cuadricula"""
for num in range(10):
    ventana.columnconfigure(num,minsize=100)
for num in range(9):
    ventana.rowconfigure(num,minsize=100)

"""Variables presentes en ambos programas"""
mov=tkinter.BooleanVar(value=False)
fren=tkinter.BooleanVar(value=False)
direc=tkinter.IntVar(value=0)
vel_mots=tkinter.IntVar(value=0)
luz_man=tkinter.BooleanVar(value=False)
luz_dir_izq=tkinter.BooleanVar(value=False)
luz_dir_der=tkinter.BooleanVar(value=False)
luz_eme=tkinter.BooleanVar(value=False)
autodecre=tkinter.StringVar(value="0")
mandecre=tkinter.StringVar(value="000")
apdecre=tkinter.StringVar(value="0")
circulo=tkinter.StringVar(value="circulo")
zigzag=tkinter.StringVar(value="zigzag")
infinito=tkinter.StringVar(value="infinito")
especial=tkinter.StringVar(value="especial")

"""Función para crear botones mantenibles"""
def crear_bot_man(texto,com_pres,com_suel,colum,fila):
    bot=tkinter.Button(ventana,text=texto)
    bot.bind("<ButtonPress-1>",com_pres)
    bot.bind("<ButtonRelease-1>",com_suel)
    bot.grid(column=colum,row=fila,sticky="nsew")
    return bot

"""Función para crear botones"""
def crear_bot(texto,com,colum,fila):
    bot=tkinter.Button(ventana,text=texto,command=com)
    bot.grid(column=colum,row=fila)
    return bot 

"""Función sobre información del programa"""
def info():
    ven=tkinter.Toplevel(ventana)
    ven.title("Información del programa")
    ven.geometry("800x800")
    for num in range(8):
        ven.columnconfigure(num,minsize=100)
    for num in range(8): 
        ven.rowconfigure(num,minsize=100)
    ven.resizable(False,False)
    lab_prog=tkinter.Label(ven,text="Información sobre integrantes:\nInstituto Tecnológico de Costa Rica\nDereck Matías Venegas Rodríguez\nMax Andrés Quirós Hernández")
    lab_prog.grid(column=0,row=0,columnspan=2)
    ima1=tkinter.PhotoImage(file="pro_1.png")
    ima2=tkinter.PhotoImage(file="pro_2.png")
    ventana.ima1=ima1
    ventana.ima2=ima2
    lab_ima1=tkinter.Label(ven,image=ima1)
    lab_ima1.grid(column=0,row=1,columnspan=2,rowspan=2)
    lab_ima2=tkinter.Label(ven,image=ima2)
    lab_ima2.grid(column=0,row=3,columnspan=2,rowspan=2)
    lab_gui=tkinter.Label(ven,text="Información sobre uso del programa:\n\n-El botón recto hace que el carro se mueva en dirección a la velocidad seleccionada.\n"
    "-El botón freno hace que el carro se detenga.\n-Los botenes < y > hacen que el carro se mueva hacia la dirección seleccionada a la velocidad seleccionada.\n"
    "-La barra le asigna una velocidad al carro, si esta es negativo el carro retrocede y si es positiva avanza.\n"
    "-Los botones de direccionales izquierda y derecha activan las direccionales del lado seleccionado y las luces de emergencia todas las direccionales.\n"
    "-El botón de faros prende los faros delanteros.\nEl botón de reconexión intenta reconectar con la Rasperry Pi.\n"
    "-El botón de decrementador automático activa el decrementador automático dependiendo del nivel de luz.\n"
    "-El botón de decrementador manual envía el número binario escrito arriba de este y activa el decrementador manual.\n"
    "-El botón de apagar decrementador desactiva decrementador.\n"
    "-Los botones de la derecha activan los movimientos especiales correspondientes a su nombre.\n"
    "-El botón de salir del programa desconecta y cierra el programa.\n",wraplength=400)
    lab_gui.grid(column=4,row=0,columnspan=4,rowspan=3)
    lab_info=tkinter.Label(ven,text="Información sobre el programa:\n\nEl programa fue desarrollado en Python 3.13 y utiliza la librería tkinter para la interfaz gráfica."
    "\nControl de vehiculo con Rasperry\nVersión 2.1",wraplength=300)
    lab_info.grid(column=5,row=5,columnspan=3,rowspan=3)

"""Interfaz"""

"""Botones mantenibles"""
crear_bot_man("Recto",lambda x:(mov.set(True),coman_bool("mov",mov)),lambda x:(mov.set(False),coman_bool("mov",mov)),1,5)
crear_bot_man("Freno",lambda x:(fren.set(True),coman_bool("fren",fren)),lambda x:(fren.set(False),coman_bool("fren",fren)),1,7)
crear_bot_man(">",lambda x:(direc.set(1),coman_gen("direc",direc),mov.set(True),coman_bool("mov",mov)),lambda x:(direc.set(0),coman_gen("direc",direc),mov.set(False),coman_bool("mov",mov)),2,6)
crear_bot_man("<",lambda x:(direc.set(-1),coman_gen("direc",direc),mov.set(True),coman_bool("mov",mov)),lambda x:(direc.set(0),coman_gen("direc",direc),mov.set(False),coman_bool("mov",mov)),0,6)

"""Botones no mantenibles"""
crear_bot("Faros\nDelanteros",lambda:(luz_man.set(not luz_man.get()),coman_bool("luz_man",luz_man)),0,1)
crear_bot("Direccional\nDerecha",lambda:(luz_dir_der.set(not luz_dir_der.get()),coman_bool("luz_dir_der",luz_dir_der),luz_dir_izq.set(False),luz_eme.set(False)),0,3)
crear_bot("Direccional\nIzquierda",lambda:(luz_dir_izq.set(not luz_dir_izq.get()),coman_bool("luz_dir_izq",luz_dir_izq),luz_dir_der.set(False),luz_eme.set(False)),2,3)
crear_bot("Luces de\nEmergencia",lambda:(luz_eme.set(not luz_eme.get()),coman_bool("luz_eme",luz_eme),luz_dir_izq.set(False),luz_dir_der.set(False)),2,1)
crear_bot("Decrementador\nautomático",lambda:coman_gen("autodecre",autodecre),4,5)
crear_bot("Apagar\ndecrementador",lambda:coman_gen("apdecre",apdecre),4,4)
crear_bot("Circulos",lambda:coman_gen("circulo",circulo),7,1)
crear_bot("Zig-zag",lambda:coman_gen("zigzag",zigzag),7,3)
crear_bot("Infinito",lambda:coman_gen("infinito",infinito),7,5)
crear_bot("Especial",lambda:coman_gen("especial",especial),7,7)

"""Entry para decrementador"""
entry_dec=tkinter.Entry(ventana,textvariable=mandecre)
entry_dec.grid(column=4,row=6)
crear_bot("Enviar número\npara decrementador",lambda:coman_gen("mandecre",mandecre),4,7)

"""Barra de velocidad"""
barra=tkinter.Scale(orient="vertical",from_=4, to=-4,variable=vel_mots)
barra.grid(column=5,row=4,rowspan=3,sticky="ns")
barra.bind("<ButtonRelease-1>",lambda x:coman_gen("vel_mots",vel_mots))

"""Conexión con Rasperry Pi"""
crear_bot("Reintentar conexión",conexion,5,1)
crear_bot("Salir del programa",desconectar,5,2)
lab_est=tkinter.Label(ventana,text="Desconectado")
lab_est.grid(column=4,row=1)

"""Mostrar información del programa"""
crear_bot("Acerca del\nprograma",info,4,2)

"""desconexion de la Rasperry"""
ventana.protocol("WM_DELETE_WINDOW",desconectar)
ventana.after(100,conexion)
ventana.mainloop()