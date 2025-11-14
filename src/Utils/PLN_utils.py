import nltk
from nltk.tokenize import word_tokenize
import spacy
from functools import lru_cache
import re
import random
from transformers import pipeline, set_seed


# --- DESCARGAS Y CARGA DE MODELOS ---
try:
    nltk.download('punkt_tab', quiet=True)
except:
    nltk.download('punkt', quiet=True)

try:
    pln = spacy.load("es_core_news_sm")
except:
    import subprocess, sys
    subprocess.check_call([sys.executable, "-m", "spacy", "download", "es_core_news_sm"])
    pln = spacy.load("es_core_news_sm")

# --- CARGA DEL MODELO GENERATIVO (CACHÉ) ---
@lru_cache(maxsize=1)
def cargar_modelo_generativo():
    try:
        generator = pipeline('text-generation', model='datificate/gpt2-small-spanish')
        set_seed(42)
        return generator
    except Exception as e:
        print(f"Error al cargar modelo: {e}")
        return None

GENERATOR = cargar_modelo_generativo()

# --- CATÁLOGO DE PRODUCTOS ---
CATALOGO = {
    "dell": {
        "Dell Inspiron 15": {"precio": 800, "ram": "16GB", "storage": "512GB SSD"},
        "Dell XPS 13": {"precio": 1200, "ram": "16GB", "storage": "1TB SSD", "extra": "pantalla 4K"},
        "Dell Alienware M15": {"precio": 1800, "ram": "32GB", "storage": "1TB SSD", "extra": "RTX 3070"}
    },
    "hp": {
        "HP Pavilion": {"precio": 600, "ram": "8GB", "storage": "1TB HDD"},
        "HP Envy 13": {"precio": 950, "ram": "16GB", "storage": "512GB SSD", "extra": "pantalla táctil"},
        "HP Omen 16": {"precio": 1500, "ram": "32GB", "storage": "1TB SSD", "extra": "RTX 3060"}
    },
    "lenovo": {
        "Lenovo ThinkPad X1 Carbon": {"precio": 1200, "ram": "32GB", "storage": "1TB SSD"},
        "Lenovo IdeaPad 5": {"precio": 700, "ram": "8GB", "storage": "512GB SSD"},
        "Lenovo Legion 5 Pro": {"precio": 1600, "ram": "32GB", "storage": "1TB SSD", "extra": "RTX 3070"}
    }
}

# --- TEMPLATES DE RESPUESTAS ---
RESPONSE_TEMPLATES = {
    "saludo": [
        "¡Hola! Bienvenido a nuestra tienda de laptops. ¿Qué tipo de equipo buscas?",
        "¡Hola! ¿En qué puedo ayudarte hoy? Tenemos Dell, HP y Lenovo.",
        "¡Buenas! Aquí estoy para ayudarte a elegir la laptop perfecta. ¿Qué necesitas?"
    ],
    "despedida": [
        "¡Gracias por tu consulta! Si necesitas algo más, aquí estaré.",
        "¡De nada! No dudes en volver si tienes más dudas.",
        "¡Hasta pronto! Espero haberte ayudado."
    ],
    "marca_general": "Trabajamos con **Dell** (profesional), **HP** (calidad-precio) y **Lenovo** (gaming y trabajo). ¿Cuál te interesa?",
    "precio_general": "Nuestros precios van desde **$600** (básicos) hasta **$1,800** (gaming). ¿Qué presupuesto tienes?",
    "catalogo_completo": """
**Dell:**
• Dell Inspiron 15: $800 - 16GB RAM, 512GB SSD
• Dell XPS 13: $1,200 - 16GB RAM, 1TB SSD, 4K
• Dell Alienware M15: $1,800 - 32GB RAM, RTX 3070

**HP:**
• HP Pavilion: $600 - 8GB RAM, 1TB HDD
• HP Envy 13: $950 - 16GB RAM, 512GB SSD, táctil
• HP Omen 16: $1,500 - 32GB RAM, RTX 3060

**Lenovo:**
• Lenovo ThinkPad X1: $1,200 - 32GB RAM, 1TB SSD
• Lenovo IdeaPad 5: $700 - 8GB RAM, 512GB SSD
• Lenovo Legion 5 Pro: $1,600 - 32GB RAM, RTX 3070
"""
}

