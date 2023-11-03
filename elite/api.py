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
                '03174741700_900151',
                '15411844754_900151',
                '07225117440_900151',
                '53747046304_900053',
                '84535903204_900040',
                '05602198903_900118',
                '01151652741_003419',
                '06126427980_900043',
                '34954629888_900111',
                '10063799677_900043',
                '91579236200_900037',
                '03715984945_900118',
                '05582883592_900147',
                '40712504885_900040',
                '86039385200_900122',
                '23115065876_900061',
                '02107796084_900007',
                '15250052789_900045',
                '01672464960_900043',
                '07350378688_900043',
                '39087593821_900043',
                '04706373409_900111',
                '07740060135_900043',
                '08118082466_900007',
                '00040817067_900029',
                '61346080259_900040',
                '15250052789_900048',
                '31187625000_900029',
                '08261848710_900048',
                '30736044809_900043',
                '13976865451_900037',
                '01438308485_900043',
                '73736040210_900036',
                '01921098120_900043',
                '71508071438_900040',
                '35369808805_900036',
                '09675427400_900043',
                '04096784575_900180',
                '04096784575_900043',
                '72540699120_900043',
                '03475734109_900061',
                '05352084990_900043',
                '04820474375_900043',
                '07048560347_900232',
                '07775876964_900122',
                '04133185242_900122',
                '87593114015_900043',
                '78216672268_900036',
                '06634452130_900043',
                '04611319601_900036',
                '08236439720_900048',
                '01591132029_900043',
                '05544794006_900037',
                '15749570746_900036',
                '03732407322_900036',
                '10869917455_900039',
                '41486291848_900043',
                '00819874043_900037',
                '32924771900_900039',
                '00963492470_900037',
                '11330901681_900037',
                '57088632187_900043',
                '04231445109_900037',
                '11420043927_900043',
                '01151652741_900043',
                '04231445109_900043',
                '78216672268_900036',
                '04133185242_900122',
                '01921098120_900043',
                '04231445109_900043',
                '86039385200_900122',
                '71508071438_900040',

                
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
