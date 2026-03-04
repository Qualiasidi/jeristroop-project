
import streamlit as st
import time
import random
import os
import urllib.parse
import traceback

# --- BLINDAJE ---
try:
    from fpdf import FPDF
except ImportError:
    st.error("⚠️ FPDF2 no está instalado. Ejecuta: pip install fpdf2")
    st.stop()

def recargar_app():
    if hasattr(st, 'rerun'): st.rerun()
    else: st.experimental_rerun()

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="JeriStroop - Brigada Jericó", page_icon="🧠", layout="wide")
IMG_LOGO = "jerico_logo.png"

# --- 1. ESTILOS VISUALES Y MODO ELÉCTRICO ---
st.markdown("""
    <style>
    .stApp {
        background: radial-gradient(circle, #08121a 0%, #102a43 50%, #08121a 100%);
        background-size: 200% 200%;
        animation: energiaStroop 5s ease infinite;
    }
    @keyframes energiaStroop { 0% { background-position: 0% 50%; } 50% { background-position: 100% 50%; } 100% { background-position: 0% 50%; } }
    
    h1, h2, h3, p, label, .stMarkdown, .stMetric, .stMetricValue { color: #ffffff !important; text-shadow: 0px 0px 8px #1C83E1; }
    
    .stException { background-color: white !important; padding: 15px; border-radius: 10px; }
    .stException * { color: black !important; text-shadow: none !important; }

    .timer {font-size: 50px; color: #FF4B4B; text-align: center; font-weight: bold; margin-bottom: 10px; text-shadow: 0px 0px 15px #FF4B4B;}
    
    .word-box {
        text-align: center; font-size: 85px; font-weight: bold; padding: 25px; 
        background-color: rgba(0, 0, 0, 0.6); border: 3px solid #1C83E1; 
        border-radius: 20px; margin-bottom: 35px; box-shadow: 0 0 20px rgba(28, 131, 225, 0.5);
    }
    
    @keyframes pulsoBtn { 0% { box-shadow: 0 0 10px #1C83E1, inset 0 0 5px #1C83E1; } 50% { box-shadow: 0 0 25px #1C83E1, inset 0 0 10px #1C83E1; } 100% { box-shadow: 0 0 10px #1C83E1, inset 0 0 5px #1C83E1; } }
    div[data-testid="stButton"] button {
        animation: pulsoBtn 1.5s infinite; border: 2px solid #1C83E1 !important; background-color: #000000 !important; color: #ffffff !important; height: 80px !important; font-size: 30px !important; border-radius: 12px;
    }
    div[data-testid="stButton"] button p { font-size: 30px !important; }
    </style>
""", unsafe_allow_html=True)

# --- 2. LÓGICA CLÍNICA (NIVELES STROOP) ---
def obtener_diagnostico_stroop(ig):
    if ig > 10:
        return "resistencia superior", "capacidad sobresaliente para inhibir respuestas automáticas. La corteza prefrontal gestiona el conflicto semántico con máxima eficiencia."
    elif ig > 0:
        return "resistencia normal alta", "adecuado control inhibitorio. Se resiste la interferencia de manera efectiva sin signos de alteración."
    elif ig == 0:
        return "interferencia promedio", "desempeño acorde a lo esperado. El control inhibitorio está equilibrado con la velocidad base de lectura."
    elif ig >= -10:
        return "susceptibilidad leve", "dificultad leve para resistir la distracción cognitiva. Mayor esfuerzo prefrontal requerido para bloquear el automatismo."
    else:
        return "susceptibilidad severa", "falla significativa en el control inhibitorio frontal. Altamente susceptible a la interferencia semántica."

# --- 3. INICIALIZACIÓN DE ESTADOS ---
if 'fase' not in st.session_state:
    st.session_state.update({
        'fase': "INICIO", 'puntos': {"P": 0, "C": 0, "PC": 0}, 'errores': {"P": 0, "C": 0, "PC": 0},
        'new_stim': True, 'word': "", 'color_key': "", 'start_time': None, 'observaciones': ""
    })

NOMBRES = ["ROJO", "AZUL", "VERDE"]
COLORES_HEX = {"ROJO": "#FF4B4B", "AZUL": "#4DA8DA", "VERDE": "#2ECC71", "NEGRO": "#FFFFFF"}

