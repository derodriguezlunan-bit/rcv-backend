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
    Analiza estas dos imágenes (Cédula de Identidad y Carnet de Circulación vehicular de Venezuela).
    Extrae con máxima precisión los siguientes datos en un formato JSON estricto:
    {
      "cedula": "",
      "nombre_completo": "",
      "estado": "",
      "ciudad": "",
      "municipio": "",
      "parroquia": "",
      "direccion_detallada": "",
      "placa": "",
      "marca": "",
      "modelo": "",
      "anio": "",
      "serial_carroceria": "",
      "serial_motor": "",
      "color": "",
      "puestos": "",
      "peso": ""
    }
    """

    response = model.generate_content([
        prompt,
        {"mime_type": cedula_img.content_type, "data": cedula_bytes},
        {"mime_type": carnet_img.content_type, "data": carnet_bytes}
    ])

    try:
        texto_limpio = response.text.replace("```json", "").replace("```", "").strip()
        datos_extraidos = json.loads(texto_limpio)
    except Exception as e:
        datos_extraidos = {"error": "No se pudieron extraer los datos con claridad", "detalle": response.text}

    datos_extraidos["telefono"] = telefono
    datos_extraidos["correo"] = correo
    datos_extraidos["tipo_vehiculo"] = tipo_vehiculo
    datos_extraidos["precio"] = precio

    return {"status": "success", "data": datos_extraidos}
