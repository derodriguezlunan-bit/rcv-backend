from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
import google.generativeai as genai
import json
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-1.5-flash')

@app.post("/api/procesar-documentos")
async def procesar_documentos(
    carnet_img: UploadFile = File(...),
    cedula: str = Form(...),
    primer_nombre: str = Form(...),
    segundo_nombre: str = Form(...),
    primer_apellido: str = Form(...),
    segundo_apellido: str = Form(...),
    fecha_nacimiento: str = Form(...),
    telefono: str = Form(...),
    correo: str = Form(...),
    tipo_vehiculo: str = Form(...),
    precio: str = Form(...),
    estado: str = Form(...),
    ciudad: str = Form(...),
    municipio: str = Form(...),
    parroquia: str = Form(...),
    direccion_detallada: str = Form(...)
):
    carnet_bytes = await carnet_img.read()

    prompt = """
    Analiza esta imagen del Carnet de Circulación vehicular de Venezuela.
    Extrae la siguiente información técnica del vehículo y devuélvela UNICAMENTE en formato JSON plano (sin texto adicional, sin bloques de código markdown ```json):
    {
      "placa": "número de placa",
      "marca": "marca",
      "modelo": "modelo",
      "anio": "año",
      "serial_carroceria": "serial de carrocería o NIV",
      "serial_motor": "serial de motor",
      "color": "color",
      "puestos": "puestos",
      "peso": "peso"
    }
    """

    response = model.generate_content([
        prompt,
        {"mime_type": carnet_img.content_type, "data": carnet_bytes}
    ])

    texto_limpio = response.text.replace("```json", "").replace("```", "").strip()
    
    try:
        datos_extraidos = json.loads(texto_limpio)
    except:
        datos_extraidos = {
            "placa": "PENDIENTE",
            "marca": "Ver Carnet",
            "modelo": "Ver Carnet"
        }

    # Consolidar los nombres y demás datos aportados
    nombre_completo = f"{primer_nombre} {segundo_nombre} {primer_apellido} {segundo_apellido}".replace("  ", " ").strip()

    datos_extraidos["cedula"] = cedula
    datos_extraidos["primer_nombre"] = primer_nombre
    datos_extraidos["segundo_nombre"] = segundo_nombre
    datos_extraidos["primer_apellido"] = primer_apellido
    datos_extraidos["segundo_apellido"] = segundo_apellido
    datos_extraidos["nombre_completo"] = nombre_completo
    datos_extraidos["fecha_nacimiento"] = fecha_nacimiento
    datos_extraidos["telefono"] = telefono
    datos_extraidos["correo"] = correo
    datos_extraidos["tipo_vehiculo"] = tipo_vehiculo
    datos_extraidos["precio"] = precio
    datos_extraidos["estado"] = estado
    datos_extraidos["ciudad"] = ciudad
    datos_extraidos["municipio"] = municipio
    datos_extraidos["parroquia"] = parroquia
    datos_extraidos["direccion_detallada"] = direccion_detallada

    return {"status": "success", "data": datos_extraidos}
