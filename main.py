from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
import io
import json
import os
import base64
import requests

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def inicio():
    return {"status": "online", "mensaje": "Backend RCV Operativo y Estable"}

@app.post("/api/procesar-documentos")
async def procesar_documentos(
    carnet_img: UploadFile = File(...),
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
    direccion_detallada: str = Form(...)
):
    try:
        # Leer la imagen subida desde el formulario web
        image_bytes = await carnet_img.read()
        image_base64 = base64.b64encode(image_bytes).decode("utf-8")
        
        # Obtener la API Key desde las variables de entorno de Render
        api_key = os.environ.get("GEMINI_API_KEY")
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
        
        prompt_texto = """
        Analiza esta imagen del carnet de circulación vehicular de Venezuela. 
        Extrae la información exacta y devuélvela ÚNICAMENTE en formato JSON plano, sin bloques de código markdown, sin comillas invertidas y sin texto adicional:
        {
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

        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": prompt_texto},
                        {
                            "inline_data": {
                                "mime_type": "image/jpeg",
                                "data": image_base64
                            }
                        }
                    ]
                }
            ]
        }

        headers = {"Content-Type": "application/json"}
        response = requests.post(url, json=payload, headers=headers)
        resultado_json = response.json()

        # Extraer los datos de la respuesta de la IA de forma segura
        if "candidates" in resultado_json and len(resultado_json["candidates"]) > 0:
            texto_generado = resultado_json["candidates"][0]["content"]["parts"][0]["text"]
            texto_limpio = texto_generado.replace("```json", "").replace("```", "").strip()
            datos_vehiculo = json.loads(texto_limpio)
        else:
            print("--- AVISO DE LA API ---")
            print(resultado_json)
            raise Exception("No se pudo obtener una respuesta válida de la IA")

    except Exception as e:
        print("--- ERROR EN ESCANEO DE IA (Usando valores por defecto seguros) ---")
        print(str(e))
        print("------------------------------------------------------------------")
        datos_vehiculo = {
            "placa": "POR-VERIFICAR",
            "marca": "Vehículo",
            "modelo": "General",
            "anio": "N/A",
            "serial_carroceria": "N/A",
            "serial_motor": "N/A",
            "color": "N/A",
            "puestos": "N/A",
            "peso": "N/A"
        }

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
        **datos_vehiculo
    }

    return {"status": "success", "data": resultado_final}