# --- 4. BARRA LATERAL ---
if os.path.exists(IMG_LOGO): st.sidebar.image(IMG_LOGO, width=180)
else: st.sidebar.title("🧠 Brigada Jericó")

st.sidebar.markdown("---")
st.sidebar.caption("Para dudas o aclaraciones, favor de comunicarse con el equipo técnico al correo: **joel.anaya@jerico-udg.com**")

nombre = st.sidebar.text_input("Nombre del participante:")
edad = st.sidebar.number_input("Edad cronológica:", min_value=7, max_value=99, step=1, value=25)

if not nombre:
    st.title("🧠 JeriStroop")
    st.info("👋 Ingresa tu nombre y edad en la barra lateral para comenzar.")
    st.stop()

# --- 5. CLASE PDF ---
class ConstanciaStroop(FPDF):
    def header(self):
        self.set_draw_color(28, 131, 225); self.set_line_width(1); self.rect(5, 5, 200, 287)
        self.set_fill_color(16, 42, 67); self.rect(5, 5, 200, 45, 'F')
        if os.path.exists(IMG_LOGO): self.image(IMG_LOGO, 12, 12, 22)
        
        self.set_y(10); self.set_x(38); self.set_font("helvetica", "B", 12); self.set_text_color(255)
        self.cell(0, 6, "JERIBOT Y JERISTROOP:", ln=True, align="C")
        self.set_x(38); self.set_font("helvetica", "B", 10)
        self.multi_cell(0, 5, "Modelos didácticos de inteligencia artificial para la divulgación de la neuroanatomía funcional y el triaje inteligente", align="C")
        self.set_x(38); self.set_font("helvetica", "", 9)
        self.cell(0, 6, "Semana del Cerebro 2026 - CULagos / Brigada Social Jericó", ln=True, align="C")
        self.ln(12)

# --- 6. FLUJO DEL JUEGO ---
if st.session_state.fase == "INICIO":
    st.title(f"Bienvenid@, {nombre}")
    
    st.markdown("""
    ### 🧠 ¿Qué es JeriStroop?
    Es una adaptación digital del **Test de Colores y Palabras (Stroop)**. Esta herramienta mide la **velocidad de procesamiento**, la **atención sostenida** y la **resistencia a la interferencia cognitiva**.
    
    ### ⏱️ Estructura de la prueba
    Consta de 3 fases de **45 segundos** cada una:
    1. **Fase de palabras (P):** velocidad de lectura automática.
    2. **Fase de colores (C):** velocidad para procesar estímulos visuales (color de tinta).
    3. **Fase de interferencia (PC):** control inhibitorio. Tendrás que nombrar el color de la tinta, ignorando la palabra escrita.
    
    ### ⚠️ Regla de oro (Penalización por Impulsividad):
    **Si cometes un error, la figura NO avanzará.** Deberás corregir tu respuesta. Oprimir botones al azar anulará tus resultados matemáticos y registrará un patrón de impulsividad clínica.
    """)

    with st.expander("🌟 Detalles de la adaptación y mejoras (JeriStroop vs Stroop físico de Golden, 2001)"):
        st.markdown("""
        Esta versión digital (JeriStroop) incorpora mejoras metodológicas superiores a la prueba de papel original:
        - 🚀 **Efecto techo nulo:** en la prueba física, el paciente tiene un máximo de 100 ítems en la hoja. Los pacientes muy ágiles pueden terminar antes de los 45s. JeriStroop genera estímulos infinitos, midiendo el verdadero límite cognitivo.
        - ⏱️ **Precisión en milisegundos:** elimina el sesgo de error de reacción humana con el cronómetro de mano del evaluador.
        - 🔀 **Aleatorización dinámica:** en la prueba de papel, los estímulos siempre están en el mismo orden espacial. JeriStroop aleatoriza cada ítem, exigiendo procesamiento ejecutivo puro.
        - 🔒 **Filtro algorítmico de impulsividad:** el software no solo bloquea el avance ante un error, sino que audita la tasa de equivocaciones. Si detecta un patrón de respuestas al azar, anula la fórmula matemática y diagnostica la impulsividad en tiempo real.
        """)
    
    if st.button("🚀 COMPRENDO LAS REGLAS - COMENZAR", use_container_width=True):
        st.session_state.fase = "INST_P"
        recargar_app()

