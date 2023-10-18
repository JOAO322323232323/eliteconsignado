import random

def criptografar(number):
    stringArray = [['G', 'U', 'K'], ['J', '7', 'Q'], ['D', 'Y', 'L'], ['W', '9', 'R'], ['Z', 'V', 'B'], ['S', 'F', 'A'], ['T', 'I', 'P'], ['O', 'E', '1'], ['H', 'X', '5'], ['C', 'M', 'N']]

    numeros = list(number)
    string = 'x'

    for n in numeros:
        s = random.randint(0, len(stringArray[int(n)]) - 1)
        letra = stringArray[int(n)][s]
        string += letra

    return string + ':' + '8381d393b72f0a4d7ed13c12a689fe1d'

# Exemplo de uso
numero = "123456"
resultado = criptografar(numero)
print(resultado)