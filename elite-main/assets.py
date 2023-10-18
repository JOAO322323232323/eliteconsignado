import api, database, fgts_facta, pandas, assets_js, json, requests, httpx

def is_valid_cpf(cpf):
    # Remover caracteres não numéricos
    cpf = ''.join(filter(str.isdigit, cpf))
    
    # Verificar se o CPF tem 11 dígitos
    if len(cpf) != 11:
        return False
    
    # Calcular o primeiro dígito verificador
    total = 0
    for i in range(9):
        total += int(cpf[i]) * (10 - i)
    remainder = total % 11
    digit1 = 0 if remainder < 2 else 11 - remainder
    
    # Verificar o primeiro dígito verificador
    if int(cpf[9]) != digit1:
        return False
    
    # Calcular o segundo dígito verificador
    total = 0
    for i in range(10):
        total += int(cpf[i]) * (11 - i)
    remainder = total % 11
    digit2 = 0 if remainder < 2 else 11 - remainder
    
    # Verificar o segundo dígito verificador
    if int(cpf[10]) != digit2:
        return False
    
    return True
    
def saldo_in100(user, saldo):

    database.DATABASE().insert_and_commit(f"INSERT INTO user_score (users_id, score_in100) VALUES ((SELECT users_id FROM users WHERE username = '{user}'), {saldo}) ON DUPLICATE KEY UPDATE score_in100 = score_in100 +{saldo};")
    dado = database.DATABASE().execute_fetch_all(f"select score_in100 from users inner join user_score on users.users_id = user_score.users_id where username = '{user}';")
    return {'Status':200, 'Resultado':f'Saldo adicionado, novo saldo do usuario para in100: "{dado[0]}"', 'Saldo':0, 'Usuario':'Admin'}

def saldo_fgts(user, saldo):
    database.DATABASE().insert_and_commit(f"INSERT INTO user_score (users_id, score_fgts) VALUES ((SELECT users_id FROM users WHERE username = '{user}'), {saldo}) ON DUPLICATE KEY UPDATE score_fgts = score_fgts +{saldo};")
    dado = database.DATABASE().execute_fetch_all(f"select score_fgts from users inner join user_score on users.users_id = user_score.users_id where username = '{user}';")
    return {'Status':200, 'Resultado':f'Saldo adicionado, novo saldo do usuario para FGTS: "{dado[0]}"', 'Saldo':0, 'Usuario':'Admin'}

def saldo_desbl(user, saldo):
    database.DATABASE().insert_and_commit(f"INSERT INTO user_score (users_id, score_desbl) VALUES ((SELECT users_id FROM users WHERE username = '{user}'), {saldo}) ON DUPLICATE KEY UPDATE score_desbl = score_desbl +{saldo};")
    dado = database.DATABASE().execute_fetch_all(f"select score_desbl from users inner join user_score on users.users_id = user_score.users_id where username = '{user}';")
    return {'Status':200, 'Resultado':f'Saldo adicionado, novo saldo do usuario para desbloqueio: "{dado[0]}"', 'Saldo':0, 'Usuario':'Admin'}

def saldo_lote_in100(user, saldo):
    database.DATABASE().insert_and_commit(f"INSERT INTO user_score (users_id, score_l_in100) VALUES ((SELECT users_id FROM users WHERE username = '{user}'), {saldo}) ON DUPLICATE KEY UPDATE score_l_in100 = score_l_in100 +{saldo};")
    dado = database.DATABASE().execute_fetch_all(f"select score_l_in100 from users inner join user_score on users.users_id = user_score.users_id where username = '{user}';")
    return {'Status':200, 'Resultado':f'Saldo adicionado, novo saldo do usuario para desbloqueio: "{dado[0]}"', 'Saldo':0, 'Usuario':'Admin'}
    
def saldo_lote_FGTS(user, saldo):
    database.DATABASE().insert_and_commit(f"INSERT INTO user_score (users_id, score_l_fgts) VALUES ((SELECT users_id FROM users WHERE username = '{user}'), {saldo}) ON DUPLICATE KEY UPDATE score_l_fgts = score_l_fgts +{saldo};")
    dado = database.DATABASE().execute_fetch_all(f"select score_l_fgts from users inner join user_score on users.users_id = user_score.users_id where username = '{user}';")
    return {'Status':200, 'Resultado':f'Saldo adicionado, novo saldo do usuario para desbloqueio: "{dado[0]}"', 'Saldo':0, 'Usuario':'Admin'}
    
def log_api(user):
    dado = database.DATABASE().execute_fetch_all(f"select cpf, nb, cpf_rep, status_process, last_update, status_code, log_user from users inner join pending on users.users_id = pending.users_id where username = '{user}' order by last_update desc;")
    return {'Status':200, 'Resultado':dado, 'Saldo':0, 'Usuario':'Admin'}

