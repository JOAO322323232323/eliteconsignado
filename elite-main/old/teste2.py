import requests

link = 'https://desenv.facta.com.br/sistemaNovo/acesso.php'

dat = {
    'login':'26006_ES2773JV',
    'senha':'Sandro@12@',
    'api_ip_1':'200.66.126.17'
}

session = requests.Session()

res = session.post(link, data=dat, verify='old/facta-com-br-chain.pem')

print(session.cookies.get_dict())

res_b = session.get('https://desenv.facta.com.br/sistemaNovo/dashboard.php')
html = res_b.text

link_a = html.find('"https://app.contako.com.br')
link_b = html[link_a:].find('});') + link_a
link_c = html[link_a:link_b].replace('"', '').replace(');', '').replace(' ', '')

print(link_c)

res_c = session.get(link_c)

widget_html = res_c.text

visitante_a = widget_html.find("var idVisitanteTemp = '")
visitante_b = widget_html[visitante_a:].find("';") + visitante_a
visitante_c = widget_html[visitante_a:visitante_b].replace("var idVisitanteTemp = '", "")

print(visitante_c)

secaointegrado_a = widget_html.find("var idSessaoIntegradoTemp = '")
secaointegrado_b = widget_html[secaointegrado_a:].find("';") + secaointegrado_a
secaointegrado_c = widget_html[secaointegrado_a:secaointegrado_b].replace("var idSessaoIntegradoTemp = '", "")

print(secaointegrado_c)