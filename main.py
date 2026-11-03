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

# Configurar la API Key de Gemini
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

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
        # Leer los bytes de la imagen subida
        imagen_bytes = await carnet_img.read()
        mime_type = carnet_img.content_type if carnet_img.content_type else "image/jpeg"

        # Inicializar el modelo Gemini 1.5 Flash
        model = genai.GenerativeModel('gemini-1.5-flash')

        prompt = """
        Analiza esta imagen del Carnet de Circulación vehicular de Venezuela.
        Extrae estrictamente los siguientes datos y respóndeme ÚNICAMENTE con un objeto JSON válido (sin texto antes ni después, ni bloques de código markdown):
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

        # Enviar prompt e imagen al modelo de IA
        response = model.generate_content([
            prompt,
            {"mime_type": mime_type, "data": imagen_bytes}
        ])

        # Limpiar la respuesta de la IA
        texto_limpio = response.text.strip()
        if texto_limpio.startswith("```json"):
            texto_limpio = texto_limpio[7:]
        if texto_limpio.startswith("```"):
            texto_limpio = texto_limpio[3:]
        if texto_limpio.endswith("```"):
            texto_limpio = texto_limpio[:-3]

        datos_vehiculo = json.loads(texto_limpio.strip())

    except Exception as e:
        print(f"Error en IA: {str(e)}")
        # Datos de respaldo detallados para identificar si falló la IA
        datos_vehiculo = {
            "placa": "ERROR_LECTURA_IA",
            "marca": "Verificar",
            "modelo": "Manual",
            "anio": "0000",
            "serial_carroceria": "N/A",
            "serial_motor": "N/A",
            "color": "N/A",
            "puestos": "N/A",
            "peso": "N/A"
        }

    # Consolidar nombre completo
    s_nombre = segundo_nombre if segundo_nombre else ""
    s_apellido = segundo_apellido if segundo_apellido else ""
    nombre_completo = f"{primer_nombre} {s_nombre} {primer_apellido} {s_apellido}".replace("  ", " ").strip()

    # Combinar con los datos del formulario
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