def create_user(user):
    
    dado = database.DATABASE().create_user(user)
    if dado['Code'] == 409:
        return {'Status':409, 'Resultado':'Usuario ja cadastrado', 'Saldo':0, 'Usuario':'Admin'}
    saldo_in100(user, 0)
    saldo_fgts(user, 0)
    saldo_desbl(user, 0)
    return {'Status':200, 'Resultado':f'Novo usuario cadastrado com sucesso, user "{dado}"', 'Saldo':0, 'Usuario':'Admin', 'ListUser':dado}

def register_user(user, passw):
    
    dado = database.DATABASE().register_user(user, passw)
    if dado['Code'] == 409:
        return {'Status':409, 'Resultado':'Usuario ja cadastrado', 'Saldo':0, 'Usuario':'Admin'}
    saldo_in100(user, 0)
    saldo_fgts(user, 0)
    saldo_desbl(user, 0)
    return {'Status':200, 'Resultado':'Novo usuario cadastrado com sucesso', 'Saldo':0, 'Usuario':'Admin', 'ListUser':dado}


def saldo_user(key):
    key_valid = database.DATABASE().execute_fetch_one(f"select * from users inner join user_score on users.users_id = user_score.users_id where username = '{key}';")
    if not key:
        return {'Status':403, 'Saldo IN100':0, 'Saldo FGTS':0, 'Saldo Desbloqueio':0, 'Usuario':'Não autenticado.'}
    return {'Status':200, 'Saldo IN100':(key_valid[10]), 'Saldo FGTS':(key_valid[9]), 'Saldo Desbloqueio':(key_valid[11]), 'Usuario':key_valid[1]}

def ins_api_interno(cpf, nb, key, rep=None):
    key_valid = database.DATABASE().execute_fetch_one(f"select * from users inner join user_score on users.users_id = user_score.users_id where username = '{key}';")

    if key_valid:
        if key_valid[10] > 0:

            if not is_valid_cpf(cpf):
                return {'Status':403, 'Resultado':'Nao autorizado. Numero de CPF INCORRETO.', 'Saldo':int(key_valid[10]), 'Usuario':key_valid[1]}, 0
            if nb == None:
                return {'Status':403, 'Resultado':'Nao autorizado. Numero de Beneficio obrigatorio.', 'Saldo':int(key_valid[10]), 'Usuario':key_valid[1]}, 0
            elif nb == '':
                return {'Status':403, 'Resultado':'Nao autorizado. Numero de Beneficio obrigatorio.', 'Saldo':int(key_valid[10]), 'Usuario':key_valid[1]}, 0
            elif len(str(nb)) < 10:
                return {'Status':403, 'Resultado':'Nao autorizado. Numero de BENEFICIO INCORRETO.', 'Saldo':int(key_valid[10]), 'Usuario':key_valid[1]}, 0
            elif cpf == None:
                return {'Status':403, 'Resultado':'Nao autorizado. Numero de CPF obrigatorio.', 'Saldo':int(key_valid[10]), 'Usuario':key_valid[1]}, 0
            elif cpf == '':
                return {'Status':403, 'Resultado':'Nao autorizado. Numero de CPF obrigatorio.', 'Saldo':int(key_valid[10]), 'Usuario':key_valid[1]}, 0


            try:
                json, usuario_log = api.API_qmc().main(cpf, nb, cpf_rep=rep)

                if json == 103:
                    return {'Status':103, 'Resultado':f'Necessario representante legal. Seu saldo nao sera subtraido nesta consulta.', 'Saldo':int(key_valid[10]), 'Usuario':key_valid[1]}, usuario_log

                if json == 104:
                    return {'Status':104, 'Resultado':f'Beneficio inexistente. Seu saldo nao sera subtraido nesta consulta.', 'Saldo':int(key_valid[10]), 'Usuario':key_valid[1]}, usuario_log

                if json == 105:
                    return {'Status':105, 'Resultado':f'Dados nao localizados, tente novamente mais tarde. Seu saldo nao sera subtraido nesta consulta.', 'Saldo':int(key_valid[10]), 'Usuario':key_valid[1]}, usuario_log

                if json == 106:
                    return {'Status':106, 'Resultado':f'Dados nao localizados ou CPF inelegivel, tente novamente mais tarde. Seu saldo nao sera subtraido nesta consulta.', 'Saldo':int(key_valid[10]), 'Usuario':key_valid[1]}, usuario_log
                
                if not json:
                    database.DATABASE().insert_and_commit(f"INSERT INTO in100_logins (login, tentativas) VALUES ('{usuario_log}', -1) ON DUPLICATE KEY UPDATE tentativas = tentativas -1;")
                    return {'Status':500, 'Resultado':f'inss fora do ar no momento, tente novamente mais tarde. Seu saldo nao sera subtraido nesta consulta.', 'Saldo':int(key_valid[10]), 'Usuario':key_valid[1]}, usuario_log

                database.DATABASE().insert_and_commit(f"INSERT INTO user_score (users_id, score_in100) VALUES ((SELECT users_id FROM users WHERE username = '{key}'), -1) ON DUPLICATE KEY UPDATE score_in100 = score_in100 -1;")

                return {'Status':200, 'Resultado':json, 'Saldo':int(key_valid[10])-1, 'Usuario':key_valid[1]}, usuario_log
            
            except Exception as f:
                return {'Status':500, 'Resultado':f'Erro interno: {f}. Seu saldo nao sera subtraido nesta consulta.', 'Saldo':int(key_valid[10]), 'Usuario':key_valid[1]}, 0
        else:
            return {'Status':402, 'Resultado':'Saldo indisponivel para realizar a solicitacao.', 'Saldo':int(key_valid[10]), 'Usuario':key_valid[1]}, 0
    else:
        return {'Status':403, 'Resultado':'Nao autorizado.', 'Saldo':0, 'Usuario':'Não reconhecido'}, 0
    
