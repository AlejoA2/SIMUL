import os


class Config:

    # Cadena de conexión a la base de datos. En Docker la
    # inyecta docker-compose.yml (MySQL del servicio "db");
    # fuera de Docker se usa SQLite como respaldo local.
    DATABASE_URL = os.getenv(
        "DATABASE_URL",
        "sqlite:///instance/simul.db"
    )

    SECRET_KEY = os.getenv(
        "SECRET_KEY",
        "simul-development-secret-key-change-me"
    )

    JWT_SECRET_KEY = os.getenv(
        "JWT_SECRET_KEY",
        "simul-development-secret-key-change-me"
    )

    JWT_ACCESS_TOKEN_EXPIRES = int(
        os.getenv("JWT_ACCESS_TOKEN_EXPIRES", "3600")
    )
