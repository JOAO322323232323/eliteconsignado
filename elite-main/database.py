import mysql.connector

class DATABASE(object):

    USERDB = 'adminbanco'
    PASSDB = '!=Str000'
    HOSTDB = '62.72.8.214'
    DATADB = 'dev'

    def __init__(self):
        self.cnx = mysql.connector.connect(user=self.USERDB, password=self.PASSDB, host=self.HOSTDB, database=self.DATADB)
        self.cursor = self.cnx.cursor()

    def execute_fetch_all(self, cmd):
        self.cursor.execute(cmd)
        return self.cursor.fetchall()
    
    def execute_fetch_one(self, cmd):
        self.cursor.execute(cmd)
        return self.cursor.fetchone()
    
    def execute_not_fetch(self, cmd):
        return self.cursor.execute(cmd)
    
    def insert_and_commit(self, cmd):
        self.cursor.execute(cmd)
        self.cnx.commit()
    
    def verify_user(self, username, password):
        self.cursor.execute(f'SELECT * from users where username = "{username}" and passw = "{password}"')

        if self.cursor.fetchone():
            return True
        else:
            return False
        
    def create_user(self, user):
        import random
        try:
            self.cursor.execute(f'SELECT * from users where username = "{user}";')
            if not self.cursor.fetchone():
                
                senha = ''.join([random.choice('abcdefghijklmnopqrstuvwxyz0123456789%^*-_=+') for i in range(10)])
                
                self.cursor.execute(f"insert into users(username, passw, created_by) values('{user}', '{senha}', 9);")
                self.cnx.commit()

                return {'Code':200, 'Status':'OK', 'Resultado':[user, senha]}
            else:
                return {'Code':409, 'Status':f'Usuario ja cadastrado na plataforma', 'Resultado':None}
        except Exception as erro:
            return {'Code':500, 'Status':f'Erro create_user: "{erro}"', 'Resultado':None}
        
    def register_user(self, user, passw):

        try:
            self.cursor.execute(f'SELECT * from users where username = "{user}";')
            if not self.cursor.fetchone():
                
                self.cursor.execute(f"insert into users(username, passw, created_by) values('{user}', '{passw}', 9);")
                self.cnx.commit()

                return {'Code':200, 'Status':'OK', 'Resultado':[user, passw]}
            else:
                return {'Code':409, 'Status':f'Usuario ja cadastrado na plataforma', 'Resultado':None}
        except Exception as erro:
            return {'Code':500, 'Status':f'Erro create_user: "{erro}"', 'Resultado':None}
        
    def SelectAndUpdatePending_fgts(self):

        self.cursor.callproc('SelectAndUpdatePending_fgts')

        for result in self.cursor.stored_results():
            return result.fetchall()
            
    def SelectAndUpdatePending_in100(self):

        self.cursor.callproc('SelectAndUpdatePending_in100')

        for result in self.cursor.stored_results():
            return result.fetchall()
        
#print(DATABASE().execute_fetch_all("select * from users inner join user_score on users.users_id = user_score.users_id where username = 'gabrielyudenich';"))
    
#print(DATABASE().SelectAndUpdatePending_in100())
