import requests, json, random, datetime, time

class API_qmc(object):

    def main(self, cpf, cod_beneficio, cpf_rep=None):
        try:
            json_autorização, usuario_log = self.get_autorizacao(cpf, cod_beneficio, cpf_rep)

            try:
                json_autorização = json_autorização.replace(' ', '')
            except:
                pass

            if str(json_autorização).find('encontradonabaseouCPFdebenef') != -1:
                return 106, usuario_log 

            if str(json_autorização).find('representantelegal') != -1:
                return 103, usuario_log
            
            if str(json_autorização).find('inexistente') != -1:
                return 104, usuario_log

            if json_autorização == 0:
                return None, usuario_log
            
            if not json_autorização:
                return 105, usuario_log

            return json_autorização, usuario_log
        except Exception as erroooo:
            print('Erro Main_api', erroooo)

    def get_autorizacao(self, cpf, cod_beneficio, cpf_rep=None):

        try:

            session = requests.Session()

            ddd = '11'
            tel = random.randint(900000000, 999999999)

            def cod_user():
                cod_users = [
                '30913998850_900036',

                

                
]
                
                return random.choice(cod_users)
            
            usuario_cod = cod_user()

            headers = {'Content-Type':'application/json; charset=UTF-8'}

            if cpf_rep:

                data = {"system":"FUNCAO","cod_operator":f"{usuario_cod}",
                            "name":f"{cpf}",
                            "cpf":f"{cpf}",
                            "cpf_represent":f"{cpf_rep}",
                            "tel":f"({ddd}){tel}",
                            "cod_beneficio":f"{cod_beneficio}",
                            "enviar_sms": "false",
                            "enviar_whatsapp": "true",
                            "enviar_email": "false"
                            }
                
            else:

                data = {"system":"FUNCAO","cod_operator":f"{usuario_cod}",
                        "name":f"{cpf}",
                        "cpf":f"{cpf}",     
                        "tel":f"({ddd}){tel}",
                        "cod_beneficio":f"{cod_beneficio}",
                        "enviar_sms": "false",
                        "enviar_whatsapp": "true",
                        "enviar_email": "false"
                        }
            
            res = session.post("https://queromaiscredito.app/DataPrev/e-consignado/beneficios/cartao_consulta_in100.php", json=data, headers=headers)

            #time.sleep(20)

            print(f'RETORNO POST: {res.text}')

            if res.status_code == 200:
                try:
                    headers = {'Content-Type': 'text/html', 'charset':'utf-8'}
                    resumo = session.get(f'https://armazem.capitalbank.systems/_dataPrev/{cpf}/Resumo-{cpf}-{cod_beneficio}.json')
                    resumo.encoding = "latin"
                    resumo_json = json.loads(resumo.text)

                    try:
                        def bool_to_sim_nao(value):
                            if str(value) == 'True' or str(value) == 'true':
                                return "Sim"
                            elif str(value) == 'False' or str(value) == 'false':
                                return "Nao"
                            else:
                                try:
                                    return value['descricao']
                                except:
                                    return f"{value}"
                        for key in resumo_json:
                            resumo_json[key] = bool_to_sim_nao(resumo_json[key])
                        resumo_json['dataConsulta'] = f'{datetime.datetime.now()}'
                    except Exception as erro_json:
                        print('ERRO JSON', erro_json)
                        pass
                    return resumo_json, usuario_cod
                except Exception as erro:
                    if res.text == '         Erro':
                        return 0, usuario_cod
                    elif res.text.find('Erro') != -1:
                        return 0, usuario_cod
                    elif res.text.find('DV inv\\u00e1lido') != -1:
                        return 0, usuario_cod
                    return res.text, usuario_cod
        except:
            print('get_autorizacao')
