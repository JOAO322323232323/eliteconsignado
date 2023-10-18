# Elite - API para uso

# Introdução

A API da Elite é uma das melhores API's do mercado para ser utilizado o módulo IN100. Atualmente estamos trabalhando para expandir cada vez mais todos os nosso modulos atuais e não somente expandir os módulos, mas também melhorar o tempo de resposta e também reduzir os erros referentes.

# Uso da API

A api é de utilização bem simples e requere apenas uma solicitação 'GET' que pode ser feita pelo navegador de forma simples ou também em qualquer solicitação de código.

O uso da API depende da quantidade de saldo que o cliente deve ter para que o retorno da solicitação seja positivo.

# Conexão

A conexão de uso da api deve ser feita pelo seguinte link:

http://62.72.8.214:6969

Lembrando que a porta para a API deve ser obrigatoriamente 6969.

# IN100

A conexão principal da IN100 é pelo caminho:

/ins_api

Os argumentos requeridos para utilizar a API são:

- cpf (Cadastro de Pessoa Física)
- nb (Número de Benefício)
- rep (Cadastro de Pessoa Física para representante. Opcional)
- key (Usuario que fará a solicitação)

Todos os argumentos são obrigatórios EXCETO o argumento de representante.

Exemplo para utilização:

http://62.72.8.214:6969/ins_api?cpf=111111111&nb=2222222222&key=user

# SALDO

A conexão principal para verificar o saldo é pelo caminho:

/saldo

O argumento requerido para utilizar a API é:

- key (Usuario que fará a solicitação)

Exemplo para utilização:

http://62.72.8.214:6969/saldo?key=user

# Respostas e Status

103 - Necessário representante legal.
104 - Benefício inexistente.
105 - Dados não localizados.
106 - Dados não localizados ou CPF inelegível.
402 - Saldo indisponível para realizar a consulta.
403 - Erro referente a falta de CPF, Numero de Benefício ou usuário para autenticação.
500 - Erro interno ou banco fora do ar para a solicitação.
