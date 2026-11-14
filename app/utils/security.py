"""
Hashing de contraseñas con la biblioteca estándar.

En el corte de frontend las contraseñas de demostración viajaban
al navegador; en el backend se guardan SIEMPRE como hash con
sal aleatoria (nunca en texto plano).

Formato almacenado (cabe de sobra en `usuario.password_hash
VARCHAR(255)`):

    pbkdf2_sha256$<iteraciones>$<sal_hex>$<hash_hex>

Se usa `hashlib.pbkdf2_hmac` (sin dependencias externas, a
diferencia de werkzeug) y `hmac.compare_digest` para comparar
en tiempo constante y evitar ataques de temporización.
"""

import hashlib
import hmac
import os


ALGORITMO = "pbkdf2_sha256"

ITERACIONES = 260_000

LONGITUD_SAL = 16


def hash_password(password: str) -> str:

    """Devuelve el hash con sal de una contraseña."""

    sal = os.urandom(LONGITUD_SAL)

    derivado = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        sal,
        ITERACIONES
    )

    return (
        f"{ALGORITMO}${ITERACIONES}"
        f"${sal.hex()}${derivado.hex()}"
    )


def verify_password(password: str, hash_guardado: str) -> bool:

    """Comprueba una contraseña contra su hash.

    Devuelve False ante cualquier hash malformado o de un
    algoritmo distinto (nunca lanza excepción).
    """

    if not hash_guardado:

        return False

    try:

        algoritmo, iteraciones, sal_hex, hash_hex = (
            hash_guardado.split("$")
        )

        if algoritmo != ALGORITMO:

            return False

        derivado = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            bytes.fromhex(sal_hex),
            int(iteraciones)
        )

    except (ValueError, TypeError):

        return False

    return hmac.compare_digest(
        derivado.hex(),
        hash_hex
    )