def fgts_api_interno(cpf, user):

    key_valid = database.DATABASE().execute_fetch_one(f"select * from users inner join user_score on users.users_id = user_score.users_id where username = '{user}';")

    if key_valid:
        if key_valid[9] > 0:

            fgts_retorno = fgts_facta.FGTS_API().get_fgts(cpf)

            if fgts_retorno['Status'] == 200:
                database.DATABASE().insert_and_commit(f"INSERT INTO user_score (users_id, score_fgts) VALUES ((SELECT users_id FROM users WHERE username = '{user}'), -1) ON DUPLICATE KEY UPDATE score_fgts = score_fgts -1;")
            return fgts_retorno
        else:
            return {'Status':402, 'Resultado':'Saldo indisponivel para realizar a solicitacao.', 'Saldo':int(key_valid[9]), 'Usuario':key_valid[1]}
        
def desbloqueio(username, cpf=None, nb=None, cpf_rep=None, botao=1, status_desb=None, status_process=None, obs_liberacao=None, desbl_auth=None, nb_liberacao=None, reembolso=False):
    if botao == 1:
        database.DATABASE().insert_and_commit(f"update pending set status_code = {status_desb}, status_process = '{status_process}', obs = '{obs_liberacao}', desbl_user = (select users_id from users where username = '{username}'), desbl_auth = {desbl_auth} where nb = '{nb_liberacao}' and desbl_auth = 1;")
        if reembolso:
            database.DATABASE().insert_and_commit(f"INSERT INTO user_score (users_id, score_desbl) VALUES ((select pending.users_id from pending inner join users on users.users_id = pending.users_id where nb = '{nb_liberacao}'), + 1) ON DUPLICATE KEY UPDATE score_desbl = score_desbl + 1;")
    elif botao == 2:
        database.DATABASE().insert_and_commit(f"insert into pending(users_id, cpf, nb, cpf_rep, status_code, status_process, desbl_auth) values((select users_id from users where username = '{username}'), '{cpf}', '{nb}', '{cpf_rep}', 202, 'Pendente de desbloqueio', 1);")
        database.DATABASE().insert_and_commit(f"INSERT INTO user_score (users_id, score_desbl) VALUES ((SELECT users_id FROM users WHERE username = '{username}'), -1) ON DUPLICATE KEY UPDATE score_desbl = score_desbl -1;")

def update_html_result(username, super_user=False):
    if super_user:
        result = database.DATABASE().execute_fetch_all(f'select username, cpf, nb, cpf_rep, status_process, obs from users inner join pending on users.users_id = pending.users_id where desbl_auth = 1;')
        desbloqueados = database.DATABASE().execute_fetch_all(f'select username, cpf, nb, cpf_rep, status_process, obs from users inner join pending on users.users_id = pending.users_id where desbl_auth = 0;')
    else:
        result = database.DATABASE().execute_fetch_all(f'select cpf, nb, cpf_rep, status_process, obs from users inner join pending on users.users_id = pending.users_id where username = "{username}" and desbl_auth = 1;')
        desbloqueados = database.DATABASE().execute_fetch_all(f'select cpf, nb, cpf_rep, status_process, obs from users inner join pending on users.users_id = pending.users_id where username = "{username}" and desbl_auth = 0;')
    return result, desbloqueados

