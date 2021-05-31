from flask import * #Flask es un framework simple para hacer paginas web
import os #Liberira del sistema, usada en esta app para obterner las extensiones de los archivos
from FileManager import * # Archivo .py que contiene las clases FileChecker y FileComparator
from DatabaseManager import * # Archivo .py que contiene los metodos para hablar con la base de datos
from werkzeug.utils import secure_filename # Metodo para verificar de manera segura los nombres de los archivos
from psycopg2 import * # Interprete de SQL
from psycopg2.extras import * # Interprete de SQL

#Initial config
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = "./files/"
app.config['ATTEMPS'] = 0
app.config['USER'] = [-1,-1,-1,-1,-1]

#Database Manager
db = DatabaseManager()

#Routes
#Login page 
@app.route('/',methods=['GET','POST'])
def loginPage():
    action = render_template("login.html") #Se establece una accion predeterminada, en este caso sera simplemente cargar login.html sin ningun cambio
    if request.method == 'POST':
        mode = request.form['mode']
        if mode == "login": #Se verifica en que modo se encuentra la pagina
            user,passwd = request.form['usernameLogin'],request.form['passLogin']  #Se obtinen los datos de la pagina a travez del metodo POST y se constrastan con la base de datos
            dataUser = db.login(user,passwd)
            if dataUser!=None and not(dataUser[5]): #Se valida que el usuario se haya loggeado y la cuenta no este bloqueada
                app.config['USER'] = dataUser #Se guardan los datos del usuario que esta usando la app 
                if dataUser[3]==2:            #Dependiendo del nivel de autorizacion se redirige al usuario a su respectiva pagina
                    action = redirect("/free_comparator")
                elif dataUser[3]==1:
                    action = redirect("/comparator")
                elif dataUser[3]==0:
                    action = redirect("/log")
            elif dataUser!=None and dataUser[5]:
                error = "Account is blocked."
                action = render_template("login.html",errorInfo=error)
            elif dataUser==None: #No hay coincidencias de la base de datos con los datos ingresados por el usuario
                app.config['ATTEMPS'] += 1
                dataUser = db.getUserId(user) #Se rectifica si el no esta registrado
                if len(dataUser) == 0:
                    comm = "3 Intentos fallidos de login por parte de un usuario desconocido"
                    id_user = None
                    error = "User is not registered."
                else: #El usuario esta registrado pero la clave es erronea
                    comm = "3 Intentos de login fallidos por parte del usuario {}".format(user)
                    id_user = dataUser[0]
                    error = "Wrong username or password."
                if app.config['ATTEMPS'] == 3:
                    db.registLog(comm,id_user) #Se registra los intentos fallidos
                    db.blockUser(id_user)      #Se bloquea la cuenta
                    app.config['ATTEMPS'] = 0
                action = render_template("login.html",errorInfo=error)
        elif mode == "register": #Modo registro, se piden los datos de la pestaña de "Sing Up"
            user,passwd,name = request.form['usernameRegister'],request.form['passRegister'],request.form['nameRegister']
            message = db.registUser(user,passwd,name)
            if message[0]:
                action = render_template("login.html",errorInfo=message[1])
            else:
                action = render_template("login.html",messageInfo=message[1])
    return action

#Comparador; nivel 3 de autorizacion
@app.route('/free_comparator',methods=['GET','POST'])
def free_comparator():
    comm = "Acesso al comparador de nivel 1"
    action = render_template("lvl2Comparator.html",data=["",""]) #Se establece una accion predeterminada, en este caso sera simplemente cargar lvl2Comparator.html sin ningun cambio
    if app.config['USER'][3]==2: #Se comprueba que el usuario tenga el nivel adecuado de autorizacion
        valid,loaded,filesData=True,False,["",""]
        diff = ""
        comm = "Comparacion de archivos"
        if request.method == 'POST':
            checker,comp = FileChecker(), FileComparator() #Se crea una instacia de las clases FileChecker y FileComparator, necesarias para la rectificacion y comparacion de los archivos
            files = request.files.getlist('files[]') #Se obtienen los archivos subidos por el usuario
            names = []
            i=0
            for file in files: #Se recorren los archivos para salvarlos en las carpeta configurada
                filename = secure_filename(file.filename) #Se obtiene el nombre del archivo de forma segura
                name = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(name)
                valid = valid and checker.check(name) #Se comprueba que el archivo cumpla con el formato
                names.append(name)
                if valid:
                    fileData = comp.getData(name)
                    filesData[i] = comp.toString(fileData)
                i += 1
            if not(valid):
                filesData = ["",""]
                comm = "Comparacion de archivos: formato invalido"
            diff = comp.compare(names[0],names[1]) #Se comparan los archivos
            loaded=True
            
            action = render_template("lvl2Comparator.html", invalid=not(valid),uploaded=loaded,data=filesData,dataDiff=diff) #Se renderiza la pagina con los datos de la comparacion
    else:
        comm = "El usuario no tiene los privilegios suficientes para ingresar al comparador de nivel 1"
        action = redirect('/error') #Se redirige al usuario por no tener los privilegios necesarios
    db.registLog(comm,app.config['USER'][0]) #Se crea el log correspondiente a la accion
    return action

