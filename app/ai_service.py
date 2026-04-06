import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

#Le damos la llave a la libreria de google
client = genai.Client(api_key=GEMINI_API_KEY)

#Usamos 'gemini-1.5-flash' porque es el modelooptimizado por Google para velocidad y
#tareas de texto rápidas (Tier Gratuito)
modelo_ia = "gemini-2.5-flash"

async def generar_resumen_nota(texto: str) -> str:
     
    #Colocamos una validacion de texto para no realizar peticiones si no existe texto
    if not texto:
        return "Sin texto para resumir"
     
    try:
        # Prompt Engineering: Le damos instrucciones claras y estrictas a la IA
        prompt = f"Actúa como un asistente de productividad. Lee el siguiente texto y genera un resumen en una sola frase corta y concisa de máximo 15 palabras. Texto: {texto}"

        # Hacemos la llamada a la IA
        respuesta = await client.aio.models.generate_content(
            model=modelo_ia,
            contents=prompt
        )
            
        #Retornamos la respuesta pero limpiamos el texto de espacios no deseados y saltos de linea
        return respuesta.text.strip()
    
    except Exception as e:
        # Prevención de fallos: Si Google se cae o el internet falla, devolvemos un mensaje de contingencia
        print(f"error en la IA: {e}")
        return "Resumen automatico no disponible temporalmente"