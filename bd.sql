CREATE TABLE usuario (
    id_usuario SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    estado BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE super_admin (
    id_usuario INTEGER PRIMARY KEY,
    CONSTRAINT fk_superadmin_usuario
        FOREIGN KEY (id_usuario)
        REFERENCES usuario(id_usuario)
        ON DELETE CASCADE
);

CREATE TABLE admin_microempresa (
    id_usuario INTEGER PRIMARY KEY,
    id_microempresa INTEGER NOT NULL,

    CONSTRAINT fk_admin_usuario
        FOREIGN KEY (id_usuario)
        REFERENCES usuario(id_usuario)
        ON DELETE CASCADE,

    CONSTRAINT fk_admin_microempresa
        FOREIGN KEY (id_microempresa)
        REFERENCES microempresa(id_microempresa)
        ON DELETE CASCADE
);

CREATE TABLE vendedor (
    id_usuario INTEGER PRIMARY KEY,
    id_microempresa INTEGER NOT NULL,

    CONSTRAINT fk_vendedor_usuario
        FOREIGN KEY (id_usuario)
        REFERENCES usuario(id_usuario)
        ON DELETE CASCADE,

    CONSTRAINT fk_vendedor_microempresa
        FOREIGN KEY (id_microempresa)
        REFERENCES microempresa(id_microempresa)
        ON DELETE CASCADE
);
