from flask import Flask, render_template, redirect, url_for, request, make_response, send_file
import datetime, json, assets, database

app = Flask(__name__, template_folder='templates', static_folder='static')

@app.route("/criar_usuario", methods=['GET', 'POST'])
def criar_usuario():
    result = None

    username = request.cookies.get('token_username')

    auth=database.DATABASE().execute_fetch_all(f'select perm_super from users where username = "{username}";')

    if not auth:
        return 'Nao autorizado'
    
    if request.method == 'POST': 
        result = assets.create_user(request.form['user_novo'])
    
    return render_template('admin_create.html', resultado=result, username=username)

@app.route("/gerenc_saldo", methods=['GET', 'POST'])
def gerenc_saldo():

    opt_saldo = ['IN100', 'FGTS', 'Desbloqueio', 'Lote IN100', 'Lote FGTS']

    result = None

    username = request.cookies.get('token_username')

    auth=database.DATABASE().execute_fetch_all(f'select perm_super from users where username = "{username}";')

    if not auth:
        return 'Nao autorizado'
    
    if request.method == 'POST':
        select_user = request.form.get('comp_select')
        opt_select = request.form.get('mod_select')
        cred = request.form['add_cred']

        if opt_select == 'IN100':
            result = assets.saldo_in100(select_user, cred)
        elif opt_select == 'FGTS':
            result = assets.saldo_fgts(select_user, cred)
        elif opt_select == 'Desbloqueio':
            result = assets.saldo_desbl(select_user, cred)
        elif opt_select == 'Lote IN100':
            result = assets.saldo_lote_in100(select_user, cred)
        elif opt_select == 'Lote FGTS':
            result = assets.saldo_lote_FGTS(select_user, cred)
        else:
            result = 'Erro interno'

    usuario=database.DATABASE().execute_fetch_all('select username from users;')
    
    return render_template('admin_saldo.html', resultado=result, usuario=usuario, opt_saldo=opt_saldo)

@app.route("/gerenc_log", methods=['GET', 'POST'])
def gerenc_log():
    result = None

    username = request.cookies.get('token_username')

    auth=database.DATABASE().execute_fetch_all(f'select perm_super from users where username = "{username}";')

    if not auth:
        return 'Nao autorizado'
    
    if request.method == 'POST':
        select_user = request.form.get('comp_select')
        result = assets.log_api(select_user)

    usuario=database.DATABASE().execute_fetch_all('select username from users;')
    
    return render_template('admin_log.html', resultado=result, usuario=usuario)

@app.route('/painel', methods=['GET'])
def painel():
    username = request.cookies.get('token_username')
    expires = request.cookies.get('login_expires')

    if not username:
        return redirect(url_for("login"))

    user_data = database.DATABASE().execute_fetch_all(f"select * from users inner join user_score on users.users_id = user_score.users_id where username = '{username}';")[0]
    permissao = ['desbloqueio', 'lote_fgts', 'lote_in100']

    in100_perm = user_data[3]
    fgts_perm = user_data[4]
    super_perm = user_data[5]

    if in100_perm == 1:
        permissao.append('IN100')
    if fgts_perm == 1:
        permissao.append('fgts')

    creditos_in100 = user_data[10]
    creditos_fgts = user_data[9]

    if datetime.datetime.now() > datetime.datetime.strptime(expires, '%Y-%m-%d %H:%M:%S.%f'):
        return redirect(url_for("login"))

    return render_template('painel_new.html', username=username, creditos_in100=creditos_in100, creditos_fgts=creditos_fgts, creditos_in100_lote=user_data[12], saldo_desbloqueio=user_data[11], creditos_fgts_lote=user_data[13], permissao=permissao, super_perm=super_perm)

@app.route('/', methods=['GET', 'POST'])
def login(error=None):
    if request.method == 'POST':

        username = request.form['username']
        passw = request.form['password']

        ver = database.DATABASE().verify_user(username, passw)

        if ver:
            resp = make_response(redirect(url_for('painel')))
            resp.set_cookie('token_username', request.form['username'])
            resp.set_cookie('login_expires', f'{datetime.datetime.now() + datetime.timedelta(hours=60)}')
            return resp
        else:
            error = 'Invalid Credentials. Please try again.'
    
    return render_template('index_login.html', error=error)

