import base64, random, time
from urllib.parse import quote

def makeid(length):
    characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
    return ''.join(random.choice(characters) for _ in range(length))

def getTimestampInSeconds():
    return int(time.time())

def generate_k():
    random_string = makeid(17)
    timestamp_chars = str(getTimestampInSeconds())[-10:]
    combined_string = random_string + timestamp_chars

    # Codifica a string combinada em Base64
    encoded_string = base64.b64encode(combined_string.encode()).decode()

    # Codifica a string Base64 resultante para ser usada em uma URI
    return quote(encoded_string)