#---------------------------------- STREAMLIT APP ----------------------------------#
import streamlit as st
import pandas as pd
import random
import math

# ====== ESTILOS GLOBALES ======
st.markdown(
    """
<style>
h1, h2, h3, h4 {
    color: #0066FF !important;
}
</style>
""",
    unsafe_allow_html=True,
)

# ==========================================================================
# ===================== CLASE MONTECARLO INTEGRAL ==========================
# ==========================================================================

class MonteCarloIntegral:
    """
    Implementa el algoritmo de Montecarlo para estimar una integral:

        Integral_a^b f(x) dx

    con:
        1) x_i ~ U(a, b)
        2) f_i = f(x_i)
        3) Integral ≈ (b - a)/n * sum_{i=1}^n f_i

    Funciones del examen:
        a) f(x) = 1 / (e^x + e^{-x})
        b) f(x) = 2 / (e^x + e^{-x})
    """

    def __init__(self, a: float, b: float, n: int, opcion_funcion: str = "a"):
        self.a = a
        self.b = b
        self.n = n
        self.opcion_funcion = opcion_funcion

        self.muestra_x = None
        self.alturas = None
        self.areas = None
        self.estimacion = None

    # ---------------------- definición de f(x) ---------------------- #
    def _f(self, x: float) -> float:
        """
        Devuelve f(x) según la opción elegida:
            a) f(x) = 1 / (e^x + e^{-x})
            b) f(x) = 2 / (e^x + e^{-x})
        """
        den = math.exp(x) + math.exp(-x)
        if den == 0:
            return 0.0

        if self.opcion_funcion == "a":
            return 1.0 / den
        else:  # "b"
            return 2.0 / den

    # ---------------------- algoritmo de Montecarlo ---------------------- #
    def run(self):
        """
        Ejecuta el algoritmo de Montecarlo:

        1) Genera n valores x_i ~ U(a,b)
        2) Calcula f(x_i) para cada muestra
        3) Calcula áreas individuales: ((b-a)/n) * f(x_i)
        4) Estimación de la integral: suma de las áreas
        """

        if self.n <= 0:
            raise ValueError("El tamaño de la muestra n debe ser mayor que 0.")
        if self.a >= self.b:
            raise ValueError("Se requiere que a < b para el intervalo de integración.")

        xs = []
        fs = []
        areas = []

        factor = (self.b - self.a) / float(self.n)

        for _ in range(self.n):
            xi = random.uniform(self.a, self.b)  # x_i ~ U(a,b)
            fxi = self._f(xi)                    # altura f(x_i)
            area_i = factor * fxi                # área de cada rectángulo

            xs.append(xi)
            fs.append(fxi)
            areas.append(area_i)

        self.muestra_x = xs
        self.alturas = fs
        self.areas = areas
        self.estimacion = sum(areas)

        # Construir DataFrame con parámetros de salida:
        # valores aleatorios generados, alturas y áreas
        df_resultados = pd.DataFrame(
            {
                "x_i (muestra U(a,b))": xs,
                "f(x_i) (altura)": fs,
                "Área_i = (b-a)/n * f(x_i)": areas,
            }
        )

        return self.estimacion, df_resultados

# ==========================================================================
# ================================ STREAMLIT UI ============================
# ==========================================================================

st.title("Estimación de Integrales por el Método de Montecarlo")

st.markdown(
    """
Este programa implementa el algoritmo de Montecarlo para aproximar la integral:

\\[
\\int_a^b f(x)\\,dx
\\]

donde puedes elegir entre las funciones del examen:

- **Opción (a):** \\( f(x) = \\frac{1}{e^x + e^{-x}} \\)
- **Opción (b):** \\( f(x) = \\frac{2}{e^x + e^{-x}} \\)
"""
)

st.header("Parámetros de entrada")

col_izq, col_der = st.columns([2, 3])

with col_izq:

    opcion_funcion = st.radio(
        "Selecciona la función f(x):",
        options=["a", "b"],
        index=0,
        help=(
            "a) f(x) = 1 / (e^x + e^{-x})\n"
            "b) f(x) = 2 / (e^x + e^{-x})"
        ),
    )

    a = st.number_input(
        "Límite inferior (a)",
        value=-6.0,
        help="Ejemplo típico del examen: a = -6. Recuerda que debe cumplirse a < b.",
    )

    b = st.number_input(
        "Límite superior (b)",
        value=6.0,
        help="Ejemplo típico del examen: b = 6. Recuerda que debe cumplirse a < b.",
    )

    n = st.number_input(
        "Tamaño de la muestra (n réplicas)",
        min_value=1,
        max_value=1000000,
        value=1000,
        step=100,
        help="Número de puntos aleatorios generados x_i ~ U(a,b).",
    )

    col_b1, col_b2 = st.columns(2)
    ejecutar = col_b1.button("▶ Ejecutar Montecarlo")
    limpiar = col_b2.button("Limpiar resultados")

if limpiar:
    if "mc_resultados" in st.session_state:
        del st.session_state["mc_resultados"]

# ----------------------- EJECUCIÓN DEL MODELO ---------------------------- #

if ejecutar:
    try:
        modelo = MonteCarloIntegral(a=a, b=b, n=int(n), opcion_funcion=opcion_funcion)
        estimacion, df_resultados = modelo.run()

        st.session_state["mc_resultados"] = {
            "estimacion": estimacion,
            "df": df_resultados,
            "a": a,
            "b": b,
            "n": int(n),
            "opcion_funcion": opcion_funcion,
        }

    except Exception as e:
        st.error(f"Error en la simulación: {e}")

# ----------------------- DESPLIEGUE DE RESULTADOS ------------------------ #

if "mc_resultados" in st.session_state:
    res = st.session_state["mc_resultados"]

    with col_der:
        st.subheader("Parámetros de salida")

        texto_funcion = (
            "f(x) = 1 / (e^x + e^{-x})" if res["opcion_funcion"] == "a"
            else "f(x) = 2 / (e^x + e^{-x})"
        )

        st.markdown(
            f"""
**Función elegida:** {texto_funcion}  
**Intervalo:** [a, b] = [{res['a']}, {res['b']}]  
**Tamaño de muestra:** n = {res['n']}  

**Estimación de la integral (Montecarlo):**  
\\[
\\hat{{I}} \\approx {res["estimacion"]:.6f}
\\]
"""
        )

    st.markdown("---")
    st.subheader("Valores aleatorios, alturas y áreas individuales")

    st.caption(
        "La tabla contiene los valores aleatorios generados x_i, las alturas f(x_i) y "
        "las áreas individuales Área_i = (b-a)/n * f(x_i), cuyo sumatorio es la estimación de la integral."
    )

    st.dataframe(
        res["df"],
        use_container_width=True,
    )

    # Opcional: descarga de resultados a CSV
    csv = res["df"].to_csv(index=False).encode("utf-8")
    st.download_button(
        label="⬇ Descargar resultados en CSV",
        data=csv,
        file_name="MonteCarlo_Integral_Resultados.csv",
        mime="text/csv",
    )
