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

/*------NUEVAS TABLAS--------*/
CREATE TABLE categoria (
    id_categoria SERIAL PRIMARY KEY,
    id_microempresa INTEGER NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    descripcion TEXT,
    activo BOOLEAN NOT NULL DEFAULT TRUE,
    fecha_creacion TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_categoria_microempresa
        FOREIGN KEY (id_microempresa)
        REFERENCES microempresas(id_microempresa)
        ON DELETE CASCADE,

    CONSTRAINT uq_categoria_microempresa_nombre
        UNIQUE (id_microempresa, nombre)
);



CREATE TABLE producto (
    id_producto SERIAL PRIMARY KEY,
    id_microempresa INTEGER NOT NULL,  -- tenant
    id_categoria INTEGER NOT NULL,

    nombre VARCHAR(150) NOT NULL,
    descripcion TEXT,

    precio_venta NUMERIC(10,2) NOT NULL,
    costo_compra NUMERIC(10,2),

    codigo VARCHAR(50),
    imagen TEXT,

    estado BOOLEAN NOT NULL DEFAULT TRUE,

    fecha_creacion TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_producto_microempresa
        FOREIGN KEY (id_microempresa)
        REFERENCES microempresas(id_microempresa)
        ON DELETE CASCADE,

    CONSTRAINT fk_producto_categoria
        FOREIGN KEY (id_categoria)
        REFERENCES categoria(id_categoria)
);



CREATE TABLE stock (
    id_stock SERIAL PRIMARY KEY,
    id_producto INTEGER NOT NULL,

    cantidad INTEGER NOT NULL DEFAULT 0,
    stock_minimo INTEGER NOT NULL DEFAULT 0,

    ultima_actualizacion TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_stock_producto
        FOREIGN KEY (id_producto)
        REFERENCES producto(id_producto)
        ON DELETE CASCADE,

    CONSTRAINT uq_stock_producto
        UNIQUE (id_producto)
);

CREATE TABLE notificacion (
    id_notificacion SERIAL PRIMARY KEY,
    id_microempresa INTEGER NOT NULL,
    id_usuario INTEGER NOT NULL,

    tipo VARCHAR(50), -- STOCK_BAJO, SIN_STOCK
    mensaje TEXT NOT NULL,

    leido BOOLEAN NOT NULL DEFAULT FALSE,
    fecha_creacion TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_notificacion_microempresa
        FOREIGN KEY (id_microempresa)
        REFERENCES microempresas(id_microempresa),

    CONSTRAINT fk_notificacion_usuario
        FOREIGN KEY (id_usuario)
        REFERENCES usuario(id_usuario)
);


/*------OTRAS NUEVAS TABLAS------*/
CREATE TABLE venta (
    id_venta SERIAL PRIMARY KEY,
    id_microempresa INT NOT NULL,
    id_cliente INT,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    total DECIMAL(10,2) NOT NULL,
    estado VARCHAR(20) NOT NULL,
    tipo VARCHAR(20) NOT NULL,

    FOREIGN KEY (id_microempresa) REFERENCES microempresas(id_microempresa),
    FOREIGN KEY (id_cliente) REFERENCES cliente(id_cliente)
);

CREATE TABLE detalle_venta (
    id_detalle SERIAL PRIMARY KEY,
    id_venta INT NOT NULL,
    id_producto INT NOT NULL,
    cantidad INT NOT NULL,
    precio_unitario DECIMAL(10,2) NOT NULL,
    subtotal DECIMAL(10,2) NOT NULL,

    FOREIGN KEY (id_venta) REFERENCES venta(id_venta),
    FOREIGN KEY (id_producto) REFERENCES producto(id_producto)
);

CREATE TABLE pago_venta (
    id_pago SERIAL PRIMARY KEY,
    id_venta INT NOT NULL,
    metodo VARCHAR(30) NOT NULL,
    comprobante_url TEXT,
    estado VARCHAR(20) NOT NULL,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (id_venta) REFERENCES venta(id_venta)
);
