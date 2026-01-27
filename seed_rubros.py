from app.database.session import SessionLocal
from app.microempresas.models import Rubro

db = SessionLocal()
rubros = [
    {"nombre": "Tecnología", "descripcion": "Venta de equipos electrónicos y software"},
    {"nombre": "Alimentos y Bebidas", "descripcion": "Restaurantes, cafeterías y tiendas de abarrotes"},
    {"nombre": "Ropa y Moda", "descripcion": "Tiendas de ropa, calzado y accesorios"},
    {"nombre": "Salud y Belleza", "descripcion": "Farmacias, cosméticos y cuidado personal"},
    {"nombre": "Servicios", "descripcion": "Consultoría, limpieza, reparación, etc."},
    {"nombre": "Ferretería", "descripcion": "Materiales de construcción y herramientas"}
]

for r_data in rubros:
    exists = db.query(Rubro).filter_by(nombre=r_data["nombre"]).first()
    if not exists:
        nuevo = Rubro(nombre=r_data["nombre"], descripcion=r_data["descripcion"], activo=True)
        db.add(nuevo)
        print(f"Creado rubro: {r_data['nombre']}")
    else:
        print(f"Ya existe: {r_data['nombre']}")

db.commit()
db.close()
