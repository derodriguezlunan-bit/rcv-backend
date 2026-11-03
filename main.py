from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
import google.generativeai as genai
from PIL import Image
import io
import json
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configurar la API Key
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

@app.get("/")
async def inicio():
    return {"status": "online", "mensaje": "Backend RCV operativo"}

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
        image_bytes = await carnet_img.read()
        imagen_pil = Image.open(io.BytesIO(image_bytes))
        
        # Usar directamente el modelo estándar reconocido por la librería
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        prompt = """
        Analiza esta imagen del carnet de circulación vehicular. 
        Extrae la información y devuélvela ÚNICAMENTE en formato JSON plano, sin bloques de código markdown ni texto adicional:
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

        response = model.generate_content([prompt, imagen_pil])

        texto = response.text.replace("```json", "").replace("```", "").strip()
        datos_vehiculo = json.loads(texto)

    except Exception as e:
        print("--- ERROR EN PROCESAMIENTO IA ---")
        print(str(e))
        print("--------------------------------")
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