elif st.session_state.fase == "INST_P":
    st.header("📖 Fase 1: Lectura de palabras (P)")
    st.info("**Instrucción:** aparecerán nombres de colores escritos en blanco. Toca el botón que corresponda a la palabra escrita lo más rápido posible.\n\n⏳ Tiempo: 45 segundos.")
    if st.button("▶️ INICIAR FASE 1", use_container_width=True):
        st.session_state.start_time = time.time(); st.session_state.fase = "P"; recargar_app()

elif st.session_state.fase == "INST_C":
    st.header("🎨 Fase 2: Nombramiento de colores (C)")
    st.info("**Instrucción:** aparecerán las letras 'XXXX' impresas en distintos colores. Toca el botón del color de la tinta lo más rápido posible.\n\n⏳ Tiempo: 45 segundos.")
    if st.button("▶️ INICIAR FASE 2", use_container_width=True):
        st.session_state.start_time = time.time(); st.session_state.fase = "C"; recargar_app()

elif st.session_state.fase == "INST_PC":
    st.header("⚡ Fase 3: Interferencia (PC)")
    st.warning("**¡ATENCIÓN!** Aparecerá el nombre de un color, pero escrito con tinta de un color diferente. **TOCA EL BOTÓN QUE CORRESPONDA AL COLOR DE LA TINTA**, ignorando lo que dice la palabra.\n\n⏳ Tiempo: 45 segundos.")
    if st.button("▶️ INICIAR RETO FINAL", use_container_width=True):
        st.session_state.start_time = time.time(); st.session_state.fase = "PC"; recargar_app()

elif st.session_state.fase in ["P", "C", "PC"]:
    restante = 45 - (time.time() - st.session_state.start_time)
    
    if restante <= 0:
        if st.session_state.fase == "P": st.session_state.fase = "INST_C"
        elif st.session_state.fase == "C": st.session_state.fase = "INST_PC"
        else: st.session_state.fase = "RESULTADOS"
        st.session_state.new_stim = True
        recargar_app()

    st.markdown(f'<div class="timer">⏱️ {max(0, restante):.1f} s</div>', unsafe_allow_html=True)
    
    if st.session_state.new_stim:
        st.session_state.word = random.choice(NOMBRES)
        if st.session_state.fase == "P": 
            st.session_state.color_key = "NEGRO"
        elif st.session_state.fase == "C":
            st.session_state.word = "XXXX"
            st.session_state.color_key = random.choice(NOMBRES)
        else:
            opciones_color = [c for c in NOMBRES if c != st.session_state.word]
            st.session_state.color_key = random.choice(opciones_color)
        st.session_state.new_stim = False
    
    color_display = COLORES_HEX.get(st.session_state.color_key, "#FFFFFF")
    st.markdown(f'<div class="word-box" style="color: {color_display};">{st.session_state.word}</div>', unsafe_allow_html=True)
    
    cols = st.columns(3)
    for i, opcion in enumerate(NOMBRES):
        if cols[i].button(opcion, key=f"btn_{opcion}", use_container_width=True):
            target = st.session_state.word if st.session_state.fase == "P" else st.session_state.color_key
            if opcion == target:
                st.session_state.puntos[st.session_state.fase] += 1
                st.session_state.new_stim = True
            else:
                st.session_state.errores[st.session_state.fase] += 1
                st.toast("❌ Error. Corrige tu respuesta.", icon="🚨")
            recargar_app()
            
    time.sleep(0.5)
    recargar_app()

