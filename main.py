from fastapi import FastAPI, Form
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def inicio():
    return {"status": "online", "mensaje": "Backend RCV Manual Operativo"}

@app.post("/api/procesar-documentos")
async def procesar_documentos(
    cedula: str = Form(...),
    primer_nombre: str = Form(...),
    segundo_nombre: str = Form(None),
    primer_apellido: str = Form(...),
    segundo_apellido: str = Form(None),
    fecha_nacimiento: str = Form(...),
    telefono: str = Form(...),
    correo: str = Form(...),
    tipo_vehiculo: str = Form(...),
    precio: str = Form(...),
    estado: str = Form(...),
    ciudad: str = Form(...),
    municipio: str = Form(...),
    parroquia: str = Form(...),
    direccion_detallada: str = Form(...),
    placa: str = Form(...),
    marca: str = Form(...),
    modelo: str = Form(...),
    anio: str = Form(...),
    serial_carroceria: str = Form(...),
    serial_motor: str = Form(...),
    color: str = Form(...),
    puestos: str = Form(...),
    peso: str = Form(...)
):
    s_nombre = segundo_nombre if segundo_nombre else ""
    s_apellido = segundo_apellido if segundo_apellido else ""
    nombre_completo = f"{primer_nombre} {s_nombre} {primer_apellido} {s_apellido}".replace("  ", " ").strip()

    resultado_final = {
        "cedula": cedula,
        "primer_nombre": primer_nombre,
        "segundo_nombre": s_nombre,
        "primer_apellido": primer_apellido,
        "segundo_apellido": s_apellido,
        "nombre_completo": nombre_completo,
        "fecha_nacimiento": fecha_nacimiento,
        "telefono": telefono,
        "correo": correo,
        "tipo_vehiculo": tipo_vehiculo,
        "precio": precio,
        "estado": estado,
        "ciudad": ciudad,
        "municipio": municipio,
        "parroquia": parroquia,
        "direccion_detallada": direccion_detallada,
        "placa": placa,
        "marca": marca,
        "modelo": modelo,
        "anio": anio,
        "serial_carroceria": serial_carroceria,
        "serial_motor": serial_motor,
        "color": color,
        "puestos": puestos,
        "peso": peso
    }

    return {"status": "success", "data": resultado_final}
