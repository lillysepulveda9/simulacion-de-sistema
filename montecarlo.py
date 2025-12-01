#----------------------------------STREAMLIT APP----------------------------------#
import streamlit as st
import pandas as pd
import random
import math

class Montecarlo:
    def __init__(self, num_variables=5, n_experimentos=6, criterio_sorteo=4, limite_inferior=1000, limite_superior=5000, tecnica_reduccion="ninguna"):
        self.num_variables = num_variables
        self.n_experimentos = n_experimentos
        self.criterio_sorteo = criterio_sorteo
        self.limite_inferior = limite_inferior
        self.limite_superior = limite_superior
        self.tecnica_reduccion = tecnica_reduccion.lower()
        self.crear_experimentos()
        self.sortear()
        self.metricas()

    def crear_experimentos(self):
        self.experimentos = []
        if self.tecnica_reduccion == "variables antitéticas":
            n_pares = self.n_experimentos // 2
            for i in range(n_pares):
                us = [random.random() for _ in range(self.num_variables)]
                experimento1 = [self.limite_inferior + (self.limite_superior - self.limite_inferior) * u for u in us]
                self.experimentos.append(experimento1)
                
                experimento2 = [self.limite_inferior + (self.limite_superior - self.limite_inferior) * (1 - u) for u in us]
                self.experimentos.append(experimento2)
            if self.n_experimentos % 2 == 1:
                experimento_extra = [random.uniform(self.limite_inferior, self.limite_superior) for _ in range(self.num_variables)]
                self.experimentos.append(experimento_extra)
        elif self.tecnica_reduccion == "muestreo estratificado (lhs)":
            n = self.n_experimentos
            d = self.num_variables
            lower_limits = [[float(k) / n for k in range(n)] for _ in range(d)]
            for j in range(d):
                random.shuffle(lower_limits[j])
            points = []
            for i in range(n):
                point = []
                for j in range(d):
                    strata_value = lower_limits[j][i] + random.random() / n
                    point.append(strata_value)
                points.append(point)
            for row in points:
                experimento = [self.limite_inferior + (self.limite_superior - self.limite_inferior) * p for p in row]
                self.experimentos.append(experimento)
        else:
            for i in range(self.n_experimentos):
                experimento_n = [random.randint(self.limite_inferior, self.limite_superior) for _ in range(self.num_variables)]
                self.experimentos.append(experimento_n)

    def sortear(self):
        satelite = []
        if self.tecnica_reduccion == "variables antitéticas":
            step = 2
            num_pares = self.n_experimentos // 2
            for i in range(0, 2 * num_pares, step):
                exp1 = sorted(self.experimentos[i])
                x1 = exp1[self.criterio_sorteo - 1]
                
                exp2 = sorted(self.experimentos[i + 1])
                x2 = exp2[self.criterio_sorteo - 1]
                
                satelite.append((x1 + x2) / 2)
            if self.n_experimentos % 2 == 1:
                exp_extra = sorted(self.experimentos[-1])
                satelite.append(exp_extra[self.criterio_sorteo - 1])
        else:
            for experimento in self.experimentos:
                experimento_sorted = sorted(experimento)
                satelite.append(experimento_sorted[self.criterio_sorteo - 1])
        self.satelite = satelite

    def metricas(self):
        if len(self.satelite) == 0:
            self.promedio_falla = 0
            self.desviacion_estandar_muestral = 0
            self.standard_error = 0
            return
        self.promedio_falla = sum(self.satelite) / len(self.satelite)
        if len(self.satelite) > 1:
            self.desviacion_estandar_muestral = math.sqrt(
                sum((x - self.promedio_falla)**2 for x in self.satelite) / (len(self.satelite) - 1)
            )
        else:
            self.desviacion_estandar_muestral = 0
        self.standard_error = self.desviacion_estandar_muestral / math.sqrt(len(self.satelite)) if len(self.satelite) > 0 else 0

    def retornar_resultados(self):
        lista = [self.satelite, round(self.promedio_falla, 2), round(self.desviacion_estandar_muestral, 2), round(self.standard_error, 2)]
        return self.experimentos, lista, self.satelite

simulacion1 = Montecarlo()  # los parametros finales de li,ls y media son opcionales segun yo para el area de parametrizacion pero no entendí bien la tarea jaja


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
