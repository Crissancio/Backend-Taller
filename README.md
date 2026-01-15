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