# --- DETECCIÓN DE INTENCIÓN ---
def detectar_intencion(mensaje):
    mensaje_lower = mensaje.lower().strip()
    for marca, productos in CATALOGO.items():
        for nombre in productos.keys():
            palabras = nombre.lower().split()
            if len(palabras) >= 2:
                coincidencias = sum(1 for p in palabras if p in mensaje_lower)
                if coincidencias >= 2:
                    return "modelo_especifico", nombre
    if any(p in mensaje_lower for p in ["hola", "buenas", "hey", "saludos", "qué tal"]):
        return "saludo", "hola"
    if any(p in mensaje_lower for p in ["gracias", "adiós", "chao", "perfecto", "ok"]):
        return "despedida", "gracias"
    if any(p in mensaje_lower for p in ["gaming", "juegos", "gamer", "rtx", "gráficos"]):
        return "gaming", "gaming"
    if any(p in mensaje_lower for p in ["trabajo", "oficina", "profesional", "negocios"]):
        return "trabajo", "trabajo"
    if any(p in mensaje_lower for p in ["barato", "económico", "accesible", "bajo presupuesto"]):
        return "barato", "barato"
    if any(p in mensaje_lower for p in ["precio", "cuánto cuesta", "cuánto vale", "costo"]):
        return "precio", "precio"
    if any(p in mensaje_lower for p in ["catálogo", "catalogo", "opciones", "qué tienen", "ver todo", "laptop", "laptops", "computadora","computadoras"]):
        return "catalogo", "catalogo"
    if any(p in mensaje_lower for p in ["marca", "marcas", "fabricante"]):
        return "marca", "marca"
    if any(p in mensaje_lower for p in ["apartar", "reservar", "comprar"]):
        return "apartar", "apartar"
    if "dell" in mensaje_lower:
        return "dell", "dell"
    if "hp" in mensaje_lower:
        return "hp", "hp"
    if "lenovo" in mensaje_lower:
        return "lenovo", "lenovo"
    return "desconocido", None

# --- RESPUESTAS ---
def generar_respuesta_marca(marca):
    if marca not in CATALOGO:
        return RESPONSE_TEMPLATES["marca_general"]
    productos = CATALOGO[marca]
    respuesta = f"Estos son los modelos de **{marca.upper()}**:\n\n"
    for nombre, specs in productos.items():
        extra = f", {specs.get('extra', '')}" if specs.get('extra') else ""
        respuesta += f"• **{nombre}**: ${specs['precio']} - {specs['ram']}, {specs['storage']}{extra}\n"
    respuesta += "\n¿Cuál te interesa más?"
    return respuesta

def generar_respuesta_precio(mensaje):
    mensaje_lower = mensaje.lower()
    for marca in ["dell", "hp", "lenovo"]:
        if marca in mensaje_lower:
            return generar_respuesta_marca(marca)
    for marca, productos in CATALOGO.items():
        for nombre, specs in productos.items():
            if any(p in mensaje_lower for p in nombre.lower().split()):
                extra = f", {specs.get('extra', '')}" if specs.get('extra') else ""
                return f"El **{nombre}** cuesta **${specs['precio']}** ({specs['ram']}, {specs['storage']}{extra}). ¿Te interesa?"
    return RESPONSE_TEMPLATES["precio_general"]

def generar_respuesta_gaming():
    return """
Para gaming te recomiendo:

1. **Dell Alienware M15** - $1,800 (RTX 3070)
2. **Lenovo Legion 5 Pro** - $1,600 (RTX 3070)
3. **HP Omen 16** - $1,500 (RTX 3060)

¿Cuál se ajusta a tu presupuesto?
"""

def generar_respuesta_trabajo():
    return """
Para trabajo profesional:

1. **Lenovo ThinkPad X1** - $1,200 (32GB RAM)
2. **Dell XPS 13** - $1,200 (pantalla 4K)
3. **HP Envy 13** - $950 (táctil)

¿Qué tipo de trabajo haces?
"""

