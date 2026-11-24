"""Se importan librerías"""
import network,asyncio,socket
from machine import Pin,PWM,ADC
from time import sleep

"""Configuración de red"""
ssid="RasPerry" #Nombre de red
contra="HolaMundo123." #Contraseña de red
wlan=network.WLAN(network.AP_IF) #Se configura la interfaz en AP
wlan.config(essid=ssid,password=contra) #Configura conexión con la red
wlan.active(True) #Se activa la interfaz
wlan.ifconfig(("192.168.4.1","255.255.255.0","192.168.4.1","192.168.4.1")) #Configura parametros de la red: IP,Máscara,Gateway,DNS

while not wlan.active():
    sleep(1)

"""Pines del motor delantero/dirección"""
mot_del=Pin(16,Pin.OUT) #Pin Enable/PWM
mot_del_izq=Pin(17,Pin.OUT) #Pin a activar si el motor debe girar a la izquierda
mot_del_der=Pin(18,Pin.OUT) #Pin a activar si el motor debe girar a la derecha

mot_del.value(1) #Activación del motor de dirección
mot_del_izq.value(0) #Dirección delantera motor de tracción
mot_del_der.value(0) #Dirección trasera motor de tracción

"""Pines del motor trasero/tracción"""
mot_tra=PWM(Pin(19),freq=1000) #Pin Enable/PWM
mot_tra_del=Pin(20,Pin.OUT) #Pin a activar si el carro debe ir hacia delante
mot_tra_atr=Pin(21,Pin.OUT) #Pin a activar si el carro debe ir hacia atrás

mot_tra.duty_u16(65535) #Fuerza del motor de tracción
mot_tra_atr.value(0) #Dirección trasera motor de tracción
mot_tra_del.value(0) #Dirección delantera motor de tracción

"""Otras variables relacionadas a los motores"""
mov=False #Define si se permite el movimiento
fren=False #Define si se permite el freno
direc=0 #Dirección
vel_mots=0 #Velocidad del motor de tracción
vel_ant=0 #Velocidad anterior del motor

"""Pines LEDs y fotoresistencia"""
foto_res=ADC(Pin(27)) #Pin fotoresistencia
led=Pin("LED",Pin.OUT) #Pin de LED de la Rasperry Pi
pin_reloj=Pin(14,Pin.OUT) #Pin reloj del registro de corrimiento
pin_datos=Pin(15,Pin.OUT) #Pin de datos del registro de corrimiento
est_leds=[0,0,0,0,0,0,0,0] #Estado actual de todos los LEDs
pin_reloj.off()
#[0,1]=luces frontales, [2,3]=direccional derecha, [4,5]=direccional izquierda, [6,7]=luces de freno

decre=0 #Estado del decrementador (0=apagado 1=automático -1=manual)
decre_val="000" #valor a decrementar
decre_pin0=Pin(10,Pin.OUT) #Bit menos significativo
decre_pin1=Pin(11,Pin.OUT) #Bit intermedio
decre_pin2=Pin(12,Pin.OUT) #Bit más significativo
lec0=Pin(7,Pin.IN) #Lectura del bit menos significativo
lec1=Pin(8,Pin.IN) #Lectura del bit intermedio
lec2=Pin(9,Pin.IN) #Lectura del bit más significativo

luz_amb= foto_res.read_u16() #Valor de fotoresistencia

"""Otras variables relacionadas a los LEDs"""
luz_man=False #Determina si los faros delanteros deben estar encencidos manualmente
luz_dir_izq=False #Determina si la direccional izquierda deben estar encendidos
luz_dir_der=False #Determina si la direccional derecha deben estar encendidos
luz_eme=False #Determina si ambas direccionales (luces de emergencia) deben estar encendidos
dir_eve=asyncio.Event()
 
"""Funciones relacionadas a los motores"""
 
"""Función para cambiar velocidad del motor de tracción"""
async def cam_vel():
    global vel_ant
    while True:
        if abs(vel_mots)==1:
            pwm=50000
        elif abs(vel_mots)==2:
            pwm=55000
        elif abs(vel_mots)==3:
            pwm=60000
        elif abs(vel_mots)==4:
            pwm=65535
        else:
            pwm=0
        
        mot_tra.duty_u16(pwm)
        
        if fren:
                mot_tra_del.value(1)
                mot_tra_atr.value(1)
        elif mov:
            if vel_mots>0:
                mot_tra_del.value(1)
                mot_tra_atr.value(0)
            elif vel_mots<0:
                mot_tra_del.value(0)
                mot_tra_atr.value(1)
        else:
            mot_tra_del.value(0)
            mot_tra_atr.value(0)
        
        #LEDs de freno
        if vel_ant>vel_mots and vel_ant>0 and vel_mots>=0:
            est_leds[6]=1
            est_leds[7]=1
        elif vel_ant<vel_mots and vel_ant<0 and vel_mots<=0:
            est_leds[6]=1
            est_leds[7]=1
        elif fren:
            est_leds[6]=1
            est_leds[7]=1
        else:
            est_leds[6]=0
            est_leds[7]=0
            
        vel_ant=vel_mots
        await asyncio.sleep(0.3)
    