#Comparador; nivel 2 de autorizacion
@app.route('/comparator',methods=['GET','POST'])
def comparator():
    comm = "Acesso al comparador de nivel 2"
    action = render_template("lvl1Comparator.html",data=["",""])
    if app.config['USER'][3]==1: #Se comprueba que el usuario tenga el nivel adecuado de autorizacion
        filesData,diff,valid,filesRequired=["",""],"",True,True
        if request.method == 'POST':
            checker,comp = FileChecker(), FileComparator() #Se crea una instacia de las clases FileChecker y FileComparator, necesarias para la rectificacion y comparacion de los archivos
            files = request.files.getlist('files[]') #Se obtienen los archivos subidos por el usuario
            names = []
            if len(files)==2: #Se comprueba la lista de archivos con el fin de determinar si el usuario monto archivos nuevos
                i=0
                for file in files: #Se recorren los archivos para salvarlos en las carpeta configurada
                    filename = secure_filename(file.filename)
                    name = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    file.save(name)
                    valid = valid and checker.check(name)#Se comprueba que el archivo cumpla con el formato
                    if valid:
                        names.append(name)
                        fileData = comp.getData(name)
                        filesData[i] = comp.toString(fileData)
                    i+=1
                if not(valid):
                    filesData = ["",""]
                    comm = "Comparacion de archivos: formato invalido"
            elif len(files)<2: #El usuario no monto archvios nuevos, se procede a salvar la informacion de los textArea
                filesRequired = False
                filesData[0],filesData[1] = request.form['file1'],request.form['file2']
                for i in range(2):
                    filename = os.path.join(app.config['UPLOAD_FOLDER'],'tempFile'+str(i)+'.txt')
                    file=open(filename,"w+")
                    file.write(filesData[i].replace("\n",""))
                    file.close()
                    if not(checker.check(filename)):
                        valid=False
                        break
                    names.append(filename)
            if valid:
                diff = comp.compare(names[0],names[1]) #Si los archivos son validos, se comparan
                comm = "Comparacion de archivos"
            action = render_template("lvl1Comparator.html",data=filesData,dataDiff=diff,invalid=not(valid),required=filesRequired)
    else:
        comm = "El usuario no tiene los privilegios suficientes para ingresar al comparador de nivel 2"
        action = redirect('/error') #El usuario se redirige a la pagina de error por no tener los privilegios necesarios
    db.registLog(comm,app.config['USER'][0]) #Se crea el log correspondiente a la accion
    return action

#Logs; nivel 1 de autorizacion
@app.route('/log')
def log():
    comm = "Acesso al log"
    if app.config['USER'][3]==0: #Se comprueba que el usuario tenga el nivel adecuado de autorizacion
        action = render_template("logs.html")
        if request.method == 'GET':
            logsData = db.consultLogs() #Se consulta la tabla log de la base de datos
            action = render_template("logs.html",logs=logsData) #Se carga la pagina con los logs
    else:
        comm = "El usuario no tiene los privilegios suficientes para ingresar al Log history"
        action = redirect('/error') #El usuario se redirige a la pagina de error por no tener los privilegios necesarios
    db.registLog(comm,app.config['USER'][0]) #Se crea el log correspondiente a la accion
    return action

@app.route('/error')
def error():
    return render_template("error.html") #Se carga la pagina de error

if __name__ == '__main__':
    fileClear()
    app.run()
    
