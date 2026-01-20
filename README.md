# Backend-Taller

## Iniciar el backend

- Crear venv:

``` Bash
python -m venv venv
```

o

``` Bash
python3 -m venv venv
```

- Iniciar venv:

```powersheall
.\venv\Scripts\activate
```

- Installar dependencias

``` powershell
pip install -r requirements.txt
```

- Iniciar Backend

``` powershell
uvicorn app.main:app --reload
```

## Configuración de acceso a la base de datos

Para conectar el backend a la base de datos, sigue estos pasos:

1. **Instala PostgreSQL** y asegúrate de tener una base de datos creada.
2. Crea un archivo `.env` en la raíz del proyecto (ya existe un ejemplo en este repositorio) con las siguientes variables:

```dotenv
DB_HOST=localhost
DB_PORT=5432
DB_NAME=nombre_de_tu_bd
DB_USER=tu_usuario
DB_PASSWORD=tu_contraseña
DATABASE_URL=postgresql://tu_usuario:tu_contraseña@localhost:5432/nombre_de_tu_bd
```

3. El backend utiliza SQLAlchemy y las variables de entorno para conectarse. Puedes modificar los valores según tu entorno local o de producción.

4. **Ejemplo de conexión:**

Si usas los valores por defecto del ejemplo:

```dotenv
DB_HOST=localhost
DB_PORT=5432
DB_NAME=saas_db_2
DB_USER=postgres
DB_PASSWORD=123456
DATABASE_URL=postgresql://postgres:123456@localhost:5432/saas_db_2
```

5. **No compartas tu archivo `.env` en repositorios públicos.**
