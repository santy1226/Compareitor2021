from psycopg2 import *
from psycopg2.extras import *

class DatabaseManager:
    def __init__(self):
        uri='postgres://vfwzjalbpftkjv:5ca88a39085371b2ed23248f15dbe6ac41ddf8e29c1a0794a67cce60c2ec1004@ec2-3-215-57-87.compute-1.amazonaws.com:5432/d7jsv90avh9695'
        self.conn = connect(uri)
        self.cur = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        
    """
        Retorna los datos para el usuario que coincida con el username y password proporcionados
        (str,str,psycopg2.extras.DictCursor)=>List
    """
    def login(self,user,passwd):
        try:
            self.cur.execute("select * from users where username='{}' and pass='{}' and id_user != 0;".format(user,passwd))
            result=self.cur.fetchall()
        except:
            result=[]
        return result[0] if len(result)>0 else None

    """
        Registra un nuevo usuario
        (str,str,str,psycopg2.extras.DictCursor)=>str
    """
    def registUser(self,user,passwd,name):
        message = [False,"User registered successfully!"]
        try:
            self.cur.execute("insert into users (username,pass,auth_level,fullname) values ('{}','{}',{},'{}');".format(user,passwd,2,name))
        except psycopg2.DatabaseError as e:
            self.conn.rollback()
            message = [True,"User already exists."]
        self.conn.commit()
        return message

    """
        Registra un nuevo log
        (str,int,psycopg2.extensions.connection,psycopg2.extras.DictCursor)=>None
    """
    def registLog(self,commentary,user):
        try:
            self.cur.execute("insert into logs (commentary,id_user) values ('{}',{});".format(commentary,0 if user==None else user))
        except:
            self.conn.rollback()
        self.conn.commit()

    """
        Retorna el ID correspondiente al username
        (str,psycopg2.extensions.connection,psycopg2.extras.DictCursor)=>int
    """
    def getUserId(self,user):
        try:
            self.cur.execute("select id_user from users where username='{}';".format(user))
            result=self.cur.fetchall()
        except:
            result=[]
        return result[0] if len(result)>0 else []

    """
        Consulta en la base de datos todos los registros de logs
        (psycopg2.extras.DictCursor)=>List
    """
    def consultLogs(self,cur):
        try:
            self.cur.execute("select id_log,username,log_date,commentary from logs x join users y on x.id_user = y.id_user;")
            result=self.cur.fetchall()
        except:
            result=[]
        return result

    """
        Bloquea la cuenta del usuario con el ID proporcionado
        (int,psycopg2.extensions.connection,psycopg2.extras.DictCursor)=>None
    """
    def blockUser(self,id_user):  
        try:
            self.cur.execute("update users set is_blocked=True where id_user={};".format(id_user))
        except:
            self.conn.rollback()
        self.conn.commit()
