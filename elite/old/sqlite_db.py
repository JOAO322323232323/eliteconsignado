import sqlite3
 
class db_sql(object):

    def __init__(self):
        self.connection = sqlite3.connect('elite/dados.db')
        self.c = self.connection.cursor()

    def verify_user(self, user, passw):
        self.c.execute(f'SELECT * FROM users where user="{user}" and senha="{passw}"')
        if self.c.fetchone():
            return True
        else:
            return False
        
    def return_user(self, user):
        self.c.execute(f'SELECT * FROM users where user="{user}"')
        return self.c.fetchone()
    
    def return_all_users(self):
        self.c.execute('SELECT user FROM users')
        return self.c.fetchall()