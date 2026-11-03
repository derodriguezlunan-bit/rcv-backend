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
    cedula_img: UploadFile = File(...),
    carnet_img: UploadFile = File(...),
    telefono: str = Form(...),
    correo: str = Form(...),
    tipo_vehiculo: str = Form(...),
    precio: str = Form(...)
):
    cedula_bytes = await cedula_img.read()
    carnet_bytes = await carnet_img.read()

    prompt = """
    Analiza detalladamente estas dos imágenes adjuntas: la Cédula de Identidad y el Carnet de Circulación vehicular.
    Extrae la siguiente información real que aparece en los documentos y devuélvela UNICAMENTE en formato JSON plano (sin texto adicional, sin bloques de código markdown como ```json):
    {
      "cedula": "número de cédula con letra V o E",
      "nombre_completo": "nombre y apellido completo del titular",
      "estado": "estado de residencia",
      "ciudad": "ciudad",
      "municipio": "municipio",
      "parroquia": "parroquia",
      "direccion_detallada": "dirección exacta de domicilio",
      "placa": "número de placa del vehículo",
      "marca": "marca del carro o moto",
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
        {"mime_type": cedula_img.content_type, "data": cedula_bytes},
        {"mime_type": carnet_img.content_type, "data": carnet_bytes}
    ])

    texto_limpio = response.text.replace("```json", "").replace("```", "").strip()
    
    try:
        datos_extraidos = json.loads(texto_limpio)
    except:
        # Si llega a haber un fallo, rescatamos al menos el texto plano que leyó la IA
        datos_extraidos = {
            "cedula": "Revisar imagen",
            "nombre_completo": "Cliente RCV",
            "estado": "Miranda",
            "ciudad": "Guarenas",
            "municipio": "Plaza",
            "parroquia": "Guarenas",
            "direccion_detallada": texto_limpio[:100],
            "placa": "PENDIENTE",
            "marca": "Ver foto",
            "modelo": "Ver foto"
        }

    datos_extraidos["telefono"] = telefono
    datos_extraidos["correo"] = correo
    datos_extraidos["tipo_vehiculo"] = tipo_vehiculo
    datos_extraidos["precio"] = precio

    return {"status": "success", "data": datos_extraidos}
