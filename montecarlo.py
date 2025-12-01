#---------------------------------- STREAMLIT APP ----------------------------------#
import streamlit as st
import pandas as pd
import random
import math
import os

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
# ===================== CLASE JOB SHOP / GREEDY ECT ========================
# ==========================================================================


class JobShopGreedyECT:
    """
    Simula un sistema Job-Shop donde cada trabajo consta de 'elementos_por_trabajo'
    elementos.

    MODO "Greedy ECT":
        Cada elemento se asigna a la máquina donde TERMINA antes.

    MODO "FIFO aleatorio":
        Cada elemento se asigna a una máquina aleatoria.
    """

    def __init__(
        self,
        num_jobs: int,
        num_machines: int,
        elementos_por_trabajo: int,
        rate_mode: str = "Aleatorio",
        rate_min: float = 1.0,
        rate_max: float = 5.0,
        rate_df: pd.DataFrame | None = None,
        sequencing_mode: str = "Greedy ECT",
    ):
        self.num_jobs = num_jobs
        self.num_machines = num_machines
        self.elementos_por_trabajo = elementos_por_trabajo
        self.rate_mode = rate_mode
        self.rate_min = rate_min
        self.rate_max = rate_max
        self.rate_df = rate_df
        self.sequencing_mode = sequencing_mode

        self.rates = None
        self.makespan = None
        self.traza = None

    # ---------------------- generación de rates ---------------------- #
    def _generar_matriz_rates(self) -> pd.DataFrame:
        if self.rate_mode.lower().startswith("manual") and self.rate_df is not None:
            sub = self.rate_df.iloc[: self.num_jobs, : self.num_machines].copy()
            sub = sub.apply(pd.to_numeric, errors="coerce").fillna(1.0)
            return sub

        elif self.rate_mode.lower().startswith("mixto") and self.rate_df is not None:
            sub = self.rate_df.iloc[: self.num_jobs, : self.num_machines].copy()
            sub = sub.apply(pd.to_numeric, errors="coerce")
            for i in range(self.num_jobs):
                for k in range(self.num_machines):
                    if pd.isna(sub.iat[i, k]) or sub.iat[i, k] <= 0:
                        sub.iat[i, k] = random.uniform(self.rate_min, self.rate_max)
            return sub

        else:
            data = [
                [random.uniform(self.rate_min, self.rate_max) for _ in range(self.num_machines)]
                for _ in range(self.num_jobs)
            ]
            cols = [f"M{k+1}" for k in range(self.num_machines)]
            idx = [f"J{j+1}" for j in range(self.num_jobs)]
            return pd.DataFrame(data, index=idx, columns=cols)

    # ---------------------- simulación job-shop ---------------------- #
    def run(self):
        rates = self._generar_matriz_rates()
        carga_maquinas = [0.0 for _ in range(self.num_machines)]
        registros = []
        orden_global = 1

        for j in range(self.num_jobs):
            for e in range(self.elementos_por_trabajo):

                tiempos_fin = []
                tiempos_proc = []
                for m in range(self.num_machines):
                    r = rates.iat[j, m]
                    proc_time = float("inf") if r <= 0 else 1.0 / r
                    tiempos_proc.append(proc_time)
                    tiempos_fin.append(carga_maquinas[m] + proc_time)

                if self.sequencing_mode == "Greedy ECT":
                    mejor_maquina = min(range(self.num_machines), key=lambda mm: tiempos_fin[mm])
                else:
                    mejor_maquina = random.randint(0, self.num_machines - 1)

                inicio = carga_maquinas[mejor_maquina]
                fin = inicio + tiempos_proc[mejor_maquina]
                carga_maquinas[mejor_maquina] = fin

                registros.append(
                    {
                        "Maquina": mejor_maquina + 1,
                        "idTrabajo": j + 1,
                        "idElemento": e + 1,
                        "HoraInicio": round(inicio, 3),
                        "HoraFin": round(fin, 3),
                        "OrdenSecuenciacion": orden_global,
                    }
                )
                orden_global += 1

        makespan = max(carga_maquinas)
        self.makespan = makespan
        self.traza = pd.DataFrame(registros)
        self.rates = rates
        return makespan, self.traza, rates


# ==========================================================================
# ============================= FUNCIONES AUX ==============================
# ==========================================================================