def generar_respuesta_barato():
    return """
Opciones económicas:

1. **HP Pavilion** - $600 (8GB RAM)
2. **Lenovo IdeaPad 5** - $700 (SSD)
3. **Dell Inspiron 15** - $800 (16GB RAM)

¿Cuál prefieres?
"""

def generar_respuesta_modelo_especifico(nombre_modelo, historial):
    for marca, productos in CATALOGO.items():
        if nombre_modelo in productos:
            specs = productos[nombre_modelo]
            caracteristicas = f"\n• **Precio:** ${specs['precio']}"
            caracteristicas += f"\n• **RAM:** {specs['ram']}"
            caracteristicas += f"\n• **Almacenamiento:** {specs['storage']}"
            if specs.get('extra'):
                caracteristicas += f"\n• **Extra:** {specs.get('extra')}"
            respuesta = f"El **{nombre_modelo}** tiene:{caracteristicas}\n\n¿Quieres reservarlo?"
            historial.append({"role": "assistant", "content": respuesta})
            return respuesta
    return "¿No lo encontré! Aquí tienes todo:\n\n" + RESPONSE_TEMPLATES["catalogo_completo"]

# --- DETECCIÓN DE MODELO EN HISTORIAL ---
def obtener_ultimo_modelo(historial):
    """
    Busca el último modelo mencionado o confirmado en el historial.
    Devuelve el nombre exacto del modelo si lo encuentra.
    """
    for msg in reversed(historial):
        # Buscar texto en 'content' o 'Modelo'
        texto = msg.get("content") or msg.get("Modelo") or ""
        texto_lower = texto.lower()
        for marca, productos in CATALOGO.items():
            for nombre in productos.keys():
                nombre_lower = nombre.lower()
                # Coincidencia exacta o al menos dos palabras del modelo
                palabras = nombre_lower.split()
                if nombre_lower in texto_lower or all(p in texto_lower for p in palabras):
                    return nombre
    return None


def generar_respuesta_apartar_con_historial(message, historial):
    mensaje_lower = message.lower()
    modelo_encontrado = None
    marca_encontrada = None

    # Paso 1: buscar modelo mencionado directamente en el mensaje
    for marca, productos in CATALOGO.items():
        for nombre in productos.keys():
            nombre_lower = nombre.lower()
            palabras_modelo = nombre_lower.split()
            # Si se menciona directamente el nombre completo o al menos dos palabras clave
            if nombre_lower in mensaje_lower or sum(1 for p in palabras_modelo if p in mensaje_lower) >= 2:
                modelo_encontrado = nombre
                marca_encontrada = marca
                break
        if modelo_encontrado:
            historial.append({"Modelo": modelo_encontrado})
            break

    # Paso 2: si no se menciona en el mensaje, buscar el último del historial
    if not modelo_encontrado:
        ultimo_modelo = obtener_ultimo_modelo(historial)
        if ultimo_modelo:
            for marca, productos in CATALOGO.items():
                if ultimo_modelo in productos:
                    modelo_encontrado = ultimo_modelo
                    marca_encontrada = marca
                    break

    # Paso 3: si aún no lo encuentra, pedir confirmación
    if not modelo_encontrado:
        return "No sé cuál laptop quieres reservar.\n¿Puedes decirme el modelo? (Ej: *Dell XPS 13*, *HP Omen 16*)"

    # Paso 4: construir la respuesta
    specs = CATALOGO[marca_encontrada][modelo_encontrado]
    extra = f", {specs.get('extra', '')}" if specs.get('extra') else ""
    respuesta = (
        f"¡Perfecto! Reservando el **{modelo_encontrado}** (${specs['precio']})\n"
        f"• RAM: {specs['ram']}\n"
        f"• Almacenamiento: {specs['storage']}{extra}\n\n"
        "**Reserva confirmada por 24 horas**\n"
        "Te enviaré un enlace de pago o puedes pasar por tienda.\n\n"
        "¿Agregar algo más?"
    )

    historial.append({"role": "assistant", "content": respuesta})
    return respuesta