@app.route('/IN100', methods=['GET', 'POST'])
def IN100(resultado=None):

    import re

    username = request.cookies.get('token_username')
    expires = request.cookies.get('login_expires')

    if username:

        user_data = database.DATABASE().execute_fetch_all(f"select * from users inner join user_score on users.users_id = user_score.users_id where username = '{username}';")[0]

        creditos_in100 = user_data[10]

        permissao = ['desbloqueio']

        in100_perm = user_data[3]
        fgts_perm = user_data[4]

        if in100_perm == 1:
            permissao.append('IN100')
        if fgts_perm == 1:
            permissao.append('fgts')

        if permissao.count('IN100') < 1:
            return redirect(url_for('painel'))

        if datetime.datetime.now() > datetime.datetime.strptime(expires, '%Y-%m-%d %H:%M:%S.%f'):
            return redirect(url_for("login"))

        if request.method == 'POST':

            cpf = ''.join(re.findall(r'\d+', request.form['CPF']))
            nb = ''.join(re.findall(r'\d+', request.form['NB']))
            cpf_rep = ''.join(re.findall(r'\d+', request.form['cpf_rep']))

            resultado, user_para_log = assets.ins_api_interno(cpf, nb, username, rep=cpf_rep)

            resultado_res = resultado['Resultado']
            resultado_res = str(resultado_res).replace('{', '').replace('}', '').replace("'", "")

            status_res = resultado['Status']

            database.DATABASE().insert_and_commit(f"insert into pending(users_id, cpf, nb, cpf_rep, status_process, in100_data, status_code, log_user) values ((SELECT users_id FROM users WHERE username = '{username}'), '{cpf}', '{nb}', '{cpf_rep}', '{resultado_res}', 1, {status_res}, '{user_para_log}');")

            creditos_in100 = int(creditos_in100) - 1

        return render_template('ins_new.html', username=username, creditos_in100=creditos_in100, creditos_fgts=user_data[9], creditos_in100_lote=user_data[12], saldo_desbloqueio=user_data[11], resultado=resultado)
    else:
        return redirect(url_for("login"))

@app.route('/fgts', methods=['GET', 'POST'])
def fgts(resultado=None):
    username = request.cookies.get('token_username')
    expires = request.cookies.get('login_expires')

    if username:

        user_data = database.DATABASE().execute_fetch_all(f"select * from users inner join user_score on users.users_id = user_score.users_id where username = '{username}';")[0]

        creditos_fgts = user_data[10]

        permissao = ['desbloqueio']

        fgts_perm = user_data[4]

        if fgts_perm == 1:
            permissao.append('fgts')

        if permissao.count('fgts') < 1:
            return redirect(url_for('painel'))
        
        def atualizar_pendente():
            return database.DATABASE().execute_fetch_all(f"select cpf, status_process, last_update from pending where users_id = (select users_id from users where username = '{username}') and fgts_data = 1 ORDER BY last_update DESC LIMIT 25;")

        if request.method == 'POST':
            resultado = assets.fgts_api_interno(request.form['CPF'], username)

            cpf = request.form['CPF']

            resultado_res = resultado['Resultado']
            resultado_res = str(resultado_res).replace('{', '').replace('}', '').replace("'", "")

            status_res = resultado['Status']

            database.DATABASE().insert_and_commit(f"insert into pending(users_id, cpf, status_process, fgts_data, status_code) values ((SELECT users_id FROM users WHERE username = '{username}'), '{cpf}', '{resultado_res}', 1, {status_res});")

            creditos_fgts = int(creditos_fgts) - 1

        return render_template('fgts.html', username=username, creditos_fgts=creditos_fgts, resultado=resultado, lista_pendente=atualizar_pendente())
    else:
        return redirect(url_for("login"))

@app.route('/desbloqueio', methods=['GET', 'POST'])
def desbloqueio(result=None, erro=None):
    
    username = request.cookies.get('token_username')

    auth=database.DATABASE().execute_fetch_all(f'select perm_super from users where username = "{username}";')

    if auth[0][0] == 0:
        superuser = False
    else:
        superuser = True

    result, desbloqueados = assets.update_html_result(username, superuser)

    key_valid = database.DATABASE().execute_fetch_one(f"select * from users inner join user_score on users.users_id = user_score.users_id where username = '{username}';")

    if request.method == 'POST':
        if key_valid:
            if key_valid[11] > 0:
                if 'desbloquear_botao' in request.form:
                    reembolso = False
                    if request.form['stts_liberacao'] == 'Cancelado':
                        reembolso = True
                        status_desb = 499
                        desbl_auth = 0
                    elif request.form['stts_liberacao'] == 'Concluido':
                        status_desb = 200
                        desbl_auth = 0
                    elif request.form['stts_liberacao'] == 'Em processamento':
                        print('meu cu')
                        status_desb = 202
                        desbl_auth = 1
                    assets.desbloqueio(username=username, desbl_auth=desbl_auth, botao=1, status_desb=status_desb, status_process=request.form['stts_liberacao'], obs_liberacao=request.form['obs_liberacao'], nb_liberacao=request.form['nb_liberacao'], reembolso=reembolso)
                    return redirect(url_for('desbloqueio', mensagem='Sistema atualizado com sucesso.')) 
                if 'solicitar_botao' in request.form:
                    cpf = request.form['CPF']
                    nb = request.form['NB']
                    cpf_rep = request.form['cpf_rep']
                    assets.desbloqueio(cpf=cpf, nb=nb, cpf_rep=cpf_rep, username=username, botao=2)
                    return redirect(url_for('desbloqueio', mensagem='Desbloqueio enviado com sucesso.'))
                
                result, desbloqueados = assets.update_html_result(username, superuser)
            else:
                erro = 'Sem saldo o suficiente para essa operação.'
    
    return render_template('desbloqueio.html', username=username, resultado=result, superuser=superuser, desbloqueados=desbloqueados, erro=erro, saldo_desbloqueio=key_valid[11], creditos_in100=key_valid[10], creditos_fgts=key_valid[9], creditos_in100_lote=key_valid[12])

