import xlrd as xls # Libreria para el manejo de archivos .xls
import os #Libreria del sistema, usada para extraer la extension de los archivos

class FileChecker:
    # Implementacion del rectificador de formatos
    def __init__(self):
        self.toCheck = [["codigo",int,lambda x:len(x)<=10],
            ["nombre",str,lambda x:len(x)<=30],
            ["no. factura",int,lambda x:True],
            ["valor",float,lambda x:len(x)<=30],
            ["concepto",str,lambda x:len(x)<=30],
            [";"]]
        
    """
        Rectifica la validez de un archivo .csv
        (str)=>bool
    """   
    def csvCheck(self,file):
        file = open(file)
        i=0
        isValid=True
        counter = 0
        try:
            for rows in file:
                counter+=1
                row = rows.split(",")
                if row[0]==";": break
                if len(row)>2:
                    for i in range(2,len(row)):
                        row[1]+=str(row[i])
                row[0],row[1]=row[0].strip(),row[1].strip()
                if row[0].lower()==self.toCheck[i][0]:
                    value=row[1].replace(",","")
                    try:
                        self.toCheck[i][1](value)
                        isValid=self.toCheck[i][2](value)
                    except:
                        isValid=False
                else:
                    isValid=False
                if not(isValid): break
                i+=1
            file.close()
        except:
            isValid = False
        isValid = isValid and counter==6
        return isValid

    """
        Rectifica la validez de un archivo .txt
        (str)=>bool
    """
    def txtCheck(self,file):
        file = open(file)
        i=0
        isValid=True
        counter = 0
        try:
            for rows in file:
                counter+=1
                row = rows.split(":")
                if row[0]==";": break
                row[0],row[1]=row[0].strip(),row[1].strip()
                if row[0].lower()==self.toCheck[i][0]:
                    value=row[1].replace(",","")
                    try:
                        self.toCheck[i][1](value)
                        isValid=self.toCheck[i][2](value)
                    except:
                        isValid=False
                else:
                    isValid=False
                if not(isValid): break
                i+=1
            file.close()
        except:
            isValid = False
        isValid = isValid and counter==6
        return isValid

    """
        Rectifica la validez de un archivo .xls
        (str)=>bool
    """ 
    def xlsCheck(self,file):
        book = xls.open_workbook(file)
        file = book.sheet_by_index(0)
        counter = 0
        try:
            for i in range(5):
                counter+=1
                row = [file.cell_value(0,i),file.cell_value(1,i)]
                if row[0].lower()==self.toCheck[i][0]:
                    value=row[1]
                    if isinstance(value,str): value=value.replace(",","")
                    try:
                        self.toCheck[i][1](value)
                        isValid=self.toCheck[i][2](str(value))
                    except:
                        isValid=False
                else:
                    isValid=False
                if not(isValid): break
            book.release_resources()
        except:
            isValid = False
        isValid = isValid and counter==5
        return isValid

    """
        Rectifica la validez de un archivo, implementacion del patron de diseño factory
        (str)=>bool
    """
    def check(self,file):
        ext = os.path.splitext(file)[1].lower()
        isValid = False
        if ext==".xls":
            isValid = self.xlsCheck(file)
        elif ext==".csv":
            isValid = self.csvCheck(file)
        elif ext==".txt":
            isValid = self.txtCheck(file)
        return isValid
        
class FileComparator:
    def __init__(self):
        self.fileChecker = FileChecker()
        self.types = [int,str,int,float,str]

    """
        Compara dos archivos sin importar su extensio y devuelve un string a modo de lista con las diferencias separadas por '#'
        (str,str)=>str
    """
    def compare(self,file1,file2):
        diff = ""
        if self.fileChecker.check(file1) and self.fileChecker.check(file2):
            dataFile1 = self.getData(file1)
            dataFile2 = self.getData(file2)
            for i in dataFile1:
                if dataFile1[i] != dataFile2[i]: diff+="{}:{}#{}:{}#".format(i,dataFile1[i],i,dataFile2[i])
            diff=diff[:len(diff)-1]
        return diff

    """
        Obtiene la informacion de un archivo .xls
        (str)=>dict
    """
    def getXLSData(self,file):
        book = xls.open_workbook(file)
        file = book.sheet_by_index(0)
        data = {}
        for i in range(5):
            value = file.cell_value(1,i)
            if isinstance(value,str): value=value.replace(",","")
            data[file.cell_value(0,i).lower()] = str(self.types[i](value)).lower()
        book.release_resources()
        return data

    """
        Obtiene la informacion de un archivo .txt
        (str)=>dict
    """
    def getTXTData(self,file):
        file = open(file)
        data = {}
        i=0
        for rows in file:
            row = rows.split(":")
            if row[0]==";": break
            value=row[1].strip().replace(",","")
            row[0],row[1]=row[0].strip(),self.types[i](value)
            data[row[0].lower()] = str(row[1]).lower()
            i+=1
        file.close()
        return data

    """
        Obtiene la informacion de un archivo .csv
        (str)=>dict
    """
    def getCSVData(self,file):
        file = open(file)
        data = {}
        i=0
        for rows in file:
            row = rows.split(",")
            if row[0]==";": break
            if len(row)>2:
                for i in range(2,len(row)):
                    row[1]+=str(row[i])
            row[0],row[1]=row[0].strip(),self.types[i](row[1].strip())
            data[row[0].lower()] = str(row[1]).lower()
            i+=1
        file.close()
        return data

    """
        Obtiene la informacion de un archivo sin importar su extension, implementacion del patron de diseño factory
        (str)=>dict
    """
    def getData(self,file):
        ext = os.path.splitext(file)[1].lower()
        data = None
        if ext==".xls":
            data = self.getXLSData(file)
        elif ext==".csv":
            data = self.getCSVData(file)
        elif ext==".txt":
            data = self.getTXTData(file)
        return data

    """
        Convierte la informacion de archivo en un string
        (dict)=>str
    """
    def toString(self,data):
        string = ""
        for i in data:
            string += "{}:{}\n".format(i,data[i])
        string += ";"
        return string

"""
    Limpia el directorio que contiene los archivos temporales de la aplicacion
    None=>None
"""
def fileClear():
    print("Cleaning...")
    files = "./files"
    for i in os.listdir(files):
        os.remove(os.path.join(files,i))