# --- FALLBACK GENERATIVO ---
def generar_respuesta_generativa(mensaje, contexto_productos):
    if GENERATOR is None:
        return "No puedo generar respuesta ahora. Aquí tienes el catálogo:\n\n" + RESPONSE_TEMPLATES["catalogo_completo"]
    prompt = f"""Eres un asistente de ventas. Solo puedes hablar de estos productos:

{contexto_productos}

REGLAS:
- Responde en 1-2 oraciones.
- Usa solo datos del catálogo.
- NO inventes nada.
- Termina con una pregunta.

Usuario: {mensaje}
Asistente:"""
    try:
        resultado = GENERATOR(
            prompt,
            max_length=len(GENERATOR.tokenizer.encode(prompt)) + 50,
            num_return_sequences=1,
            do_sample=True,
            temperature=0.6,
            top_p=0.9,
            top_k=40,
            repetition_penalty=1.2,
            pad_token_id=GENERATOR.tokenizer.eos_token_id,
            eos_token_id=GENERATOR.tokenizer.eos_token_id
        )
        texto = resultado[0]['generated_text'][len(prompt):].strip()
        respuesta = re.split(r'[.!?]\s*|\n', texto)[0].strip()
        if len(respuesta) < 10:
            return "¿Podrías ser más específico? Aquí tienes el catálogo:\n\n" + RESPONSE_TEMPLATES["catalogo_completo"]
        if not respuesta.endswith(('.', '!', '?')):
            respuesta += "."
        if not "?" in respuesta:
            respuesta = respuesta[:-1] + ". ¿Te interesa?"
        return respuesta.capitalize()
    except Exception as e:
        print(f"Error GPT-2: {e}")
        return "No entendí bien. ¿Quieres ver el catálogo?"

# --- FUNCIÓN PRINCIPAL ---
historial = []
def response_chat(message):
    
    historial.append({"role": "user", "content": message})
    intencion, keyword = detectar_intencion(message)
    respuestas_rapidas = {
        "saludo": lambda: random.choice(RESPONSE_TEMPLATES["saludo"]),
        "despedida": lambda: random.choice(RESPONSE_TEMPLATES["despedida"]),
        "marca": lambda: RESPONSE_TEMPLATES["marca_general"],
        "catalogo": lambda: RESPONSE_TEMPLATES["catalogo_completo"],
        "precio": lambda: generar_respuesta_precio(message),
        "gaming": lambda: generar_respuesta_gaming(),
        "trabajo": lambda: generar_respuesta_trabajo(),
        "barato": lambda: generar_respuesta_barato(),
        "dell": lambda: generar_respuesta_marca("dell"),
        "hp": lambda: generar_respuesta_marca("hp"),
        "lenovo": lambda: generar_respuesta_marca("lenovo"),
        "apartar": lambda: generar_respuesta_apartar_con_historial(message, historial),
        "modelo_especifico": lambda: generar_respuesta_modelo_especifico(keyword, historial),
    }
    print(historial)
    if intencion in respuestas_rapidas:
        respuesta = respuestas_rapidas[intencion]()
        historial.append({"role": "assistant", "content": respuesta})
        return {
            "response": respuesta,
            "category": intencion,
            "matched_keyword": keyword,
            "response_time": "instant",
            "historial": historial
        }
    if intencion == "desconocido":
        contexto = "\n".join([
            f"- {nombre}: ${specs['precio']}, {specs['ram']}, {specs['storage']}{' (' + specs.get('extra','') + ')' if specs.get('extra') else ''}"
            for marca, productos in CATALOGO.items()
            for nombre, specs in productos.items()
        ])
        respuesta = generar_respuesta_generativa(message, contexto)
        historial.append({"role": "assistant", "content": respuesta})
        return {
            "response": respuesta,
            "category": "fallback_generativo",
            "matched_keyword": None,
            "response_time": "generative",
            "historial": historial
        }
    return {
        "response": RESPONSE_TEMPLATES["catalogo_completo"],
        "category": "fallback_final",
        "matched_keyword": None,
        "response_time": "instant",
        "historial": historial
    }