@app.route('/lote_in100', methods=['GET', 'POST'])
def lote_in100():

    username = request.cookies.get('token_username')

    ready, result = assets.update_html_result_lote_in100(username)

    return render_template('in100_lote_upload.html', result=result, username=username)

@app.route('/lote_fgts', methods=['GET', 'POST'])
def lote_fgts():

    username = request.cookies.get('token_username')

    auth=database.DATABASE().execute_fetch_all(f'select perm_super from users where username = "{username}";')

    if auth[0][0] == 0:
        superuser = False
    else:
        superuser = True

    ready, result = assets.update_html_result_lote_fgts(username)

    return render_template('fgts_lote_upload.html', result=result, username=username, superuser=superuser)

@app.route('/upload_in100', methods=['POST'])
def upload_arquivo_in100():

    import os, pandas

    username = request.cookies.get('token_username')

    key_valid = database.DATABASE().execute_fetch_one(f"select * from users inner join user_score on users.users_id = user_score.users_id where username = '{username}';")

    if 'arquivo' not in request.files:
        return redirect(url_for('lote_in100', mensagem='Nenhum arquivo enviado.'))

    arquivo = request.files['arquivo']

    if arquivo.filename == '':
        return redirect(url_for('lote_in100', mensagem='Nenhum arquivo selecionado.'))

    if key_valid:
        if key_valid[12] > 0:

            arquivo_path = os.path.join('uploads', arquivo.filename)
            arquivo.save(arquivo_path)

            # Verificar se o arquivo é um arquivo Excel (.xlsx)
            if arquivo.filename.endswith('.xlsx'):
                
                try:
                    df = pandas.read_excel(arquivo_path)

                    if int(len(df)) > int(key_valid[12]):
                        return redirect(url_for('lote_in100', mensagem='Usuário com saldo insuficiente para realizar a ação.'))

                    reg_lote = assets.insert_lote_in100(username, df)

                    return redirect(url_for('lote_in100', mensagem=f"Arquivo enviado para processamento com sucesso. ID do lote [{reg_lote}]"))
                except Exception as e:
                    return redirect(url_for('lote_in100', mensagem=f"Ocorreu um erro durante a conversão: {str(e)}"))
            else:
                return redirect(url_for('lote_in100', mensagem='Arquivo enviado não é um Excel válido.'))
            
        return redirect(url_for('lote_in100', mensagem='Usuário com saldo insuficiente para realizar a ação.'))
    
@app.route('/upload_fgts', methods=['POST'])
def upload_arquivo_fgts():

    import os, pandas

    username = request.cookies.get('token_username')

    key_valid = database.DATABASE().execute_fetch_one(f"select * from users inner join user_score on users.users_id = user_score.users_id where username = '{username}';")

    if 'arquivo' not in request.files:
        return redirect(url_for('lote_fgts', mensagem='Nenhum arquivo enviado.'))

    arquivo = request.files['arquivo']

    if arquivo.filename == '':
        return redirect(url_for('lote_fgts', mensagem='Nenhum arquivo selecionado.'))

    if key_valid:
        if key_valid[13] > 0:

            arquivo_path = os.path.join('uploads', arquivo.filename)
            arquivo.save(arquivo_path)

            if arquivo.filename.endswith('.xlsx'):
                
                try:
                    df = pandas.read_excel(arquivo_path)

                    if int(len(df)) > int(key_valid[13]):
                        return redirect(url_for('lote_fgts', mensagem='Usuário com saldo insuficiente para realizar a ação.'))

                    reg_lote = assets.insert_lote_fgts(username, df)

                    return redirect(url_for('lote_fgts', mensagem=f"Arquivo enviado para processamento com sucesso. ID do lote [{reg_lote}]"))
                except Exception as e:
                    return redirect(url_for('lote_fgts', mensagem=f"Ocorreu um erro durante a conversão: {str(e)}"))
            else:
                return redirect(url_for('lote_fgts', mensagem='Arquivo enviado não é um Excel válido.'))
            
        return redirect(url_for('lote_fgts', mensagem='Usuário com saldo insuficiente para realizar a ação.'))

