-- ==========================================
-- 1. TABLAS INDEPENDIENTES (Sin Foreign Keys)
-- ==========================================

-- Tabla: usuario
CREATE TABLE usuario (
    id_usuario SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    estado BOOLEAN NOT NULL DEFAULT TRUE
);

-- Tabla: planes
/* MODIFICADO
CREATE TABLE planes (
    id_plan SERIAL PRIMARY KEY,
    nombre VARCHAR NOT NULL UNIQUE,
    precio DOUBLE PRECISION NOT NULL,
    limite_usuarios INTEGER NOT NULL,
    descripcion TEXT
);
*/
CREATE TABLE planes (
    id_plan SERIAL PRIMARY KEY,
    nombre VARCHAR NOT NULL UNIQUE,
    precio DOUBLE PRECISION NOT NULL,
    limite_productos INTEGER NOT NULL,
    limite_admins INTEGER NOT NULL,
    limite_vendedores INTEGER NOT NULL,
    activo BOOLEAN NOT NULL DEFAULT TRUE,
    descripcion TEXT
);

-- Tabla: microempresas
CREATE TABLE microempresas (
    id_microempresa SERIAL PRIMARY KEY,
    nombre VARCHAR NOT NULL,
    nit VARCHAR NOT NULL UNIQUE,
    direccion VARCHAR,
    telefono VARCHAR,
    moneda VARCHAR DEFAULT 'BOB',
    impuestos DOUBLE PRECISION DEFAULT 0.0,
    logo VARCHAR,
    horario_atencion VARCHAR,
    estado BOOLEAN DEFAULT TRUE,
    fecha_registro TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Índices para microempresas
CREATE INDEX ix_microempresas_nombre ON microempresas (nombre);
CREATE INDEX ix_microempresas_nit ON microempresas (nit);


-- ==========================================
-- 2. TABLAS DEPENDIENTES (Con Foreign Keys)
-- ==========================================

-- Tabla: super_admin
CREATE TABLE super_admin (
    id_usuario INTEGER PRIMARY KEY,
    CONSTRAINT fk_superadmin_usuario
        FOREIGN KEY (id_usuario)
        REFERENCES usuario(id_usuario)
        ON DELETE CASCADE
);

-- Tabla: admin_microempresa
CREATE TABLE admin_microempresa (
    id_usuario INTEGER PRIMARY KEY,
    id_microempresa INTEGER NOT NULL,

    CONSTRAINT fk_admin_usuario
        FOREIGN KEY (id_usuario)
        REFERENCES usuario(id_usuario)
        ON DELETE CASCADE,

    CONSTRAINT fk_admin_microempresa
        FOREIGN KEY (id_microempresa)
        REFERENCES microempresas(id_microempresa) -- Corregido a plural
        ON DELETE CASCADE
);

-- Tabla: vendedor
CREATE TABLE vendedor (
    id_usuario INTEGER PRIMARY KEY,
    id_microempresa INTEGER NOT NULL,

    CONSTRAINT fk_vendedor_usuario
        FOREIGN KEY (id_usuario)
        REFERENCES usuario(id_usuario)
        ON DELETE CASCADE,

    CONSTRAINT fk_vendedor_microempresa
        FOREIGN KEY (id_microempresa)
        REFERENCES microempresas(id_microempresa) -- Corregido a plural
        ON DELETE CASCADE
);

-- Tabla: suscripciones
CREATE TABLE suscripciones (
    id_suscripcion SERIAL PRIMARY KEY,
    fecha_inicio TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    fecha_fin TIMESTAMP WITH TIME ZONE,
    estado BOOLEAN DEFAULT TRUE,
    
    id_microempresa INTEGER NOT NULL,
    id_plan INTEGER NOT NULL,
    
    CONSTRAINT fk_suscripciones_microempresa 
        FOREIGN KEY (id_microempresa) 
        REFERENCES microempresas(id_microempresa)
        ON DELETE CASCADE,
        
    CONSTRAINT fk_suscripciones_plan 
        FOREIGN KEY (id_plan) 
        REFERENCES planes(id_plan)
        ON DELETE RESTRICT
);

CREATE TABLE cliente (
    id_cliente SERIAL PRIMARY KEY,
    id_microempresa INTEGER NOT NULL,   -- id_tenant

    nombre VARCHAR(150) NOT NULL,
    documento VARCHAR(50),
    telefono VARCHAR(30),
    email VARCHAR(150),

    estado BOOLEAN NOT NULL DEFAULT TRUE,  -- TRUE = activo, FALSE = eliminado

    fecha_creacion TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_cliente_microempresa
        FOREIGN KEY (id_microempresa)
        REFERENCES microempresas(id_microempresa)
        ON DELETE CASCADE
);



-- Índices para suscripciones
CREATE INDEX ix_suscripciones_id_microempresa ON suscripciones (id_microempresa);
CREATE INDEX ix_suscripciones_id_plan ON suscripciones (id_plan);