def correr_experimentos(
    n_simulaciones: int,
    usar_aleatorio: bool,
    trabajos_manual: int,
    maquinas_manual: int,
    elementos_fijo: int,
    rate_mode: str,
    rate_df: pd.DataFrame,
    carpeta_salida: str,
    sequencing_mode: str,
):

    os.makedirs(carpeta_salida, exist_ok=True)

    makespans = []
    descripciones = []

    for s in range(1, n_simulaciones + 1):

        # --- valores aleatorios o fijos ---
        if usar_aleatorio:
            n_jobs = random.randint(20, 30)
            n_machines = random.randint(3, 5)
            elementos = random.choice([5, 10, 15])
        else:
            n_jobs = trabajos_manual
            n_machines = maquinas_manual
            elementos = elementos_fijo

        simulador = JobShopGreedyECT(
            num_jobs=n_jobs,
            num_machines=n_machines,
            elementos_por_trabajo=elementos,
            rate_mode=rate_mode,
            rate_min=1.0,
            rate_max=5.0,
            rate_df=rate_df,
            sequencing_mode=sequencing_mode,
        )

        mk, traza, _ = simulador.run()
        makespans.append(mk)

        # guardar CSV
        ruta = os.path.join(carpeta_salida, f"Sim_{s:02d}.csv")
        traza.to_csv(ruta, index=False)

        if rate_mode.lower().startswith("manual"):
            desc_rate = "Manual (matriz usuario)"
        elif rate_mode.lower().startswith("mixto"):
            desc_rate = "Mixto (manual + aleatorio)"
        else:
            desc_rate = "Aleatorio"

        descripciones.append(
            f"Sim {s:02d} | Trabajos={n_jobs}, Máquinas={n_machines}, Elem={elementos}, "
            f"{desc_rate}, Regla={sequencing_mode} → Makespan={mk:.3f} h"
        )

    return makespans, descripciones


# ==========================================================================
# ================================ STREAMLIT UI ============================
# ==========================================================================

st.title("Simulación Job-Shop con Greedy ECT y FIFO aleatorio")

st.header("Parámetros")

if "n_trabajos" not in st.session_state:
    st.session_state["n_trabajos"] = 26
if "n_maquinas" not in st.session_state:
    st.session_state["n_maquinas"] = 5
if "n_elementos" not in st.session_state:
    st.session_state["n_elementos"] = 5

MAX_TRABAJOS = 30
MAX_MAQUINAS = 5
if "rate_df" not in st.session_state:
    columnas = [f"M{k+1}" for k in range(MAX_MAQUINAS)]
    index = [f"J{j+1}" for j in range(MAX_TRABAJOS)]
    st.session_state["rate_df"] = pd.DataFrame(1.0, index=index, columns=columnas)

col_param, col_resultados = st.columns([2, 3])

with col_param:

    usar_aleatorio = st.checkbox("Usar aleatorio (trabajos, máquinas y elementos)")

    if st.button("Randomizar ahora"):
        st.session_state["n_trabajos"] = random.randint(20, 30)
        st.session_state["n_maquinas"] = random.randint(3, 5)
        st.session_state["n_elementos"] = random.choice([5, 10, 15])

    n_trabajos = st.number_input(
        "N° Trabajos (20–30)", min_value=20, max_value=30, key="n_trabajos"
    )

    # --- Elementos por trabajo con protección ---
    opciones_elem = [5, 10, 15]
    valor_actual = st.session_state.get("n_elementos", 5)
    if valor_actual not in opciones_elem:
        valor_actual = 5

    elementos_por_trabajo = st.selectbox(
        "Elementos por trabajo (fijo)",
        options=opciones_elem,
        index=opciones_elem.index(valor_actual),
    )
    st.session_state["n_elementos"] = elementos_por_trabajo

    n_maquinas = st.number_input(
        "N° Máquinas (3–5)", min_value=3, max_value=5, key="n_maquinas"
    )

    rate_mode = st.selectbox(
        "Rates (u/hr)", ["Aleatorio", "Manual", "Mixto (manual + aleatorio)"]
    )

    modo_seq = st.selectbox(
        "Modo de secuenciación",
        ["Greedy ECT", "FIFO aleatorio"],
    )

    col_b1, col_b2 = st.columns(2)
    ejecutar = col_b1.button("▶ Correr 20 simulaciones")
    limpiar = col_b2.button("Limpiar")

st.subheader("Matriz de rates (Trabajo × Máquina)")
rate_df_editada = st.data_editor(
    st.session_state["rate_df"], key="editor_rates", use_container_width=True
)
st.session_state["rate_df"] = rate_df_editada

CARPETA_SALIDA = os.path.join(os.getcwd(), "ExamenSims")

if limpiar:
    if "resultados_sim" in st.session_state:
        del st.session_state["resultados_sim"]

if ejecutar:
    makespans, descripciones = correr_experimentos(
        n_simulaciones=20,
        usar_aleatorio=usar_aleatorio,
        trabajos_manual=int(n_trabajos),
        maquinas_manual=int(n_maquinas),
        elementos_fijo=int(elementos_por_trabajo),
        rate_mode=rate_mode,
        rate_df=st.session_state["rate_df"],
        carpeta_salida=CARPETA_SALIDA,
        sequencing_mode=modo_seq,
    )

    prom = sum(makespans) / len(makespans)
    mn = min(makespans)
    mx = max(makespans)

    st.session_state["resultados_sim"] = {
        "makespans": makespans,
        "descripciones": descripciones,
        "promedio": prom,
        "min": mn,
        "max": mx,
        "carpeta": CARPETA_SALIDA,
    }

if "resultados_sim" in st.session_state:
    res = st.session_state["resultados_sim"]

    with col_resultados:
        st.subheader("Resultados por simulación")
        for linea in res["descripciones"]:
            st.write(linea)

    st.write("---")
    st.write(
        f"**Makespan promedio:** {res['promedio']:.3f} h  \n"
        f"**Min:** {res['min']:.3f} h | **Max:** {res['max']:.3f} h"
    )
    st.write(f"CSVs guardados en: `{res['carpeta']}`")