elif st.session_state.fase == "RESULTADOS":
    try:
        st.title("📊 Informe Clínico JeriStroop")
        
        P = st.session_state.puntos["P"]
        C = st.session_state.puntos["C"]
        PC = st.session_state.puntos["PC"]
        err_P = st.session_state.errores["P"]
        err_C = st.session_state.errores["C"]
        err_PC = st.session_state.errores["PC"]
        
        # --- FILTROS CLÍNICOS ANTI-TRAMPA Y ANTI-BULLSHIT ---
        suma_pc = P + C if (P + C) > 0 else 1
        pc_esp = (C * P) / suma_pc
        interf = PC - pc_esp

        # 1. Filtro de Baja Cooperación
        if P < 10 or C < 10:
            diag_corto = "prueba inválida (datos insuficientes)"
            desc_diag = "el número de ítems alcanzados en las fases base es demasiado bajo. Es matemáticamente imposible calcular un índice válido. Sugiere falta de cooperación, barrera del lenguaje o alteración motora severa."
            color_borde = "#FF4B4B"
            interf = 0.0
        # 2. Filtro de Impulsividad (Spam de botones)
        elif err_P > (P * 0.3) or err_C > (C * 0.3) or err_PC > (PC * 0.3) or err_PC >= 6:
            diag_corto = "susceptibilidad severa (impulsividad clínica)"
            desc_diag = "se detectó una tasa de errores anormalmente alta que invalida la fórmula matemática original. Este patrón de respuestas al azar refleja un fallo grave en el automonitoreo y control inhibitorio prefrontal."
            color_borde = "#FF4B4B"
        # 3. Cálculo Normal
        else:
            diag_corto, desc_diag = obtener_diagnostico_stroop(interf)
            color_borde = '#2ECC71' if interf >= 0 else '#FF4B4B'
        
        st.success("### ¡Gracias por hacerlo lo mejor posible!")
        
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Ítems Lectura (P)", P, delta=f"-{err_P} errores", delta_color="normal")
        c2.metric("Ítems Colores (C)", C, delta=f"-{err_C} errores", delta_color="normal")
        c3.metric("Ítems Interf. (PC)", PC, delta=f"-{err_PC} errores", delta_color="normal")
        c4.metric("Índice Final (IG)", f"{interf:.2f}")

        st.markdown(f"""
        <div style="padding: 15px; border-radius: 10px; border: 2px solid {color_borde}; background-color: rgba(0,0,0,0.4);">
            <h3 style="margin-top:0;">📋 Diagnóstico de interferencia: {diag_corto.capitalize()}</h3>
            <p><strong>Interpretación clínica:</strong> {desc_diag}</p>
        </div>
        <br>
        """, unsafe_allow_html=True)

        st.markdown("### 📝 Registro Clínico Cualitativo")
        st.session_state.observaciones = st.text_area("¿Hubo algún distractor externo, fatiga, falla técnica o situación que afectara tu desempeño? (Opcional)", 
                                     value=st.session_state.observaciones, placeholder="Ej. 'Había mucho ruido en la sala', 'Me distrajo el teléfono'...")

        with st.expander("📊 Transparencia de baremos basada en prueba neuropsicológica estandarizada (Golden, 2001)"):
            st.markdown(f"""
            Has registrado **{edad} años**. El manual especifica correcciones normativas (Puntuaciones T) que varían significativamente según la edad cronológica. 
            - **Adultos mayores (65-80 años):** Se aplican correcciones directas (+14 en P, +11 en C, +15 en PC) para compensar la lentificación natural.
            - **Niños (7-14 años):** Se aplican correcciones decrecientes por maduración del lóbulo frontal.
            
            Para propósitos de cribado rápido e independiente de la edad, esta aplicación utiliza el **Índice de Interferencia Bruto (IG)**, que es el indicador más robusto de control inhibitorio puro.
            
            **Fórmulas clínicas aplicadas:**
            """)
            st.latex(r"PC_{esperado} = \frac{P \times C}{P + C}")
            st.latex(r"Interferencia (IG) = PC_{obtenido} - PC_{esperado}")
            st.markdown("""
            **Escala diagnóstica del Índice de Interferencia (IG):**
            - **> 10 (resistencia superior):** capacidad sobresaliente.
            - **1 a 10 (resistencia normal alta):** control inhibitorio óptimo.
            - **0 (interferencia promedio):** desempeño acorde a la expectativa matemática.
            - **-1 a -10 (susceptibilidad leve):** dificultad leve para resistir distracción.
            - **< -10 (susceptibilidad severa):** vulnerabilidad frontal significativa a la interferencia.
            """)

        texto_telegram = f"JeriStroop_Resultados\nNombre:{nombre}\nEdad:{edad}\nLectura(P):{P}_Err:{err_P}\nColores(C):{C}_Err:{err_C}\nInterf(PC):{PC}_Err:{err_PC}\nIG:{interf:.2f}\nDiag:{diag_corto.replace(' ','_')}\nObs:{st.session_state.observaciones}"
        link_tg = f"https://t.me/Jeribotoficial?text={urllib.parse.quote(texto_telegram)}"
        
        st.markdown(f"### 📤 [ENVIAR EXPEDIENTE COMPLETO A JERIBOT]({link_tg})")

        # --- CONSTANCIA PDF ---
        try:
            pdf = ConstanciaStroop()
            pdf.add_page()
            pdf.set_y(55)
            
            pdf.set_font("helvetica", "B", 16); pdf.set_text_color(28, 131, 225)
            pdf.cell(0, 8, "CONSTANCIA DE PARTICIPACIÓN", ln=True, align="C")
            pdf.ln(5)
            
            pdf.set_font("helvetica", "", 12); pdf.set_text_color(0)
            pdf.cell(0, 6, "La Brigada Social Jericó reconoce a:", ln=True, align="C")
            pdf.set_font("helvetica", "B", 16); pdf.set_text_color(243, 156, 18)
            pdf.cell(0, 10, f"{nombre.upper()} ({edad} años)", ln=True, align="C")
            pdf.ln(5)
            
            pdf.set_fill_color(240, 240, 240); pdf.set_text_color(0)
            pdf.set_font("helvetica", "B", 11)
            pdf.cell(0, 6, " RESULTADOS CLÍNICOS", fill=True, ln=True)
            pdf.set_font("helvetica", "I", 9)
            pdf.cell(0, 6, " Basados en prueba neuropsicológica estandarizada (Golden, 2001).", fill=True, ln=True)
            
            pdf.set_font("helvetica", "", 10)
            pdf.cell(0, 6, f"  - Ítems alcanzados lectura (P): {P} (Errores: {err_P})", ln=True)
            pdf.cell(0, 6, f"  - Ítems alcanzados colores (C): {C} (Errores: {err_C})", ln=True)
            pdf.cell(0, 6, f"  - Ítems alcanzados interferencia (PC): {PC} (Errores: {err_PC})", ln=True)
            pdf.cell(0, 6, f"  - Índice final de interferencia (IG): {interf:.2f}", ln=True)
            pdf.ln(5)
            
            pdf.set_font("helvetica", "B", 13); pdf.set_text_color(28, 131, 225)
            pdf.cell(0, 8, f"DIAGNÓSTICO OBTENIDO: {diag_corto.upper()}", border=1, ln=True, align="C")
            pdf.ln(3)
            pdf.set_font("helvetica", "I", 9); pdf.set_text_color(50, 50, 50)
            pdf.multi_cell(0, 5, f"Interpretación clínica: {desc_diag}", align="J")
            
            pdf.ln(15)
            pdf.set_text_color(26, 82, 118); pdf.set_font("courier", "B", 14)
            pdf.cell(0, 5, "[ o _ o ]", ln=True, align="C") 
            pdf.set_font("times", "I", 26) 
            pdf.cell(0, 8, "J . B o t", ln=True, align="C") 
            
            x_start = 90; y_pos = pdf.get_y()
            pdf.set_line_width(0.6); pdf.set_draw_color(26, 82, 118)
            pdf.line(x_start, y_pos, x_start + 30, y_pos - 3)
            pdf.line(x_start + 30, y_pos - 3, x_start + 20, y_pos + 1)
            pdf.line(x_start + 20, y_pos + 1, x_start + 40, y_pos - 1)
            
            pdf.ln(5)
            pdf.set_text_color(0); pdf.set_font("helvetica", "", 10)
            pdf.cell(0, 5, "Mascota virtual de la Brigada Social Jericó", ln=True, align="C")

            pdf_path = f"ConstanciaStroop_{nombre.replace(' ', '_')}.pdf"
            pdf.output(pdf_path)
            
            st.markdown("---")
            with open(pdf_path, "rb") as f:
                st.download_button("🎓 Descargar constancia clínica (PDF)", f, file_name=pdf_path)
                
        except Exception as e:
            st.error(f"Error interno PDF: {e}")

        if st.button("🔄 REALIZAR LA PRUEBA DE NUEVO (Resetea estado)", use_container_width=True):
            st.session_state.clear()
            recargar_app()
            
    except Exception as e:
        st.error(f"Error al procesar los resultados: {e}")
        st.code(traceback.format_exc())
