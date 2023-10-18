import requests, json

def get_token():
    link = 'https://api.bancoprata.com.br/v1/users/login'

    json_data = {"email":"victor.barros@elitepromotora.com.br","password":"BRASIL@20"}

    headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 OPR/100.0.0.0'}

    res = requests.post(link, json=json_data, headers=headers)

    return json.loads(res.text)['data']['token']

def fgts(cpf):
    
    link = f'https://pratadigital.com.br/sistema-cb/v1/qitech/fgts/balance?document={cpf}&rate_id=7'

    headers = {'Authorization':f'Bearer {get_token()}',
            'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 OPR/100.0.0.0'}

    res = requests.get(link, headers=headers)

    if res.status_code == 400:

        link_wait = 'https://pratadigital.com.br/sistema-cb/v1/qitech/fgts/balance-wait-list'

        res_wait = requests.get(link_wait, headers=headers)

        json_data = json.loads(res_wait.text)

        for x in json_data['data']:

            cpf_formated = f'{cpf[0]}{cpf[1]}{cpf[2]}.{cpf[3]}{cpf[4]}{cpf[5]}.{cpf[6]}{cpf[7]}{cpf[8]}-{cpf[9]}{cpf[10]}'
            
            if x['document'] == cpf_formated:

                return x
    else:
        return json.loads(res.text)['data']
        
#print(fgts('18497379837'))