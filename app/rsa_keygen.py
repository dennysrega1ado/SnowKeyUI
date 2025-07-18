from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
import os

def generate_rsa_keypair(key_name: str, output_dir: str):
    """
    Genera un par de llaves RSA (privada y pública) de 2048 bits en formato PEM sin passphrase.
    Guarda los archivos en el directorio especificado con el nombre dado.
    """
    # Generar la llave privada
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )

    # Serializar la llave privada en formato PEM sin passphrase
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )

    # Serializar la llave pública en formato PEM
    public_key = private_key.public_key()
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

    # Guardar los archivos
    priv_path = os.path.join(output_dir, f"{key_name}_private.pem")
    pub_path = os.path.join(output_dir, f"{key_name}_public.pem")
    with open(priv_path, 'wb') as f:
        f.write(private_pem)
    with open(pub_path, 'wb') as f:
        f.write(public_pem)
    return priv_path, pub_path 