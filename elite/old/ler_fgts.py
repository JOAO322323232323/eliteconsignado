import requests, json, pandas, sqlite3, threading, time

connection = sqlite3.connect('fgts_temp.db', check_same_thread=False)
c = connection.cursor()

connection_a = sqlite3.connect('fgts_temp.db', check_same_thread=False)
connection_b = sqlite3.connect('fgts_temp.db', check_same_thread=False)
connection_c = sqlite3.connect('fgts_temp.db', check_same_thread=False)
connection_d = sqlite3.connect('fgts_temp.db', check_same_thread=False)
connection_e = sqlite3.connect('fgts_temp.db', check_same_thread=False)

c_a = connection_a.cursor()
c_b = connection_b.cursor()
c_c = connection_c.cursor()
c_d = connection_d.cursor()
c_e = connection_e.cursor()

c.execute(f'CREATE TABLE IF NOT EXISTS fgts_temp(cpf text, status text);')
connection.commit()

def lock_database(cursor, codigo, connec=connection, commit=False):
    lock = threading.Lock()
    res = 'again'
    try:
        lock.acquire(True)
        res = cursor.execute(codigo)
        if commit:
            connec.commit()
    except:
        lock.release()
        return 'again'
    finally:
        lock.release()
        return res

def formatar_cpf(cpf):
    # Remove qualquer caractere não numérico do CPF
    cpf = ''.join(filter(str.isdigit, cpf))

    # Adiciona zeros à esquerda até que tenha 11 dígitos
    cpf = cpf.zfill(11)

    return cpf

def validar_cpf(cpf):
    # Remove qualquer caractere não numérico do CPF
    cpf = ''.join(filter(str.isdigit, cpf))

    # Adiciona zeros à esquerda até que tenha 11 dígitos
    cpf = cpf.zfill(11)

    # Verifica se todos os dígitos são iguais, o que tornaria o CPF inválido
    if cpf == cpf[0] * 11:
        return False

    # Calcula o primeiro dígito verificador
    soma = 0
    for i in range(9):
        soma += int(cpf[i]) * (10 - i)
    resto = 11 - (soma % 11)
    if resto in (10, 11):
        resto = 0
    if resto != int(cpf[9]):
        return False

    # Calcula o segundo dígito verificador
    soma = 0
    for i in range(10):
        soma += int(cpf[i]) * (11 - i)
    resto = 11 - (soma % 11)
    if resto in (10, 11):
        resto = 0
    if resto != int(cpf[10]):
        return False

    return True

def get_token():
    link = 'https://api.bancoprata.com.br/v1/users/login'

    json_data = {"email":"victor.barros@elitepromotora.com.br","password":"BRASIL@20"}

    headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 OPR/100.0.0.0'}

    res = requests.post(link, json=json_data, headers=headers)

    return json.loads(res.text)['data']['token']

def fgts(cpf):

    print('[FGTS] Testando CPF:', cpf)
    
    try:
        link = f'https://pratadigital.com.br/sistema-cb/v1/qitech/fgts/balance?document={cpf}&rate_id=7'

        headers = {'Authorization':f'Bearer {get_token()}',
                'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 OPR/100.0.0.0'}

        res = requests.get(link, headers=headers)

        res_json = json.loads(res.text)

        try:
            if res_json['error']['message'] == 'O CPF digitado já está na lista de espera. Por gentileza acompanhe e aguarde o resultado.' or res_json['error']['message'] == 'Este CPF já está sendo consultado. Neste momento PENDENTE DE RETORNO DA CAIXA. Por gentileza, aguarde. Não é necessário iniciar nova consulta.':

                link_wait = 'https://pratadigital.com.br/sistema-cb/v1/qitech/fgts/balance-wait-list'

                res_wait = requests.get(link_wait, headers=headers)

                json_data = json.loads(res_wait.text)

                for x in json_data['data']:

                    try:

                        cpf_formated = f'{cpf[0]}{cpf[1]}{cpf[2]}.{cpf[3]}{cpf[4]}{cpf[5]}.{cpf[6]}{cpf[7]}{cpf[8]}-{cpf[9]}{cpf[10]}'

                    except IndexError:

                        return f'CPF formatado incorretamente, {len(cpf)} numeros.'
                    
                    if x['document'] == cpf_formated:

                        if x['status'] == 'failed':
                            return {'Code':401, 'Resultado':x['status_reason']}
                        
                        elif x['status'] == 'pending':
                            return {'Code':402, 'Resultado':'null'}
            elif res_json['error']['message']:
                return {'Code':200, 'Resultado':res_json['error']['message']}
        except:
            data = json.loads(res.text)['data']

            try:
                if data['status'] == 'pending':
                    return {'Code':402, 'Resultado':'null'}
            except:
                pass

            try:
                if data['status'] == 'failed':
                    return {'Code':402, 'Resultado':data['status_reason']}
            except:
                pass

            try:
                return {'Code':200, 'Resultado':data['disbursed_issue_amount']}
            except:
                pass

    except Exception as erro:
        return {'Code':400, 'Resultado':'null'}
    
