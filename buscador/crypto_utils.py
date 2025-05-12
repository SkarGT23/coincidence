from cryptography.fernet import Fernet
import os

# Genera una clave y la guarda en un archivo seguro si no existe
def generar_clave(path='clave.key'):
    if not os.path.exists(path):
        clave = Fernet.generate_key()
        with open(path, 'wb') as f:
            f.write(clave)
    else:
        with open(path, 'rb') as f:
            clave = f.read()
    return clave

def cifrar_archivo(ruta_archivo, clave_path='clave.key'):
    clave = generar_clave(clave_path)
    fernet = Fernet(clave)
    with open(ruta_archivo, 'rb') as file:
        original = file.read()
    cifrado = fernet.encrypt(original)
    with open(ruta_archivo + '.enc', 'wb') as encrypted_file:
        encrypted_file.write(cifrado)
    os.remove(ruta_archivo)

def descifrar_archivo(ruta_archivo_enc, clave_path='clave.key'):
    clave = generar_clave(clave_path)
    fernet = Fernet(clave)
    with open(ruta_archivo_enc, 'rb') as enc_file:
        cifrado = enc_file.read()
    descifrado = fernet.decrypt(cifrado)
    ruta_original = ruta_archivo_enc.replace('.enc', '')
    with open(ruta_original, 'wb') as dec_file:
        dec_file.write(descifrado)
    os.remove(ruta_archivo_enc)
    return ruta_original

# Ofuscación de contraseña: reconstruye la real de la forma B7O3O1O9M -> BOOOM
def reconstruir_contrasena(ofuscada):
    return ''.join([c for c in ofuscada if not c.isdigit()])