"""Función para cambiar dirección del carro"""
async def cam_direc():
    if direc==1:
        mot_del_der.value(1)
        mot_del_izq.value(0)
        mot_del_der.value(0)
        mot_del_der.value(1)
    elif direc==-1:
        mot_del_der.value(0)
        mot_del_izq.value(1)
        mot_del_izq.value(0)
        mot_del_izq.value(1)
    else:
        mot_del_der.value(0)
        mot_del_izq.value(0)
        return
    await asyncio.sleep(0.175)
     
"""Funciones relacionadas a los LEDs"""
    
"""Función para encender faros delanteros"""
def luz_far():
    if luz_man or luz_amb<=8000:
        est_leds[0]=1
        est_leds[1]=1
    else:
        est_leds[0]=0
        est_leds[1]=0
    
"""Función para detectar cambios de luz en el ambiente"""
async def cam_luz_amb():
    global luz_amb,decre_val
    while True:
        luz_amb=foto_res.read_u16()
        luz_far()
        
        #Determinador de intervalo para decrementador
        if decre==1:
            if luz_amb>=0 and luz_amb<8191:
                decre_val="000"
            elif luz_amb>=8191 and luz_amb<16383:
                decre_val="001"
            elif luz_amb>=16383 and luz_amb<24575:
                decre_val="010"
            elif luz_amb>=24575 and luz_amb<32767:
                decre_val="011"
            elif luz_amb>=32767 and luz_amb<40959:
                decre_val="100"
            elif luz_amb>=40959 and luz_amb<49151:
                decre_val="101"
            elif luz_amb>=49151 and luz_amb<57343:
                decre_val="110"
            elif luz_amb>=57343 and luz_amb<=65535:
                decre_val="111"
        await asyncio.sleep(1)

"""Función para encender direccionales"""
async def luz_dir():
    global luz_eme,luz_dir_izq,luz_dir_der
    while True:
        await dir_eve.wait()
        while luz_eme or luz_dir_der or luz_dir_izq:
            if luz_eme:
                est_leds[2]=1
                est_leds[3]=1
                est_leds[4]=1
                est_leds[5]=1
            if luz_dir_der:
                est_leds[2]=1
                est_leds[3]=1
                est_leds[4]=0
                est_leds[5]=0
            elif luz_dir_izq:
                est_leds[2]=0
                est_leds[3]=0
                est_leds[4]=1
                est_leds[5]=1
            await asyncio.sleep(0.5)
            est_leds[2]=0
            est_leds[3]=0
            est_leds[4]=0
            est_leds[5]=0
            await asyncio.sleep(0.5)
        dir_eve.clear()

"""Función para que encender o apagar los LEDs en el registro de corrimiento"""
async def leds():
    global est_leds
    while True:
        bina=list(decre_val) #Lista de elementos para binarios

        #Si el decrementador esta activo cambia todos los leds
        if decre!=0:
            decre_pin0.value(int(bina[-1]))
            decre_pin1.value(int(bina[-2]))
            decre_pin2.value(int(bina[-3]))
            await asyncio.sleep(0.01)
            bit0=lec0.value()
            bit1=lec1.value()
            bit2=lec2.value()
            est_leds=[bit2,bit2,bit1,bit1,bit1,bit1,bit0,bit0] #Faros=bit más significativo, intermitentes=bit intermedio, frenos=bit menos significativos

        #Mandar el estado de los LEDs al registro
        for pos in range(len(est_leds)):
            pin_datos.value(est_leds[-(pos+1)])
            pin_reloj.off()
            pin_reloj.on()
        await asyncio.sleep(0.01)

"""Funciones de movimientos definidos"""

"""Función para hacer que el carro avance en círculos"""
async def circulo():
    global mov, direc, vel_mots
    vel_ant=vel_mots
    vel_mots = 3
    mov = True
    
    direc = 1
    await cam_direc()
    await asyncio.sleep(10)

    mov = False
    direc = 0
    vel_mots = vel_ant
    await cam_direc()

