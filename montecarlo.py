#---------------------------------- STREAMLIT APP ----------------------------------#
import streamlit as st
import pandas as pd
import random
import math

# ====== ESTILOS GLOBALES ======
st.markdown("""
<style>
h1, h2, h3, h4 {
    color: #0066FF !important;
}
</style>
""", unsafe_allow_html=True)
# ===================================================================


# ===================== CLASE MONTECARLO ============================
class Montecarlo:
    def __init__(self, num_variables=5, n_experimentos=6, criterio_sorteo=4, 
                 limite_inferior=1000, limite_superior=5000, tecnica_reduccion="ninguna"):

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

        # VARIABLES ANTITÉTICAS
        if self.tecnica_reduccion == "variables antitéticas":
            n_pares = self.n_experimentos // 2
            for i in range(n_pares):
                us = [random.random() for _ in range(self.num_variables)]
                exp1 = [self.limite_inferior + (self.limite_superior - self.limite_inferior) * u for u in us]
                exp2 = [self.limite_inferior + (self.limite_superior - self.limite_inferior) * (1 - u) for u in us]
                self.experimentos.append(exp1)
                self.experimentos.append(exp2)
            if self.n_experimentos % 2 == 1:
                extra = [random.uniform(self.limite_inferior, self.limite_superior) for _ in range(self.num_variables)]
                self.experimentos.append(extra)

        # MUESTREO ESTRATIFICADO (LHS)
        elif self.tecnica_reduccion == "muestreo estratificado (lhs)":
            n = self.n_experimentos
            d = self.num_variables
            lower_limits = [[float(k) / n for k in range(n)] for _ in range(d)]
            for j in range(d):
                random.shuffle(lower_limits[j])
            points = []
            for i in range(n):
                point = [lower_limits[j][i] + random.random() / n for j in range(d)]
                points.append(point)
            for row in points:
                exp = [self.limite_inferior + (self.limite_superior - self.limite_inferior) * p for p in row]
                self.experimentos.append(exp)

        # SIN REDUCCIÓN DE VARIANZA
        else:
            for i in range(self.n_experimentos):
                exp = [random.randint(self.limite_inferior, self.limite_superior) for _ in range(self.num_variables)]
                self.experimentos.append(exp)

    def sortear(self):
        satelite = []

        if self.tecnica_reduccion == "variables antitéticas":
            step = 2
            num_pares = self.n_experimentos // 2
            for i in range(0, 2 * num_pares, step):
                exp1 = sorted(self.experimentos[i])
                exp2 = sorted(self.experimentos[i + 1])
                x1 = exp1[self.criterio_sorteo - 1]
                x2 = exp2[self.criterio_sorteo - 1]
                satelite.append((x1 + x2) / 2)
            if self.n_experimentos % 2 == 1:
                exp_extra = sorted(self.experimentos[-1])
                satelite.append(exp_extra[self.criterio_sorteo - 1])

        else:
            for experimento in self.experimentos:
                exp_sorted = sorted(experimento)
                satelite.append(exp_sorted[self.criterio_sorteo - 1])

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

        self.standard_error = (
            self.desviacion_estandar_muestral / math.sqrt(len(self.satelite))
            if len(self.satelite) > 0 else 0
        )

    def retornar_resultados(self):
        lista = [
            self.satelite,
            round(self.promedio_falla, 2),
            round(self.desviacion_estandar_muestral, 2),
            round(self.standard_error, 2)
        ]
        return self.experimentos, lista, self.satelite
# ===================================================================



# ===================== STREAMLIT UI ================================
st.title("Simulación Montecarlo")

st.header("Problema:")
st.write("""
Supongamos que tenemos un satélite que depende de 5 paneles solares.  
Queremos estimar el tiempo hasta que falla el sistema (MTTF),  
simulando la vida útil de los paneles (uniforme entre 1000 y 5000 hs).
""")

st.subheader("Parámetros de la simulación:")

# Inputs
n = st.number_input("Número de simulaciones (n):", min_value=1, value=6, step=1)
paneles = st.number_input("Número de paneles:", min_value=1, value=5)
panel_para_fallar = st.number_input("Número de paneles necesarios para que deje de funcionar el satélite:", min_value=1, value=4)

st.write("Cada panel tiene vida útil uniforme en el rango [1000, 5000]. Puedes modificar los límites:")

col1, col2 = st.columns(2)
with col1:
    limite_inferior = st.number_input("Límite inferior (hs):", min_value=0, value=1000, step=100)
with col2:
    limite_superior = st.number_input("Límite superior (hs):", min_value=limite_inferior + 1, value=5000, step=100)

tecnica_reduccion = st.selectbox(
    "Técnica de reducción de varianza:",
    ["Ninguna", "Variables Antitéticas", "Muestreo Estratificado (LHS)"]
)


# ===== BOTÓN =====
if st.button("Ejecutar Simulación"):

    st.subheader("Resultados de la Simulación:")

    simulacion = Montecarlo(
        num_variables=paneles,
        n_experimentos=n,
        criterio_sorteo=panel_para_fallar,
        limite_inferior=limite_inferior,
        limite_superior=limite_superior,
        tecnica_reduccion=tecnica_reduccion
    )

    experimentos, resultados, satelite = simulacion.retornar_resultados()

    # Ordenamos experimentos para coincidir con ejemplo
    for idx, exp in enumerate(experimentos):
        exp.sort()
        if simulacion.tecnica_reduccion == "variables antitéticas":
            exp.append(satelite[idx // 2])
        else:
            exp.append(satelite[idx])

    df = pd.DataFrame(
        experimentos,
        columns=[f"Panel {i+1}" for i in range(paneles)] + ["Satelite (xi)"]
    )
    df.index += 1

    st.table(df)

    # Métricas finales
    st.write(f"**Promedio del tiempo de falla:** {resultados[1]} hs")
    st.write(f"**Desviación estándar muestral:** {resultados[2]} hs")
    st.write(f"**Error estándar:** {resultados[3]} hs")

