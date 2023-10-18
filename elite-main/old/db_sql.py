import sqlite3

class db_sql(object):

    def __init__(self):
        self.connection = sqlite3.connect('banco_cpf.db')
        self.c = self.connection.cursor()

    def create_table(self):
        self.c.execute("CREATE TABLE IF NOT EXISTS dados(cpf text, nome text, sexo text, data_nascimento text)")

    def insert_table(self, cpf, nome, sexo, data_nascimento):
        self.c.execute(f'INSERT INTO dados VALUES("{cpf}", "{nome}", "{sexo}", "{data_nascimento}")')
        self.connection.commit()

    def execute_main(self, cpf, nome, sexo, data_nascimento):
        self.create_table()
        self.insert_table(cpf, nome, sexo, data_nascimento)
        
    def search_name(self, text):
        self.c.execute(f'SELECT * FROM dados WHERE nome like "%{text}%"')
        return self.c.fetchall()

    def search_date(self, data):
        self.c.execute(f'SELECT * FROM dados WHERE data_nascimento like "%{data}%"')
        print(self.c.fetchall())

'''with open('resultados_piceli.txt', 'w', encoding='utf-8') as file:
    file.write(str(db_sql().search_name('picelli')))'''

print(db_sql().search_name('Natan Martins Camargo'))