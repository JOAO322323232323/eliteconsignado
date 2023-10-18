def is_valid_cpf(cpf):
    # Remover caracteres não numéricos
    cpf = ''.join(filter(str.isdigit, cpf))
    
    # Verificar se o CPF tem 11 dígitos
    if len(cpf) != 11:
        return False
    
    # Calcular o primeiro dígito verificador
    total = 0
    for i in range(9):
        total += int(cpf[i]) * (10 - i)
    remainder = total % 11
    digit1 = 0 if remainder < 2 else 11 - remainder
    
    # Verificar o primeiro dígito verificador
    if int(cpf[9]) != digit1:
        return False
    
    # Calcular o segundo dígito verificador
    total = 0
    for i in range(10):
        total += int(cpf[i]) * (11 - i)
    remainder = total % 11
    digit2 = 0 if remainder < 2 else 11 - remainder
    
    # Verificar o segundo dígito verificador
    if int(cpf[10]) != digit2:
        return False
    
    return True

# Teste
cpf = '6367233563'
print(is_valid_cpf(cpf))
