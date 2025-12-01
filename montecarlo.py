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
    Implementa el algoritmo de Montecarlo para estimar la integral:

        Integral_a^b (2/pi) * f(x) dx

    Es decir:
        I = ∫_a^b (2/π) f(x) dx

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

        # valor intermedio (b-a)/n * sum f(x_i)
        self.estimacion_base = None
        # valor final con 2/pi
        self.estimacion = None

    # ---------------------- definición de f(x) ---------------------- #
    def _f(self, x: float) -> float:
        """ Devuelve f(x) según la opción elegida. """
        den = math.exp(x) + math.exp(-x)
        if den == 0:
            return 0.0

        if self.opcion_funcion == "a":
            return 1.0 / den
        else:
            return 2.0 / den

    # ---------------------- algoritmo de Montecarlo ---------------------- #
    def run(self):
        """
        1) x_i ~ U(a,b)
        2) f_i = f(x_i)
        3) Calcular (b-a)/n * sum f(x_i)
        4) Multiplicar por 2/pi para estimar la integral pedida
        """

        if self.n <= 0:
            raise ValueError("El tamaño de muestra n debe ser mayor que 0.")
        if self.a >= self.b:
            raise ValueError("Debe cumplirse a < b.")

        xs = []
        fs = []
        areas = []

        # factor (b-a)/n
        factor = (self.b - self.a) / float(self.n)

        for _ in range(self.n):
            xi = random.uniform(self.a, self.b)
            fxi = self._f(xi)

            # Área_i = ((b-a)/n) * f(x_i)
            area_i = factor * fxi

            xs.append(xi)
            fs.append(fxi)
            areas.append(area_i)

        # Paso 3: (b-a)/n * sum f(x_i)
        suma_f = sum(fs)
        estimacion_base = factor * suma_f

        # Paso 4: integral con factor 2/pi
        estimacion_final = (2 / math.pi) * estimacion_base

        self.muestra_x = xs
        self.alturas = fs
        self.areas = areas
        self.estimacion_base = estimacion_base
        self.estimacion = estimacion_final

        df_resultados = pd.DataFrame(
            {
                "x_i": xs,
                "f(x_i)": fs,
                "Área_i = ((b-a)/n)·f(x_i)": areas,
            }
        )

        # devuelve ambas estimaciones
        return self.estimacion, self.estimacion_base, df_resultados


# ==========================================================================
# ================================ STREAMLIT UI ============================
# ==========================================================================

st.title("Estimación de Integrales por el Método de Montecarlo")

# === DESCRIPCIÓN CON TEXTO + LATEX CORRECTO === #
st.markdown("Este programa estima la siguiente integral:")

st.latex(r"\int_{-6}^{6} \frac{2}{\pi} f(x)\,dx")

st.markdown("donde puedes elegir entre las siguientes funciones del examen:")

st.markdown("- **Opción (a):**")
st.latex(r"f(x) = \frac{1}{e^x + e^{-x}}")

st.markdown("- **Opción (b):**")
st.latex(r"f(x) = \frac{2}{e^x + e^{-x}}")

st.header("Parámetros de entrada")

col_izq, col_der = st.columns([2, 3])

with col_izq:

    opcion_funcion = st.radio(
        "Selecciona la función f(x):",
        options=["a", "b"],
        index=0,
    )

    # Intervalo fijo [-6, 6], sin opción de cambiarlo
    a = -6.0
    b = 6.0
    st.markdown("**Intervalo de integración fijo:**")
    st.latex(r"[a,b] = [-6,6]")

    n = st.number_input(
        "Tamaño de la muestra (n réplicas)",
        min_value=1,
        max_value=500000,
        value=10,        # ya no 1000 "hardcodeado"
        step=1,
        help="Número de réplicas n para x_i ~ U(-6,6).",
    )

    col_b1, col_b2 = st.columns(2)
    ejecutar = col_b1.button("▶ Ejecutar Montecarlo")
    limpiar = col_b2.button("Limpiar resultados")

if limpiar:
    if "mc_resultados" in st.session_state:
        del st.session_state["mc_resultados"]


# ----------------------- EJECUCIÓN ---------------------------- #

if ejecutar:
    try:
        modelo = MonteCarloIntegral(a=a, b=b, n=int(n), opcion_funcion=opcion_funcion)
        estimacion, estimacion_base, df_resultados = modelo.run()

        st.session_state["mc_resultados"] = {
            "estimacion": estimacion,              # con 2/pi
            "estimacion_base": estimacion_base,    # (b-a)/n * sum f(x_i)
            "df": df_resultados,
            "a": a,
            "b": b,
            "n": int(n),
            "opcion_funcion": opcion_funcion,
        }

    except Exception as e:
        st.error(f"⚠ Error en la simulación: {e}")


# ----------------------- RESULTADOS --------------------------- #

if "mc_resultados" in st.session_state:
    res = st.session_state["mc_resultados"]

    with col_der:
        st.subheader("Resultados")

        funcion_texto = (
            r"f(x)=\frac{1}{e^x + e^{-x}}" if res["opcion_funcion"] == "a"
            else r"f(x)=\frac{2}{e^x + e^{-x}}"
        )

        st.markdown("**Función usada:**")
        st.latex(funcion_texto)

        st.markdown(
            f"""
**Intervalo:** [{res['a']}, {res['b']}]  
**Tamaño de muestra:** n = {res['n']}
"""
        )

        # Accesos seguros con .get() para evitar KeyError si hay estado viejo
        estim_base = res.get("estimacion_base", None)
        estim_final = res.get("estimacion", None)

        if estim_base is not None:
            st.markdown("**Cálculo intermedio:**")
            st.latex(
                r"\frac{b-a}{n}\sum_{i=1}^n f(x_i) \approx "
                + f"{estim_base:.6f}"
            )

        if estim_final is not None:
            st.markdown("**Estimación de la integral:**")
            st.latex(
                r"\hat{I} = \frac{2}{\pi}\cdot\frac{b-a}{n}\sum_{i=1}^n f(x_i) \approx "
                + f"{estim_final:.6f}"
            )

    st.markdown("---")
    st.subheader("Muestras, alturas y áreas")

    st.dataframe(res["df"], use_container_width=True)

    # Botón de descarga
    csv = res["df"].to_csv(index=False).encode("utf-8")
    st.download_button(
        label="⬇ Descargar CSV",
        data=csv,
        file_name="MonteCarlo_Resultados.csv",
        mime="text/csv",
    )
