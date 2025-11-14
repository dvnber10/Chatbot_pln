# 📘 Chatbot de Venta de Computadoras — README

## 🖥️ Descripción General

Este proyecto implementa un **chatbot inteligente para la venta de laptops** utilizando **FastAPI**, procesamiento de lenguaje natural (**NLP**) y un pequeño modelo generativo (GPT-2 español).

El chatbot entiende intenciones, recomienda productos Dell/HP/Lenovo, permite reservar un equipo, muestra el catálogo y utiliza un fallback generativo cuando no detecta la intención del usuario.

---

# 🚀 Tecnologías utilizadas

* **FastAPI** para la API
* **Spacy (es_core_news_sm)** para análisis NLP
* **NLTK** para tokenización
* **Transformers (HuggingFace)** para generación de texto
* **GPT-2 Small Spanish (`datificate/gpt2-small-spanish`)**
* **Sistema de sesión con historial en memoria**

---

# 🧠 Actualización Importante: Modificación Completa de `PLN_utils.py`

El archivo `PLN_utils.py` fue completamente **reescrito y ampliado**.
Ahora contiene un sistema NLP mucho más avanzado, con:

### ✔ Modelos NLP mejor cargados

```python
try:
    nltk.download('punkt_tab', quiet=True)
except:
    nltk.download('punkt', quiet=True)
```

### ✔ SpaCy con descarga automática

```python
try:
    pln = spacy.load("es_core_news_sm")
except:
    subprocess.check_call([sys.executable, "-m", "spacy", "download", "es_core_news_sm"])
    pln = spacy.load("es_core_news_sm")
```

### ✔ Inclusión de un modelo generativo GPT-2 español

El modelo se carga una sola vez gracias a `@lru_cache`:

```python
@lru_cache(maxsize=1)
def cargar_modelo_generativo():
    generator = pipeline('text-generation', model='datificate/gpt2-small-spanish')
    set_seed(42)
    return generator
```

### ✔ Catálogo detallado de productos

```python
CATALOGO = {
    "dell": {
        "Dell Inspiron 15": {...},
        "Dell XPS 13": {...},
        "Dell Alienware M15": {...}
    },
    ...
}
```

### ✔ Sistema de intenciones mejorado

La función `detectar_intencion()` identifica:

* saludos
* precios
* gaming
* trabajo
* barato
* catálogo
* marcas
* modelos específicos
* intención de reservar (“apartar”)

### ✔ Respuestas estructuradas según intención

Cada intención tiene su generador:

* `generar_respuesta_marca`
* `generar_respuesta_precio`
* `generar_respuesta_gaming`
* `generar_respuesta_trabajo`
* `generar_respuesta_barato`
* `generar_respuesta_modelo_especifico`
* `generar_respuesta_apartar_con_historial`

### ✔ Historial de conversación integrado

Ahora el chatbot:

* Recuerda el último modelo mencionado
* Permite reservar sin repetir el modelo
* Añade cada turno al historial interno

### ✔ Fallback generativo cuando no detecta intención

```python
resultado = GENERATOR(prompt, ...)
```

Si no hay coincidencias, responde pero **solo usando información del catálogo**.

---

# 📂 Estructura de Proyecto

```
src/
 ├── Controllers/
 │     └── chat_controller.py      # Endpoints FastAPI
 ├── Services/
 │     └── chat_service.py         # Lógica del servicio
 ├── Repositories/
 │     └── chat_repo.py            # Manejo de sesiones
 ├── Utils/
 │     └── PLN_utils.py            # NLP avanzado + catálogo + GPT2
 └── Models/
        chat_model.py
```

---

# 🔥 Endpoints principales

### **POST /api/chatbot/chat**

Enviar un mensaje al bot
Respuesta incluye:

* texto
* categoría detectada
* keyword
* sesión
* tiempo de respuesta

### **POST /api/chatbot/analyze**

Devuelve:

* tokens
* lemas
* POS tags

### **GET /api/chatbot/history/{session_id}**

Historial completo de la sesión.

### **GET /api/chatbot/session/{session_id}**

Información de la sesión.

### **GET /api/chatbot/stats**

Estadísticas del bot.

---

# 💬 Ejemplo de interacción

```
Usuario: hola  
Bot: ¡Hola! Bienvenido a nuestra tienda de laptops. ¿Qué tipo de equipo buscas?

Usuario: quiero algo para gaming  
Bot: Para gaming te recomiendo...

Usuario: reservar el alienware  
Bot: ¡Perfecto! Reservando el Dell Alienware M15...
```

---

# 📦 Instalación

```bash
pip install -r requirements.txt
python -m spacy download es_core_news_sm
```

---

# ▶️ Ejecutar servidor

```bash
uvicorn app:app --reload
```

---

# 📝 Notas finales

Este README documenta el nuevo funcionamiento del chatbot y explica claramente las modificaciones profundas hechas en `PLN_utils.py`, que ahora incluye:

* catálogo real
* motor generativo
* detección avanzada de intención
* sistema de historial
* manejo de reservas
* fallback seguro con GPT-2

