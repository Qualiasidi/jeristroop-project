import streamlit as st
import time
import random
import base64
import os

st.set_page_config(page_title="JeriStroop V15 - CULagos", page_icon="🧠", layout="centered")

# --- FUNCIONES DE APOYO ---
def get_video_base64(file_path):
    try:
        with open(file_path, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except:
        return None

# --- ESTILOS ---
st.markdown("""
<style>
.timer {font-size: 45px; color: #FF4B4B; text-align: center; font-weight: bold; margin-bottom: 20px;}
.word-box {text-align: center; font-size: 90px; font-weight: bold; padding: 25px; border: 3px solid #eee; border-radius: 20px; margin-bottom: 35px;}
.stButton>button {width: 100%; height: 65px; font-size: 22px; font-weight: bold; border-radius: 12px;}
.footer-legend {font-size: 15px; color: #555; text-align: center; margin-top: 60px; border-top: 1px solid #eee; padding-top: 25px; line-height: 1.5;}
</style>
""", unsafe_allow_html=True)

# --- INICIALIZACIÓN DE ESTADOS ---
if 'fase' not in st.session_state:
    st.session_state.update({
        'fase': "INICIO",
        'puntos': {"P": 0, "C": 0, "PC": 0},
        'new_stim': True,
        'word': "",
        'color_key': ""
    })

NOMBRES = ["ROJO", "AZUL", "VERDE"]
COLORES_HEX = {"ROJO": "#FF4B4B", "AZUL": "#1C83E1", "VERDE": "#2E7D32"}

# --- LÓGICA DE FLUJO ---

# 1. PANTALLA INICIAL (CRITERIOS DE VALIDEZ)
if st.session_state.fase == "INICIO":
    st.title("🧠 JeriStroop: Evaluación Neuropsicológica")
    st.markdown("### 📋 Requisitos de Validez Clínica")
    st.warning("""
    Para que los resultados de esta prueba sean confiables:
    1. El evaluado debe tener entre **7 y 80 años**.
    2. El evaluado debe saber **leer con fluidez**.
    """)
    st.write("Esta herramienta mide la agilidad mental, la atención selectiva y la resistencia a la interferencia cognitiva.")
    if st.button("CUMPLO LOS REQUISITOS - COMENZAR"):
        st.session_state.fase = "INST_P"
        st.rerun()

# 2. INSTRUCCIONES FASE P (PALABRAS)
elif st.session_state.fase == "INST_P":
    st.header("Fase 1: Lectura de Palabras")
    st.info("Instrucción: Lea las palabras que aparecen en pantalla y seleccione el botón del color que corresponda lo más rápido posible.")
    if st.button("¡ENTENDIDO, EMPEZAR!"):
        st.session_state.start_time = time.time(); st.session_state.fase = "P"; st.rerun()

# 3. TEST CORRIENDO (P, C, PC)
elif st.session_state.fase in ["P", "C", "PC"]:
    restante = 45 - (time.time() - st.session_state.start_time)
    if restante <= 0:
        if st.session_state.fase == "P": st.session_state.fase = "INST_C"
        elif st.session_state.fase == "C": st.session_state.fase = "INST_PC"
        else: st.session_state.fase = "RESULTADOS"
        st.session_state.new_stim = True; st.rerun()

    st.markdown(f'<div class="timer">⏱️ {max(0, restante):.1f}s</div>', unsafe_allow_html=True)
    if st.session_state.new_stim:
        st.session_state.word = random.choice(NOMBRES)
        if st.session_state.fase == "P": st.session_state.color_key = "NEGRO"
        elif st.session_state.fase == "C":
            st.session_state.word = "XXXX"; st.session_state.color_key = random.choice(NOMBRES)
        else: st.session_state.color_key = random.choice([c for c in NOMBRES if c != st.session_state.word])
        st.session_state.new_stim = False
    
    color_display = COLORES_HEX.get(st.session_state.color_key, "#000000")
    st.markdown(f'<div class="word-box" style="color: {color_display};">{st.session_state.word}</div>', unsafe_allow_html=True)
    cols = st.columns(3)
    for i, opcion in enumerate(NOMBRES):
        if cols[i].button(opcion):
            target = st.session_state.word if st.session_state.fase == "P" else st.session_state.color_key
            if opcion == target: st.session_state.puntos[st.session_state.fase] += 1
            st.session_state.new_stim = True; st.rerun()
    time.sleep(0.05); st.rerun()

# 4. INSTRUCCIONES FASE C (COLORES)
elif st.session_state.fase == "INST_C":
    st.header("Fase 2: Nombramiento de Colores")
    st.info("Instrucción: Identifique el color de las 'XXXX' que aparecen en pantalla lo más rápido posible.")
    if st.button("LISTO PARA FASE 2"):
        st.session_state.start_time = time.time(); st.session_state.fase = "C"; st.rerun()

# 5. INSTRUCCIONES FASE PC (INTERFERENCIA)
elif st.session_state.fase == "INST_PC":
    st.header("Fase 3: Interferencia Color-Palabra")
    st.warning("⚠️ ¡Atención! Identifique el COLOR DE LA PALABRA, ignorando el texto escrito.")
    if st.button("LISTO PARA EL RETO FINAL"):
        st.session_state.start_time = time.time(); st.session_state.fase = "PC"; st.rerun()

# 6. RESULTADOS FINALES MEJORADOS
elif st.session_state.fase == "RESULTADOS":
    st.title("📊 Informe de Resultados JeriStroop")
    P, C, PC = st.session_state.puntos["P"], st.session_state.puntos["C"], st.session_state.puntos["PC"]
    pc_esp = (C * P) / (C + P)
    interf = PC - pc_esp
    
    st.subheader("Resultados Obtenidos")
    c1, c2, c3 = st.columns(3)
    c1.metric("Lectura (P)", P)
    c2.metric("Colores (C)", C)
    c3.metric("Interferencia", f"{interf:.2f}")

    st.write("---")
    st.subheader("🧐 Análisis Detallado por Escala")

    # Escala 1
    st.info(f"**1. Lectura de Palabras (P): {P} aciertos**")
    st.write("Mide la velocidad de procesamiento verbal automático. Es un indicador de la agilidad del hemisferio izquierdo para decodificar símbolos lingüísticos.")

    # Escala 2
    st.info(f"**2. Nombramiento de Colores (C): {C} aciertos**")
    st.write("Evalúa la rapidez sensorial para reconocer y clasificar estímulos visuales puros (colores). Refleja la eficiencia neuropsicológica base.")

    # Escala 3
    st.info(f"**3. Condición de Interferencia (PC): {PC} aciertos**")
    st.write("Es la escala más compleja. Evalúa la capacidad de su cerebro para inhibir una respuesta automática (leer) a favor de una respuesta controlada (nombrar el color).")

    # Conclusión
    st.success(f"**Análisis de Resistencia a la Interferencia: {interf:.2f}**")
    interpretacion = "Usted posee una **Alta Resistencia** a la interferencia cognitiva." if interf > 0 else "Usted muestra una **Mayor Susceptibilidad** a estímulos distractores externos."
    st.write(f"Según el Manual de Golden, este índice refleja su nivel de flexibilidad cognitiva pura. {interpretacion}")

    st.write("---")

    # --- ROBOT Y VINCULACIÓN ---
    col_vid, col_btn = st.columns([1, 2])
    with col_vid:
        v64 = get_video_base64("jeribot.mp4")
        if v64:
            st.markdown(f'<video width="100%" autoplay loop muted playsinline><source src="data:video/mp4;base64,{v64}" type="video/mp4"></video>', unsafe_allow_html=True)
        else:
            st.write("🤖 *¡Excelente trabajo!*")

    with col_btn:
        st.write("Para integrar estos resultados a su expediente clínico en la Brigada Jericó, haga clic en el siguiente enlace:")
        link = f"https://t.me/Jeribotoficial?text=STROOP_DATA_P{P}_C{C}_PC{PC}_INT{interf:.2f}"
        st.markdown(f"### 📤 [VINCULAR CON MI EXPEDIENTE]({link})")

    st.markdown("""
    <div class="footer-legend">
        <b>¿Dudas o aclaraciones?</b><br>
        Favor de comunicarse con el equipo técnico al correo:<br>
        <a href="mailto:joel.anaya@jerico-udg.com">joel.anaya@jerico-udg.com</a>
    </div>
    """, unsafe_allow_html=True)

