import threading, assets, database, old.fgts_chain, time

class validador(object):

    def valida_in100(self):

        while True:

            try:
                res_db = database.DATABASE().SelectAndUpdatePending_in100()

                if res_db == None:
                    pass
                else:   
                    for res in res_db:

                        cpf = ''.join(filter(str.isdigit, res[1]))
                        nb = ''.join(filter(str.isdigit, res[2]))

                        print(f'[IN100] Analisando cpf: {cpf}')

                        if res[3] == None:
                            cpf_rep = None
                        else:
                            cpf_rep = ''.join(filter(str.isdigit, res[3]))

                        resultado, log = assets.ins_api_interno(cpf, nb, 'validador_user', cpf_rep)

                        resultado_res = resultado['Resultado']
                        resultado_res = str(resultado_res).replace('{', '').replace('}', '').replace("'", "")

                        if resultado['Status'] == 200:
                            database.DATABASE().insert_and_commit(f"update pending set status_code = 200, status_process = '{resultado_res}' where cpf = '{res[1]}' and nb = '{res[2]}' and pending_id = {res[0]};")
                        elif resultado['Status'] in [403, 103, 104, 105, 106, 402]:
                            database.DATABASE().insert_and_commit(f"INSERT INTO user_score (users_id, score_l_in100) VALUES ((select users_id from pending where pending_id = {res[0]}), +1) ON DUPLICATE KEY UPDATE score_l_in100 = score_l_in100 +1;")
                            database.DATABASE().insert_and_commit(f"update pending set status_code = {resultado['Status']}, status_process = '{resultado_res}' where cpf = '{res[1]}' and nb = '{res[2]}' and pending_id = {res[0]};")

                        print(f'[IN100] Finalizado cpf: {cpf}')

            except Exception as erro:
                print('Erro Valida IN100', erro)

            time.sleep(15)

                                                
    def valida_fgts(self):

        while True:

            try:

                res_db = database.DATABASE().SelectAndUpdatePending_fgts()

                if res_db == None:
                    pass
                else:
                    for res in res_db:

                        cpf = ''.join(filter(str.isdigit, res[1]))

                        print(f'[FGTS] Analisando cpf: {cpf}')

                        resultado = old.fgts_chain.FGTS_API('92359_juliameirar', 'Banco@1826', 'facta-com-br-chain.pem').get_fgts(cpf)
                        resultado_res = resultado['Retorno']

                        #print(resultado)

                        if resultado['Status'] == 200:
                            database.DATABASE().insert_and_commit(f"update pending set status_code = 200, status_process = '{resultado_res['total']}' where cpf = '{res[1]}' and pending_id = {res[0]};")
                        elif resultado['Status'] in [403, 103, 104, 105, 106, 402, 400]:
                            database.DATABASE().insert_and_commit(f"INSERT INTO user_score (users_id, score_l_fgts) VALUES ((select users_id from pending where pending_id = {res[0]}), +1) ON DUPLICATE KEY UPDATE score_l_fgts = score_l_fgts +1;")
                            database.DATABASE().insert_and_commit(f"update pending set status_code = {resultado['Status']}, status_process = '{resultado_res}' where cpf = '{res[1]}' and pending_id = {res[0]};")

                        print(f'[FGTS] Finalizado cpf: {cpf}')

            except Exception as erro:
                print('Erro Valida FGTS:', erro)
                pass

            time.sleep(15)

    def main_sys(self):

        th_01_fgts = threading.Thread(target=self.valida_fgts)
        th_02_fgts = threading.Thread(target=self.valida_fgts)
        th_03_fgts = threading.Thread(target=self.valida_fgts)
        th_04_fgts = threading.Thread(target=self.valida_fgts)
        th_05_fgts = threading.Thread(target=self.valida_fgts)

        th_01_in100 = threading.Thread(target=self.valida_in100)
        th_02_in100 = threading.Thread(target=self.valida_in100)
        th_03_in100 = threading.Thread(target=self.valida_in100)
        th_04_in100 = threading.Thread(target=self.valida_in100)
        th_05_in100 = threading.Thread(target=self.valida_in100)

        th_01_fgts.start()
        th_02_fgts.start()
        th_03_fgts.start()
        th_04_fgts.start()
        th_05_fgts.start()

        th_01_in100.start()
        th_02_in100.start()
        th_03_in100.start()
        th_04_in100.start()
        th_05_in100.start()

        th_01_fgts.join()
        th_02_fgts.join()
        th_03_fgts.join()
        th_04_fgts.join()
        th_05_fgts.join()

        th_01_in100.join()
        th_02_in100.join()
        th_03_in100.join()
        th_04_in100.join()
        th_05_in100.join()

        print('Iniciado, não mexe.')

validador().main_sys()