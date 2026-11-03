from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
import google.generativeai as genai
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

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
        # Leer los bytes de la imagen
        image_bytes = await carnet_img.read()
        
        # Usar la forma directa y oficial de Gemini para imágenes
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        prompt = """
        Analiza esta imagen de un carnet de circulación vehicular. 
        Extrae estrictamente en formato JSON plano (sin texto adicional ni marcas de código) lo siguiente:
        {
          "placa": "valor",
          "marca": "valor",
          "modelo": "valor",
          "anio": "valor",
          "serial_carroceria": "valor",
          "serial_motor": "valor",
          "color": "valor",
          "puestos": "valor",
          "peso": "valor"
        }
        """

        # Enviar imagen como un diccionario de partes
        response = model.generate_content([
            prompt,
            {
                "mime_type": carnet_img.content_type or "image/jpeg",
                "data": image_bytes
            }
        ])

        # Limpiar texto de respuesta
        texto = response.text.replace("```json", "").replace("```", "").strip()
        import json
        datos_vehiculo = json.loads(texto)

    except Exception as e:
        print("EXCEPCIÓN REAL:", str(e))
        datos_vehiculo = {
            "placa": "ERROR-IA",
            "marca": "Verificar",
            "modelo": "Manual",
            "anio": "0000",
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
