import pandas, json, requests, datetime

def ler_csv(arquivo, cpf_coluna='CPF', nb_coluna='NB', cpf_rep_coluna='CPF_REP', sep=';', file_name='None'):

    headers = { 'User-Agent': 'Mozilla/5.0 (Windows NT 6.0; WOW64; rv:24.0) Gecko/20100101 Firefox/24.0' }

    dados_csv = pandas.read_csv(arquivo, sep=sep)

    df = pandas.DataFrame(columns=
                                    [
                                        'CPF',
                                        'Numero do Beneficio',
                                        'Data Nascimento',
                                        'Nome Beneficiario',
                                        'Situação do beneficio',
                                        'Especie de Beneficio',
                                        'Concessão judicial',
                                        'Data Despacho Beneficio',
                                        'UF Pagamento',
                                        'Tipo de crédito',
                                        'CBCIF PAGADORA',
                                        'Agência Pagadora',
                                        'Conta Corrente',
                                        'Pensao Alimenticia',
                                        'Possui representante legal',
                                        'Possui procurador',
                                        'Entidade de Representação',
                                        'Elegível para empréstimo',
                                        'Margem disponível',
                                        'Margem disp. cartão',
                                        'Valor de limite do cartão',
                                        'Qtd. Emprestimos ativos suspensos',
                                        'Data da Consulta',
                                        'CPF do Rep. Legal', #cpfRepresentanteLegal
                                        'Nome Rep. Legal', #nomeRepresentanteLegal
                                        'dataFimRepresentanteLegal', #dataFimRepresentanteLegal
                                        'Bloqueado para emprestimo',
                                        'Margem disp. RCC',
                                        'Valor de limite RCC'
                                    ]
                                    )
    
    for index, row in dados_csv.iterrows():
        nome_coluna_cpf = dados_csv.columns[dados_csv.columns.get_loc(cpf_coluna)]
        cpf = row[nome_coluna_cpf]
        cpf = str(cpf).replace('.', '').replace('-', '').replace(' ', '')

        while len(cpf) < 11:
            cpf = f'0{cpf}'

        nome_coluna_nb = dados_csv.columns[dados_csv.columns.get_loc(nb_coluna)]
        nb = row[nome_coluna_nb]
        matricula = str(nb).replace('.', '').replace('-', '').replace(' ', '')

        try:
            nome_coluna_cpf_rep = dados_csv.columns[dados_csv.columns.get_loc(cpf_rep_coluna)]
            cpf_rep = row[nome_coluna_cpf_rep]
            try:
                cpf_rep_num = str(int(cpf_rep)).replace('.', '').replace('-', '').replace(' ', '').replace('/', '')
            except:
                cpf_rep_num = None
        except:
            cpf_rep_num = None

        if cpf_rep_num:
            res = json.loads(requests.get(f'http://62.72.8.214:6969/ins_api?cpf={cpf}&nb={matricula}&rep={cpf_rep_num}&key=validador_user', headers=headers).text)
            print(f'http://62.72.8.214:6969/ins_api?cpf={cpf}&nb={matricula}&rep={cpf_rep_num}&key=validador_user')
        else:
            res = json.loads(requests.get(f'http://62.72.8.214:6969/ins_api?cpf={cpf}&nb={matricula}&key=validador_user', headers=headers).text)
            print(f'http://62.72.8.214:6969/ins_api?cpf={cpf}&nb={matricula}&key=validador_user')

        if res['Status'] == 200:

            x = res['Resultado']

            try:
                conta_corrente = x['contaCorrente']
            except:
                conta_corrente = None

            try:
                cpfRepresentanteLegal = x['cpfRepresentanteLegal']
            except:
                cpfRepresentanteLegal = None

            try:
                nomeRepresentanteLegal = x['nomeRepresentanteLegal']
            except:
                nomeRepresentanteLegal = None

            try: 
                dataFimRepresentanteLegal = x['dataFimRepresentanteLegal']
            except:
                dataFimRepresentanteLegal = None
            try:
                df.loc[len(df)] = [
                                    x['cpf'],
                                    x['numeroBeneficio'],
                                    x['dataNascimento'],
                                    x['nomeBeneficiario'],
                                    x['situacaoBeneficio'],
                                    x['especieBeneficio'],
                                    x['concessaoJudicial'],
                                    x['dataDespachoBeneficio'],
                                    x['ufPagamento'],
                                    x['tipoCredito'],
                                    x['cbcIfPagadora'],
                                    x['agenciaPagadora'],
                                    conta_corrente,
                                    x['pensaoAlimenticia'],
                                    x['possuiRepresentanteLegal'],
                                    x['possuiProcurador'],
                                    x['possuiEntidadeRepresentacao'],
                                    x['elegivelEmprestimo'],
                                    x['margemDisponivel'],
                                    x['margemDisponivelCartao'],
                                    x['valorLimiteCartao'],
                                    x['qtdEmprestimosAtivosSuspensos'],
                                    f'{datetime.datetime.now()}',
                                    cpfRepresentanteLegal,
                                    nomeRepresentanteLegal,
                                    dataFimRepresentanteLegal,
                                    x['bloqueadoParaEmprestimo'],
                                    x['margemDisponivelRCC'],
                                    x['valorLimiteRCC']
                                ]
                df.to_csv(f'ResultadoExcel{file_name}.csv', encoding="utf-8")
            except TypeError:
                
                with open(f'log{file_name}.txt', 'a', encoding='utf-8') as file:
                    file.write(f'{cpf},{matricula},{res}\n')
        else:

            with open(f'log{file_name}.txt', 'a', encoding='utf-8') as file:
                file.write(f'{cpf},{matricula},{res}\n')

        print(f'[{cpf}] Resultado:', res['Status'])

    return df

# Nome arquivo, nome da coluna de cpf, nome da coluna de beneficio
ler_csv('loteextrato.csv', 'CPF', 'NB', file_name='1809_3')