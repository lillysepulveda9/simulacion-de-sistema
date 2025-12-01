#----------------------------------STREAMLIT APP----------------------------------#
import streamlit as st
import pandas as pd

st.title("Simulación Montecarlo")
st.write("Esta aplicación tiene como finalidad resolver el problema del tiempo de falla (MTTF) de un satelite utilizando simulación Montecarlo.")
st.write("Problema: Supongamos que tenemos un satélite, que para su funcionamiento depende de que al menos 2 paneles solares de los 5 que tiene disponibles estén en funcionamiento, y queremos calcular φ la vida útil esperada del satélite (el tiempo promedio de funcionamiento hasta que falla, usualmente conocido en la literatura como MTTF - Mean Time To Failure). Supongamos que cada panel solar tiene una vida útil que es aleatoria, y está uniformemente distribuída en el rango [1000 hs, 5000 hs] (valor promedio: 3000 hs). Para estimar por Monte Carlo el valor de φ, haremos n experimentos, cada uno de los cuales consistirá en sortear el tiempo de falla de cada uno de los paneles solares del satélite, y observar cual es el momento en el cuál han fallado 4 de los mismos, esta es la variable aleatoria cuya esperanza es el tiempo promedio de funcionamiento del satélite. El valor promedio de las n observaciones nos proporciona una estimación de φ.")
st.write("### Parámetros de la simulación: ")
n = st.number_input(
    "Número de simulaciones (n):",
    min_value=1,
    value=6,
    step=1
)
paneles = st.number_input(
    "Número de paneles: ",
    min_value=1,
    value=5
)
panel_para_fallar = st.number_input(
    "Número de paneles necesarios para que deje de funcionar el satélite",
    min_value=1,
    value=4
)
st.write("Cada panel tiene una vida útil uniformemente distribuída en el rango [1000 hs, 5000 hs]. Pero puedes variar el límite si gustas.")
col1, col2 = st.columns(2)
with col1:
    limite_inferior = st.number_input(
        "Límite inferior de la vida útil (hs):",
        min_value=0,
        value=1000,
        step=100
    )
with col2:
    limite_superior = st.number_input(
        "Límite superior de la vida útil (hs):",
        min_value=limite_inferior + 1,
        value=5000,
        step=100
    )
tecnica_reduccion = st.selectbox(
    "Técnica de reducción de varianza:",
    ["Ninguna", "Variables Antitéticas", "Muestreo Estratificado (LHS)"]
)
enviar = st.button("Ejecutar Simulación")
if enviar:
    st.write("### Simulación:")
    simulacion = Montecarlo(num_variables=paneles, n_experimentos=n, criterio_sorteo=panel_para_fallar, limite_inferior=limite_inferior, limite_superior=limite_superior, tecnica_reduccion=tecnica_reduccion)
    experimentos, resultados, satelite = simulacion.retornar_resultados()  # resultados son: lista = [satelite, promedio falla, desviacion estandar muestral, error estandar]
    for idx, i in enumerate(experimentos):
        i.sort()  # Ordenar los tiempos de paneles para coincidir con el ejemplo
        if simulacion.tecnica_reduccion == "variables antitéticas":
            i.append(satelite[idx // 2])
        else:
            i.append(satelite[idx])
    df = pd.DataFrame(experimentos, columns=[f'Panel {i+1}' for i in range(paneles)] + ['Satelite (xi)'])
    df.index += 1
    st.table(df)
    for i, texto in enumerate(["Promedio de tiempo de falla del sistema (satelite):", "Desviación estándar muestral:", "Error estándar:"]):
        st.write(f"**{texto}** {resultados[i+1]} hs")