"""Función para hacer que el carro avance en zig-zag"""
async def zigzag():
    global mov, direc, vel_mots
    vel_ant=vel_mots
    vel_mots = 3
    mov = True

    for i in range(3):
        direc = -1
        await cam_direc()
        await asyncio.sleep(2)

        direc = 1
        await cam_direc()
        await asyncio.sleep(2)
    
    direc = 0
    mov = False
    vel_mots =  vel_ant
    await cam_direc()

"""Función para hacer que el carro avance en infinito"""
async def infinito():
    global mov, direc, vel_mots
    vel_ant=vel_mots
    vel_mots = 3
    mov = True
    
    direc = -1
    await cam_direc()
    await asyncio.sleep(2.5)

    direc = 0
    await cam_direc()
    await asyncio.sleep(1.5) 
    
    direc = 1
    await cam_direc()
    await asyncio.sleep(2.5)

    direc = 0
    await cam_direc()
    await asyncio.sleep(1.5)
    
    direc = -1
    await cam_direc()
    await asyncio.sleep(2.5)

    direc = 0
    mov = False
    vel_mots =  vel_ant
    await cam_direc()

"""Función de movimiento especial"""
async def especial():
    #Realiza un cuadrado
    global mov, direc, vel_mots
    vel_ant=vel_mots
    vel_mots = 3
    mov = True

    for i in range(4):
        direc = 0 
        await cam_direc()
        await asyncio.sleep(2)
        direc = 1  
        await cam_direc()
        await asyncio.sleep(1.5)
        
    direc = 0
    mov = False
    vel_mots = vel_ant
    await cam_direc()
    
"""Función para comunicación remota con PC"""
async def cliente(reader,writer):
    global mov,fren,direc,vel_mots,luz_man,luz_dir_izq,luz_dir_der,luz_eme,decre,decre_val,est_leds
    try:
        while True:
            datos=await reader.readline()
            if not datos:
                break #Se cerró la conexión
            
            comando=datos.decode("utf-8").strip()
            if not comando: #Si no recibe comando continua la programación
                continue
            
            if comando.startswith("mov:"):
                mov=bool(int(comando.split(":")[1]))
            elif comando.startswith("fren:"):
                fren=bool(int(comando.split(":")[1]))
            elif comando.startswith("direc:"):
                direc=int(comando.split(":")[1])
                await cam_direc()
            elif comando.startswith("vel_mots:"):
                vel_mots=int(comando.split(":")[1])
            elif comando.startswith("luz_man:"):
                luz_man=bool(int(comando.split(":")[1]))
                luz_far()
            elif comando.startswith("luz_dir_izq:"):
                if not luz_dir_izq:
                    luz_dir_der,luz_eme=False,False
                    luz_dir_izq=bool(int(comando.split(":")[1]))
                    dir_eve.set()
                else:
                    luz_dir_izq=bool(int(comando.split(":")[1]))
            elif comando.startswith("luz_dir_der:"):
                if not luz_dir_der:
                    luz_dir_izq,luz_eme=False,False
                    luz_dir_der=bool(int(comando.split(":")[1]))
                    dir_eve.set()
                else:
                    luz_dir_der=bool(int(comando.split(":")[1]))
            elif comando.startswith("luz_eme:"):
                if not luz_eme:
                    luz_dir_izq,luz_dir_der=False,False
                    luz_eme=bool(int(comando.split(":")[1]))
                    dir_eve.set()
                else:
                   luz_eme=bool(int(comando.split(":")[1]))
            elif comando.startswith("autodecre:"):
                decre=1
            elif comando.startswith("mandecre:"):
                decre=-1
                decre_val=comando.split(":")[1]
            elif comando.startswith("apdecre:"):
                decre=0
                decre_pin0.value(0)
                decre_pin1.value(0)
                decre_pin2.value(0)
                decre_val="000"
                est_leds=[0,0,0,0,0,0,0,0]
            elif comando.startswith("circulo:"):
                await circulo()
            elif comando.startswith("zigzag:"):
                await zigzag()
            elif comando.startswith("infinito:"):
                await infinito()
            elif comando.startswith("especial:"):
                await especial()
            elif comando.startswith("salir:"):
                break
    except OSError:
        pass
    finally:
        writer.close()
        await writer.wait_closed()

async def ser_rem():
    servidor=await asyncio.start_server(cliente,"0.0.0.0",5000)
    while True:
        await asyncio.sleep(0.05)

"""Función que crea las tareas/bucles a liberar"""
async def main():
    asyncio.create_task(cam_luz_amb())
    asyncio.create_task(leds())
    asyncio.create_task(cam_vel())
    asyncio.create_task(luz_dir())
    asyncio.create_task(ser_rem())
    while True:
        await asyncio.sleep(0.1)
        
"""Bucle principal"""
led.value(1)
asyncio.run(main())