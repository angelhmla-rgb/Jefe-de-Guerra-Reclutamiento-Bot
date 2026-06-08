import os
import io
import discord
from discord.ext import commands
import pandas as pd
from PIL import Image
import requests

TOKEN = os.getenv("DISCORD_TOKEN")
# Tu ID de canal donde se envía el mensaje automático y el tablero final
CANAL_ID = 1513230063225671750 

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# ================= CONFIGURACIÓN DE RUTAS =================
GITHUB_USER = "angelhmla-rgb"
GITHUB_REPO = "Jefe-de-Guerra-Reclutamiento-Bot"
GITHUB_BRANCH = "main"

URL_BASE_GITHUB = f"https://raw.githubusercontent.com/{GITHUB_USER}/{GITHUB_REPO}/{GITHUB_BRANCH}/iconos"
PLANTILLA_IMG = "Plantilla_Reclutamiento_Con_Cores.JPG"
# Reemplaza el texto de abajo con el ID largo de tu Google Sheet
GOOGLE_SHEET_ID = "1OfrieToO_D7RfNZbC79wvhCweViOBg8qNqHJh-uefFk"
URL_GOOGLE_SHEET = f"https://docs.google.com/spreadsheets/d/{GOOGLE_SHEET_ID}/export?format=xlsx"
OUTPUT_IMG = "update_reclutamiento.png"

# Coordenadas estimadas (X, Y) para ubicar los iconos al lado de cada Core
COORDENADAS_CORES = {
    "Core 1": (380, 275),
    "Core 2": (380, 362),
    "Core 3": (380, 450),
    "Core 4": (380, 538),
    "Core 5": (380, 626),
    "Core 6": (380, 714),
    "Core 7": (380, 808),
}

def descargar_icono_github(clase_esp):
    """Descarga el icono desde el repositorio en tiempo real"""
    url_icono = f"{URL_BASE_GITHUB}/{clase_esp}.png"
    try:
        respuesta = requests.get(url_icono)
        if respuesta.status_code == 200:
            return Image.open(io.BytesIO(respuesta.content)).convert("RGBA")
        else:
            print(f"⚠️ Icono no encontrado en GitHub: {clase_esp}.png")
            return None
    except Exception as e:
        print(f"❌ Error al conectar con GitHub para {clase_esp}: {e}")
        return None

def generar_imagen_reclutamiento():
    if not os.path.exists(PLANTILLA_IMG):
        raise FileNotFoundError(f"No se encuentra la plantilla '{PLANTILLA_IMG}' en la raíz.")
        
    imagen_final = Image.open(PLANTILLA_IMG).convert("RGBA")
    df = pd.read_excel(URL_GOOGLE_SHEET)
    
    for index, row in df.iterrows():
        # Asegúrate de que las columnas en tu Excel se llamen exactamente 'Core' y 'Clase'
        core_nombre = str(row['Core']).strip()
        clases_texto = str(row['Clase']).strip()
        
        if core_nombre in COORDENADAS_CORES and clases_texto and clases_texto != "nan":
            lista_clases = [c.strip() for c in clases_texto.split(",")]
            
            inicio_x, inicio_y = COORDENADAS_CORES[core_nombre]
            posicion_x_actual = inicio_x
            
            for clase_esp in lista_clases:
                if "_" not in clase_esp and len(clase_esp) > 15:
                    continue
                    
                icono = descargar_icono_github(clase_esp)
                if icono:
                    icono = icono.resize((56, 56))  # Tamaño ideal para las franjas
                    imagen_final.paste(icono, (posicion_x_actual, inicio_y), icono)
                    posicion_x_actual += 70  # Desplazamiento horizontal
                    
    imagen_final.save(OUTPUT_IMG, "PNG")
    return OUTPUT_IMG

@bot.event
async def on_ready():
    print(f"Conectado como {bot.user}")
    canal = bot.get_channel(CANAL_ID)
    if canal:
        await canal.send("✅ Bot conectado correctamente desde Railway y listo para procesar imágenes.")

@bot.command(name="reclutamiento")
async def actualizar_tabla(ctx):
    """Comando para purgar el canal por completo y enviar el tablero nuevo"""
    # Restringir para que solo se pueda usar en el canal de reclutamiento
    if ctx.channel.id != CANAL_ID:
        return
        
    try:
        # 🧹 PURGA ABSOLUTA: Borra los últimos 99 mensajes del canal (imágenes, textos, comandos)
        await ctx.channel.purge(limit=100)
        
        # Enviamos un mensaje temporal para que los oficiales sepan que está trabajando
        status_msg = await ctx.send("⏳ Leyendo Google Sheets y generando nuevo tablero limpio...")
        
        # Genera la nueva imagen con los iconos frescos
        archivo_imagen = generar_imagen_reclutamiento()
        file = discord.File(archivo_imagen)
        
        # Borramos el mensaje temporal justo antes de mandar el definitivo
        await status_msg.delete()
        
        # Publicamos el tablero definitivo de la hermandad
        await ctx.send("⚔️ **¡El Tablero de Reclutamiento de Jefe de Guerra ha sido actualizado!** ⚔️", file=file)
        
    except Exception as e:
        await ctx.send(f"❌ Error al procesar la limpieza o el tablero: {e}")

bot.run(TOKEN)