@app.route('/download_excel_lote')
def download_excel_lote():
    arquivo_path = 'uploads/Modelo_lote_in100.xlsx'  # Caminho para o arquivo na pasta "static"
    return send_file(arquivo_path, as_attachment=True)

@app.route('/download_excel_lote_fgts')
def download_excel_lote_fgts():
    arquivo_path = 'uploads/Modelo_lote_fgts.xlsx'  # Caminho para o arquivo na pasta "static"
    return send_file(arquivo_path, as_attachment=True)

@app.route('/download_lote_finalizado_in100')
def download_lote_finalizado_in100():

    username = request.cookies.get('token_username')

    lote_id = request.args.get('lote_id')

    import io
    buffer = io.BytesIO()

    df = assets.df_result_lote_in100(username, lote_id)
    df.to_excel(buffer, index=False)
    buffer.seek(0)

    return send_file(buffer, as_attachment=True, download_name=f'Lote_{lote_id}.xlsx')

@app.route('/download_lote_finalizado_fgts')
def download_lote_finalizado_fgts():

    username = request.cookies.get('token_username')

    lote_id = request.args.get('lote_id')

    import io
    buffer = io.BytesIO()

    df = assets.df_result_lote_fgts(username, lote_id)
    df.to_excel(buffer, index=False)
    buffer.seek(0)

    return send_file(buffer, as_attachment=True, download_name=f'Lote_{lote_id}.xlsx')

@app.route("/cadastro", methods=['GET', 'POST'])
def cadastro():
    warning = None

    if request.method == 'POST': 

        if request.form['Senha'] == request.form['senha_rep']:

            warning = assets.register_user(request.form['Usuario'], request.form['Senha'])

        else:

            warning = {'Status':301, 'Resultado':'Senhas não coincidem.'}
    
    return render_template('register.html', warning=warning)

@app.route('/busca_cpf', methods=['GET', 'POST'])
def busca_cpf(result=None, erro=None):
    
    username = request.cookies.get('token_username')

    key_valid = database.DATABASE().execute_fetch_one(f"select * from users inner join user_score on users.users_id = user_score.users_id where username = '{username}';")

    if request.method == 'POST':
        if key_valid:
            if key_valid[14] > 0:
                cpf = request.form['CPF']
                result = assets.busca_cpf(cpf=cpf, username=username)
            else:
                erro = 'Sem saldo o suficiente para essa operação.'
    
    return render_template('busca_cpf.html', username=username, resultado=result, erro=erro)

@app.route('/busca_nome', methods=['GET', 'POST'])
def busca_nome(result=None, erro=None):
    
    username = request.cookies.get('token_username')

    key_valid = database.DATABASE().execute_fetch_one(f"select * from users inner join user_score on users.users_id = user_score.users_id where username = '{username}';")

    if request.method == 'POST':
        if key_valid:
            if key_valid[14] > 0:
                nome = request.form['Nome']
                result = assets.busca_nome(nome, username)
                print(result)
            else:
                erro = 'Sem saldo o suficiente para essa operação.'
    
    return render_template('busca_nome.html', username=username, resultado=result, erro=erro)

@app.route('/deletar_lote')
def deletar_lote():
    lote = request.args.get('lote_id')
    tipo = request.args.get('type')
    assets.deletar_lote(lote)
    if tipo == 'fgts':
        return redirect(url_for('lote_fgts')) 
    else:
        return redirect(url_for('lote_in100')) 
    
@app.route('/resetar_lotes')
def resetar_lotes():
    tipo = request.args.get('type')
    assets.resetar_lotes()
    if tipo == 'fgts':
        return redirect(url_for('lote_fgts')) 
    else:
        return redirect(url_for('lote_in100')) 

@app.route('/logout', methods=['GET'])
def logout():
    resp = make_response(redirect(url_for('login')))
    resp.set_cookie('token_username', '')
    resp.set_cookie('login_expires', '')
    return resp

if __name__ == '__main__': 
   app.run(debug=True, host='0.0.0.0', port=80, threaded=True)
