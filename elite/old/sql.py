import sqlite3, datetime, json

class db_sql(object):

    def __init__(self):
        self.connection = sqlite3.connect('dados.db')
        self.c = self.connection.cursor()

    def execute(self, sql):
        self.c.execute(sql)
        return self.connection.commit()
    
    def return_data(self, sql):
        self.c.execute(sql)
        return self.c.fetchall()

text = {"ins":1,"receita":0,"nome":0,"interpol":0,"gerenc_log":0}

json_texto = json.dumps(text)

print(
    db_sql().execute(f'CREATE TABLE IF NOT EXISTS user_log(cpf text, nb text, cpf_rep text, res text, user text, date_time text);')
    #db_sql().execute(f'ALTER TABLE user_log ADD date_time text;')
    #db_sql().execute('ALTER TABLE users ADD last_login text;')
    #db_sql().return_data('SELECT * from users where user="gabrielyudenich"')
)