def inserir_db(arquivo):

    with open(arquivo, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    print('[BANCO DE DADOS] Criando banco de dados')

    c.execute(f'UPDATE fgts_temp SET status = "null" where status = "analisando";')
    connection.commit()

    for line in lines:
        cpf = str(line.strip()).replace('.', '').replace('-', '')
        cpf = formatar_cpf(cpf)

        if validar_cpf(cpf):

            try:
                if not len(c.execute(f'SELECT * FROM fgts_temp WHERE cpf = "{cpf}"').fetchone()) > 0:

                    c.execute(f'INSERT INTO fgts_temp VALUES("{cpf}", "null");')
                    print(f'[BANCO DE DADOS] Inserindo CPF: {cpf}')

                    connection.commit()
                else:
                    print(f'[BANCO DE DADOS] CPF: {cpf} já na base.')
            except:
                c.execute(f'INSERT INTO fgts_temp VALUES("{cpf}", "null");')
                print(f'[BANCO DE DADOS] Inserindo CPF: {cpf}')

                connection.commit()

        else:

            print(f'[SISTEMA] CPF: {cpf} não é válido.')

def fgts_funcao(arquivo, cursor, connection_sett):

    dt = pandas.DataFrame(columns=['CPF', 'Status'])

    #######################
    loop = True

    while loop:

        cursor.execute(f'UPDATE fgts_temp SET status = "null" where status like "%Ops, ocorreu um erro inesperado%";')
        connection_sett.commit()

        dados = cursor.execute('SELECT * from fgts_temp where status = "null" LIMIT 5').fetchall()

        if len(dados) == 0:
            loop = False

        for x in dados:
            
            cpf = x[0]

            try:
                cursor.execute(f'UPDATE fgts_temp SET status = "analisando" where cpf = "{cpf}";')
                connection_sett.commit()

                if validar_cpf(cpf):
                    try:
                        resultado = fgts(cpf)['Resultado']
                    except:
                        resultado = None

                    dt.loc[len(dt)] = [f'{cpf}', resultado]

                    cursor.execute(f'UPDATE fgts_temp SET status = "{resultado}" where cpf = "{cpf}";')
                    connection_sett.commit()

                    dt.to_csv(f'{arquivo}_CSV.csv', sep=';')
            except:
                pass
        
def validar_fgts(arquivo, workers=3):

    inserir_db(arquivo)

    threads = list()

    cursor_list = [c_a, c_b, c_c, c_d, c_e]
    connection_list = [connection_a, connection_b, connection_c, connection_d, connection_e]

    for index in range(workers):
        x = threading.Thread(target=fgts_funcao, args=(arquivo, cursor_list[index], connection_list[index]))
        threads.append(x)
        print(f'[SISTEMA] Iniciado Thread: {index+1}')
        time.sleep(5)
        x.start()

    for index, thread in enumerate(threads):
        thread.join()

#validar_fgts('arquivo.txt', 5)