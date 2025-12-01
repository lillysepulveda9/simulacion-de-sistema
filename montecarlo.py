#----------------------------------STREAMLIT APP----------------------------------#
import streamlit as st
import pandas as pd
import random
import math

# ====== ESTILOS ======
st.markdown("""
<style>
.azul {
    color: #0066FF;
    font-weight: 600;
}
</style>
""", unsafe_allow_html=True)
# =====================

st.title("Simulación Montecarlo")
st.write("Esta aplicación tiene como finalidad resolver el problema del tiempo de falla (MTTF) de un satelite utilizando simulación Montecarlo.")

st.write("""
<span class='azul'>Problema:</span>  
Supongamos que tenemos un satélite, que para su funcionamiento depende de que al menos 2 paneles solares de los 5 que tiene disponibles estén en funcionamiento, y queremos calcular φ la vida útil esperada del satélite.
""", unsafe_allow_html=True)

# -------- PARÁMETROS ---------
st.write("<span class='azul'>### Parámetros de la simulación:</span>", unsafe_allow_html=True)

n = st.number_input(
    label="<span class='azul'>Número de simulaciones (n):</span>",
    min_value=1,
    value=6,
    step=1,
    format="%d",
    help="Cantidad de experimentos Montecarlo",
    key="n",
)

paneles = st.number_input(
    label="<span class='azul'>Número de paneles:</span>",
    min_value=1,
    value=5,
    step=1,
    format="%d",
    key="paneles",
)

panel_para_fallar = st.number_input(
    label="<span class='azul'>Número de paneles necesarios para que falle el satélite:</span>",
    min_value=1,
    value=4,
    step=1,
    format="%d",
    key="criterio",
)

st.write("<span class='azul'>Cada panel tiene vida útil uniforme en [1000, 5000], pero puedes cambiarlo:</span>", unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    limite_inferior = st.number_input(
        label="<span class='azul'>Límite inferior (hs):</span>",
        min_value=0,
        value=1000,
        step=100,
        format="%d",
        key="li",
    )

with col2:
    limite_superior = st.number_input(
        label="<span class='azul'>Límite superior (hs):</span>",
        min_value=limite_inferior + 1,
        value=5000,
        step=100,
        format="%d",
        key="ls",
    )

tecnica_reduccion = st.selectbox(
    label="<span class='azul'>Técnica de reducción de varianza:</span>",
    options=["Ninguna", "Variables Antitéticas", "Muestreo Estratificado (LHS)"],
    key="tecnica",
)

enviar = st.button("Ejecutar Simulación")

# (El resto de tu código sigue igual…)
