import requests, json, codecs, re, pandas, os, datetime, pandas, time

FILE_GLOBAL = datetime.datetime.now().strftime("%d%m%Y%H%M%S")
LOGIN_CONFIG = '92415_33490868889' # LOGIN DA VADIA
SENHA_CONFIG = 'Consig*@99@' # SENHA DA VADIA

class FGTS_API(object):

    def __init__(self, login, senha, path_certificate):
        self.login = login
        self.senha = senha
        self.path_certificate = path_certificate

    def get_cookies(self, login, senha):
            
        try:

            link = 'https://desenv.facta.com.br/sistemaNovo/acesso.php'

            dat = {
                'login':login,
                'senha':senha,
                'api_ip_1':'200.66.126.17'
            }

            session = requests.Session()

            res = session.post(link, data=dat, verify=self.path_certificate)
            cook_json = session.cookies.get_dict()

            FGTServer_value = cook_json['FGTServer']
            PHPSESSID_value = cook_json['PHPSESSID']

            return [FGTServer_value, PHPSESSID_value, session]
        
        except Exception as erro_cookies:
            print('[SISTEMA] Erro GET COOKIES:', erro_cookies)
            return []
        
    def get_fgts(self, cpf):

        data = self.get_cookies(self.login, self.senha)

        if data:

            session = data[2]

            url = "https://desenv.facta.com.br/sistemaNovo/ajax/simulador/fgts.php"

            headers = {
                'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36 OPR/101.0.0.0',
                'accept': 'application/json',
                'path': '/sistemaNovo/ajax/simulador/fgts.php',
                'authority': 'desenv.facta.com.br'
            }

            cook = {
                'FGTServer':data[0],
                'PHPSESSID':data[1]
            }

            data = {
                'cpf': cpf,
                'login': self.login,
                'acao': 'consulta'
            }

            response = session.post(url, headers=headers, data=data, cookies=cook, verify=self.path_certificate)

            json_data = json.loads(str(response.text).lstrip(codecs.BOM_UTF8.decode('utf-8')))

            if int(json_data['codigo']) == 0:
                return {'Status':200, 'Retorno':json_data['fgts'][0]}
            elif int(json_data['codigo']) == 100:
                return {'Status':100, 'Retorno':'Sua solicitação entrou na nossa fila de consulta de saldos.'}
            elif int(json_data['codigo']) == 403:
                return {'Status':403, 'Retorno':'Instituição Fiduciária não possui autorização do Trabalhador para Operação Fiduciária.'}
            elif int(json_data['codigo']) == 404:
                return {'Status':404, 'Retorno':'Trabalhador informado não possui contas de FGTS.'}
            elif int(json_data['codigo']) == 400:
                return {'Status':400, 'Retorno':'Trabalhador não possui adesão ao saque aniversário vigente na data corrente.'}
            elif int(json_data['codigo']) == 200:
                return {'Status':103, 'Retorno':'Cliente não possui saldo FGTS.'}
            else:
                return {'Status':101, 'Retorno':json_data} 
            
        else:
            return {'Status':102, 'Retorno':'Usuario incorreto ou erro nos cookies.'} 

    def get_lote(self, cpf_list, df, index_th):

        num = 0

        #task_cpf = open(file, 'r', encoding='utf-8').readlines()

        total_num = len(cpf_list)

        for cpf in cpf_list:

            if cpf.find('#') != -1:
                print(f'[SISTEMA {index_th}] Comentário: {cpf}')
            else:

                cpf = re.findall(r'\d+', cpf)[0]

                if self.validar_cpf(self.formatar_cpf(cpf)):

                    cpf = self.formatar_cpf(cpf)
                    num += 1
                    
                    print(f'[SISTEMA {index_th}] Testando CPF: {cpf} | {num}/{total_num}')

                    resultado = self.get_fgts(cpf)

                    if resultado['Status'] == 200:

                        try:
                            valor = resultado['Retorno']['total']
                        except:
                            valor = resultado

                        df.loc[len(df)] = [cpf, valor]

                        df.to_csv(f'resultado_{FILE_GLOBAL}.csv')

                        time.sleep(3)

                        print(f'[SISTEMA {index_th}] PAUSA DE 3 SEGUNDOS')
                
                    elif resultado['Retorno'].find('fila de consulta') != -1:
                        with open('reprocessar.txt', 'a') as file:
                            file.write(f'{cpf}\n')

                    else:
                        with open('resultado_falho.txt', 'a') as file   :
                            retorno = resultado['Retorno']
                            file.write(f'{cpf}|{retorno}\n')

        print('[SISTEMA] Conluido.')

    def formatar_cpf(self, cpf):
        # Remove qualquer caractere não numérico do CPF
        cpf = ''.join(filter(str.isdigit, cpf))

        # Adiciona zeros à esquerda até que tenha 11 dígitos
        cpf = cpf.zfill(11)

        return cpf

    def validar_cpf(self, cpf):
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

    def main_fgts(self, file, thread=False):

        import threading

        df = pandas.DataFrame(columns=['CPF', 'RESULTADO'])

        if not thread:
            cpf_list = [x for x in open(file, 'r').readlines()]
            self.get_lote(cpf_list, df, 'UNICO')
        else:
            arquivo_base = open(file, 'r').readlines()

            partes = [arquivo_base[i:i + len(arquivo_base) // 5] for i in range(0, len(arquivo_base), len(arquivo_base) // 5)]
        
            th_01 = threading.Thread(target=self.get_lote, args=(partes[0], df, '01'))
            th_02 = threading.Thread(target=self.get_lote, args=(partes[1], df, '02'))
            th_03 = threading.Thread(target=self.get_lote, args=(partes[2], df, '03'))
            th_04 = threading.Thread(target=self.get_lote, args=(partes[3], df, '04'))
            th_05 = threading.Thread(target=self.get_lote, args=(partes[4], df, '05'))

            th_01.start()
            th_02.start()
            th_03.start()
            th_04.start()
            th_05.start()

            th_01.join()
            th_02.join()
            th_03.join()
            th_04.join()
            th_05.join()

        try:
            print('[SISTEMA] Iniciando reprocessamento.')
            self.get_lote('reprocessar.txt', f'{FILE_GLOBAL}_re')
            os.remove('reprocessar.txt')
            print('[SISTEMA] Processamento finalizado')
        except:
            print('[SISTEMA] Não há reprocessamento.')

#FGTS_API(LOGIN_CONFIG, SENHA_CONFIG, 'facta-com-br-chain.pem').main_fgts('a.txt', False)

#print(FGTS_API(LOGIN_CONFIG, SENHA_CONFIG, 'facta-com-br-chain.pem').get_fgts('43384169808'))