def insert_lote_in100(username, dataframe):

    unique_id = assets_js.generate_k()

    for line in dataframe.iterrows():

        cpf = str(line[1].CPF)
        cpf = ''.join(filter(str.isdigit, cpf))

        nb = str(line[1].NB)
        nb = ''.join(filter(str.isdigit, nb))

        cpf_rep = str(line[1].CPF_REP)

        if cpf_rep == 'nan' or cpf_rep == 'NaN':
            cpf_rep = None
        else:
            cpf_rep = ''.join(filter(str.isdigit, cpf_rep))

        cpf = formatar_cpf(cpf)

        if is_valid_cpf(cpf):

            database.DATABASE().insert_and_commit(f"insert into pending(users_id, cpf, nb, cpf_rep, lote_in100, status_code, unique_id) values((SELECT users_id FROM users WHERE username = '{username}'), '{cpf}', '{nb}', '{cpf_rep}', 1, 202, '{unique_id}')")

    return unique_id

def insert_lote_fgts(username, dataframe):

    unique_id = assets_js.generate_k()

    for line in dataframe.iterrows():

        cpf = str(line[1].CPF)
        cpf = ''.join(filter(str.isdigit, cpf))
        cpf = formatar_cpf(cpf)

        if is_valid_cpf(cpf):

            database.DATABASE().insert_and_commit(f"insert into pending(users_id, cpf, lote_fgts, status_code, unique_id) values((SELECT users_id FROM users WHERE username = '{username}'), '{cpf}', 1, 202, '{unique_id}')")

    return unique_id

def update_html_result_lote_in100(username, unique_id=None):

    result = database.DATABASE().execute_fetch_all(f'SELECT unique_id, COUNT(*) AS total, COUNT(CASE WHEN status_code = 202 THEN 1 END) AS nao_processado, COUNT(CASE WHEN status_code <> 202 THEN 1 END) AS processado FROM users INNER JOIN pending ON users.users_id = pending.users_id WHERE username = "{username}" AND lote_in100 = 1 GROUP BY unique_id;')
    ready = database.DATABASE().execute_fetch_all(f'select cpf, nb, cpf_rep, status_process, unique_id from users inner join pending on users.users_id = pending.users_id where username = "{username}" and lote_in100 = 1 and status_code = 200 and unique_id = "{unique_id}";')

    return ready, result

def update_html_result_lote_fgts(username, unique_id=None):

    result = database.DATABASE().execute_fetch_all(f'SELECT unique_id, COUNT(*) AS total, COUNT(CASE WHEN status_code = 202 THEN 1 END) AS nao_processado, COUNT(CASE WHEN status_code <> 202 THEN 1 END) AS processado FROM users INNER JOIN pending ON users.users_id = pending.users_id WHERE username = "{username}" AND lote_fgts = 1 GROUP BY unique_id;')
    ready = database.DATABASE().execute_fetch_all(f'select cpf, status_process, unique_id from users inner join pending on users.users_id = pending.users_id where username = "{username}" and lote_fgts = 1 and status_code = 200 and unique_id = "{unique_id}";')

    return ready, result

def df_result_lote_in100(username, unique_id):

    ready, result = update_html_result_lote_in100(username, unique_id)

    return pandas.DataFrame(ready, columns=['CPF', 'Numero de beneficio', 'CPF Representante', 'Resultado', 'ID do Lote'])

def df_result_lote_fgts(username, unique_id):

    ready, result = update_html_result_lote_fgts(username, unique_id)

    return pandas.DataFrame(ready, columns=['CPF', 'Resultado', 'ID do Lote'])

def busca_cpf(cpf, username):

    token = database.DATABASE().execute_fetch_one("select token from api_tokens where descr = 'painel_busca';")[0]

    headers = {'User-Agent':"DysonLink/29019 CFNetwork/1188 Darwin/20.0.0",
               'Server': 'cloudflare'}

    with httpx.Client(headers=headers) as client:
        timeout = httpx.Timeout(30.0)
        res = client.get(f"https://apisdedicado.nexos.dev/SerasaCpf/cpf?token={token}&cpf={cpf}", timeout=timeout).text
        print(res)
    
    return json.loads(res)

def busca_nome(nome, username):

    token = database.DATABASE().execute_fetch_one("select token from api_tokens where descr = 'painel_busca';")[0]
    return json.loads(requests.get(f"https://apisdedicado.nexos.dev/SerasaNome/nome?token={token}&nome='{nome}'").text)

def deletar_lote(lote_id):
    database.DATABASE().insert_and_commit(f"delete from pending where unique_id = '{lote_id}';")

def resetar_lotes():
    database.DATABASE().insert_and_commit("update pending set selected_flag = 0, status_code = 202 where last_update > DATE_SUB(NOW(), INTERVAL 1 HOUR) and status_code = 300;")

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

def formatar_cpf(cpf):

    if len(str(cpf)) < 11:
        # Remove qualquer caractere não numérico do CPF
        cpf = ''.join(filter(str.isdigit, cpf))

        # Adiciona zeros à esquerda até que tenha 11 dígitos
        cpf = cpf.zfill(11)

    return cpf

#(busca_cpf('12379737916', ''))