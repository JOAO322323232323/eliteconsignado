import requests, json

#kyc -> Interpol
#basic_data -> Receita Federal

#12248394985

#data = '{"Datasets": "basic_data","q": "email{gabrielyudenich@gmail.com}", "AccessToken": "39eeac05-3bc8-4112-ad28-43a55a436f13"}'


data = '{"Datasets": "basic_data","q": "doc{16514718434}", "AccessToken": "39eeac05-3bc8-4112-ad28-43a55a436f13"}'
link = 'https://queromaiscredito.app/peoplev2'

#link = 'https://queromaiscredito.app/DataPrev/e-consignado/beneficios/cartao_resultados.php'
#data = {"system":"FUNCAO","cod_operator":"18500078707_900151"}

res = requests.post(link, data=data)

json_data = json.loads(res.text)

print(json_data)
'''
for pessoa in json_data['Result']:

    pis = pessoa['BasicData']['AlternativeIdNumbers']['SocialSecurityNumber']
    nome_completo = pessoa['BasicData']['Name']
    pais = pessoa['BasicData']['TaxIdCountry']
    genero = pessoa['BasicData']['Gender']
    data_nascimento = pessoa['BasicData']['BirthDate']
    pais_de_nascimento = pessoa['BasicData']['BirthCountry']
    nome_mae = pessoa['BasicData']['MotherName']
    nome_pai = pessoa['BasicData']['FatherName']
    situacao_receita = pessoa['BasicData']['TaxIdStatus']
    regiao_fiscal = pessoa['BasicData']['TaxIdFiscalRegion']
    obito = pessoa['BasicData']['HasObitIndication']'''