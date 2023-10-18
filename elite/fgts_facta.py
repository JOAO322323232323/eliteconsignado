import requests, json, codecs

class FGTS_API(object):

    def __init__(self):
        self.login = '92415_33490868889'
        self.senha = 'Consig*@99@'
        self.path_certificate = 'facta-com-br-chain.pem'

    def get_cookies(self, login, senha):
            
        try:

            link = 'https://desenv.facta.com.br/sistemaNovo/acesso.php'

            ip = json.loads(requests.get('https://pro.ip-api.com/json/?key=ygbal37oYOpr9SC').text)['query']

            headers = {
                'Accept': 'application/json',
                'Content-Length': '96',
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                'Origin': 'https://desenv.facta.com.br',
                'Referer': 'https://desenv.facta.com.br/sistemaNovo/login.php',
                'Sec-Ch-Ua': '"Not/A)Brand";v="99", "Opera GX";v="101", "Chromium";v="115"',
                'Sec-Ch-Ua-Mobile': '?0',
                'Sec-Ch-Ua-Platform': '"Windows"',
                'Sec-Fetch-Dest': 'empty',
                'Sec-Fetch-Mode': 'cors',
                'Sec-Fetch-Site': 'same-origin',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36 OPR/101.0.0.0',
                'X-Requested-With': 'XMLHttpRequest'
            }

            dat = {
                'login':login,
                'senha':senha,
                'token':'',
                'api_ip_1':'200.66.126.33',
                'api_ip_2':'',
                'api_ip_3':''
            }

            session = requests.Session()

            res = session.post(link, data=dat, verify=self.path_certificate, headers=headers)
            #print(res.status_code)
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
                'authority': 'desenv.facta.com.br',
                'Sec-Ch-Ua-Platform':"Windows",
                'Sec-Ch-Ua':'"Not/A)Brand";v="99", "Opera GX";v="101", "Chromium";v="115"'
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

            import httpx

            with httpx.Client(verify=self.path_certificate) as client:
                timeout = httpx.Timeout(30.0)
                response = client.post(url, headers=headers, data=data, cookies=cook, timeout=timeout)

            #response = session.post(url, headers=headers, data=data, cookies=cook, verify=self.path_certificate)

            #print(response.text)

            json_data = json.loads(str(response.text).lstrip(codecs.BOM_UTF8.decode('utf-8')))

            if int(json_data['codigo']) == 0:
                return {'Status':200, 'Resultado':json_data['fgts'][0]}
            elif int(json_data['codigo']) == 100:
                return {'Status':100, 'Resultado':'Sua solicitação entrou na nossa fila de consulta de saldos.'}
            elif int(json_data['codigo']) == 403:
                return {'Status':403, 'Resultado':'Instituição Fiduciária não possui autorização do Trabalhador para Operação Fiduciária.'}
            elif int(json_data['codigo']) == 404:
                return {'Status':404, 'Resultado':'Trabalhador informado não possui contas de FGTS.'}
            elif int(json_data['codigo']) == 400:
                return {'Status':400, 'Resultado':'Trabalhador não possui adesão ao saque aniversário vigente na data corrente.'}
            elif int(json_data['codigo']) == 200:
                return {'Status':103, 'Resultado':'Cliente não possui saldo FGTS.'}
            elif int(json_data['codigo']) == 999:
                return {'Status':104, 'Resultado':'Caixa não retornou saldo para o CPF informado.'}
            else:
                return {'Status':101, 'Resultado':json_data} 
            
        else:
            return {'Status':102, 'Resultado':'Usuario incorreto ou erro nos cookies.'} 

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
    
#print(FGTS_API().get_fgts('18497379837'))