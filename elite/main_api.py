from flask import Flask, request
import assets, database, re

app = Flask(__name__, template_folder='templates')

@app.route('/ins_api', methods=['GET'])
def ins_api(cpf=None, nb=None, rep=None, key=None):

    cpf = request.args.get("cpf")
    nb = request.args.get("nb")
    try:
        rep = request.args.get("rep")
    except:
        rep = None
    key = request.args.get("key")   

    cpf = re.findall(r'\d+', cpf)[0]

    resultado, user = assets.ins_api_interno(cpf, nb, key, rep)

    resultado_res = resultado['Resultado']
    resultado_res = str(resultado_res).replace('{', '').replace('}', '').replace("'", "")

    status_res = resultado['Status']

    database.DATABASE().insert_and_commit(f"insert into pending(users_id, cpf, nb, cpf_rep, status_process, in100_data, status_code, log_user) values ((SELECT users_id FROM users WHERE username = '{key}'), '{cpf}', '{nb}', '{rep}', '{resultado_res}', 1, {status_res}, '{user}');")

    return resultado

@app.route('/saldo', methods=['GET'])
def saldo_user(key=None):
    key = request.args.get("key") 
    return assets.saldo_user(key)

@app.route('/fgts_api', methods=['GET'])
def fgts_api(cpf=None, key=None):

    cpf = request.args.get("cpf")
    key = request.args.get("key")   

    retorno_resp = assets.fgts_api_interno(cpf, key)

    return retorno_resp

if __name__ == '__main__': 
   app.run(debug=True, host='0.0.0.0', port=6969, threaded=True)