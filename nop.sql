CREATE TABLE usuario (
    id_usuario SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    activo BOOLEAN NOT NULL DEFAULT TRUE,
    fecha_creacion TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE super_admin (
    id_usuario INTEGER PRIMARY KEY,
    CONSTRAINT fk_superadmin_usuario
        FOREIGN KEY (id_usuario)
        REFERENCES usuario(id_usuario)
        ON DELETE CASCADE
);

CREATE TABLE rubro (
    id_rubro SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL UNIQUE,
    descripcion TEXT,
    activo BOOLEAN NOT NULL DEFAULT TRUE
);


CREATE TABLE microempresa (
    id_microempresa SERIAL PRIMARY KEY,
    nombre VARCHAR(150) NOT NULL,
    nit VARCHAR(30) NOT NULL UNIQUE,

    correo_contacto VARCHAR(150),
    direccion VARCHAR(255),
    telefono VARCHAR(30),

    latitud NUMERIC(10,7),
    longitud NUMERIC(10,7),

    dias_atencion VARCHAR(100), -- Ej: "Lunes a Viernes"
    horario_atencion VARCHAR(150),

    moneda VARCHAR(10) NOT NULL,
    impuestos NUMERIC(5,2),

    logo TEXT,

    id_rubro INTEGER,

    activo BOOLEAN NOT NULL DEFAULT FALSE,
    fecha_registro TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_microempresa_rubro
        FOREIGN KEY (id_rubro)
        REFERENCES rubro(id_rubro)
);


CREATE TABLE admin_microempresa (
    id_usuario INTEGER PRIMARY KEY,
    id_microempresa INTEGER NOT NULL,

    correo_contacto VARCHAR(150),
    telefono_contacto VARCHAR(30),

    es_owner BOOLEAN NOT NULL DEFAULT FALSE,

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

    correo_contacto VARCHAR(150),
    telefono_contacto VARCHAR(30),

    CONSTRAINT fk_vendedor_usuario
        FOREIGN KEY (id_usuario)
        REFERENCES usuario(id_usuario)
        ON DELETE CASCADE,

    CONSTRAINT fk_vendedor_microempresa
        FOREIGN KEY (id_microempresa)
        REFERENCES microempresa(id_microempresa)
        ON DELETE CASCADE
);


CREATE TABLE cliente (
    id_cliente SERIAL PRIMARY KEY,
    id_microempresa INTEGER NOT NULL,
    nombre VARCHAR(150) NOT NULL,
    documento VARCHAR(50),
    telefono VARCHAR(30),
    email VARCHAR(150),
    fecha_creacion TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_cliente_microempresa
        FOREIGN KEY (id_microempresa)
        REFERENCES microempresa(id_microempresa)
        ON DELETE CASCADE
);

CREATE TABLE plan (
    id_plan SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    precio NUMERIC(10,2) NOT NULL,
    duracion_meses INTEGER NOT NULL,

    limite_admins INTEGER NOT NULL,
    limite_vendedores INTEGER NOT NULL,
    limite_productos INTEGER NOT NULL,

    descripcion TEXT,
    estado BOOLEAN NOT NULL DEFAULT TRUE,
    fecha_creacion TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE pago (
    id_pago SERIAL PRIMARY KEY,
    id_usuario INTEGER NOT NULL,
    id_microempresa INTEGER,
    id_plan INTEGER NOT NULL,

    monto NUMERIC(10,2) NOT NULL,
    metodo_pago VARCHAR(50),
    comprobante_url TEXT,

    estado_pago VARCHAR(20) NOT NULL CHECK (estado_pago IN ('PENDIENTE', 'APROBADO', 'RECHAZADO')),
    tipo_pago VARCHAR(20) NOT NULL CHECK (tipo_pago IN ('INICIAL', 'CAMBIO_PLAN', 'RENOVACION')),

    fecha_pago TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    verificado_por INTEGER,
    fecha_verificacion TIMESTAMP,
    observaciones TEXT,

    CONSTRAINT fk_pago_usuario
        FOREIGN KEY (id_usuario)
        REFERENCES usuario(id_usuario),

    CONSTRAINT fk_pago_microempresa
        FOREIGN KEY (id_microempresa)
        REFERENCES microempresa(id_microempresa),

    CONSTRAINT fk_pago_plan
        FOREIGN KEY (id_plan)
        REFERENCES plan(id_plan),

    CONSTRAINT fk_pago_verificador
        FOREIGN KEY (verificado_por)
        REFERENCES super_admin(id_usuario)
);

CREATE TABLE suscripcion (
    id_suscripcion SERIAL PRIMARY KEY,
    id_microempresa INTEGER NOT NULL,
    id_plan INTEGER NOT NULL,
    id_pago_origen INTEGER NOT NULL,

    estado_suscripcion VARCHAR(20) NOT NULL
        CHECK (estado_suscripcion IN ('ACTIVA', 'VENCIDA', 'CANCELADA')),

    fecha_inicio TIMESTAMP NOT NULL,
    fecha_fin TIMESTAMP NOT NULL,
    fecha_cancelacion TIMESTAMP,
    fecha_creacion TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_suscripcion_microempresa
        FOREIGN KEY (id_microempresa)
        REFERENCES microempresa(id_microempresa)
        ON DELETE CASCADE,

    CONSTRAINT fk_suscripcion_plan
        FOREIGN KEY (id_plan)
        REFERENCES plan(id_plan),

    CONSTRAINT fk_suscripcion_pago
        FOREIGN KEY (id_pago_origen)
        REFERENCES pago(id_pago)
);
