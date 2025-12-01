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
    elementos. Cada elemento se asigna, uno por uno, a la máquina donde TERMINA antes,
    considerando el tiempo ya comprometido (heurística Greedy ECT).

    - num_jobs: número de trabajos J
    - num_machines: número de máquinas M
    - elementos_por_trabajo: elementos u operaciones por trabajo
    - rate_mode: 'Aleatorio', 'Manual' o 'Mixto'
    - rate_min, rate_max: límites de muestreo para rates aleatorios (u/hr)
    - rate_df: matriz de rates (Trabajo x Máquina) definida por usuario (pandas.DataFrame)
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
    ):
        self.num_jobs = num_jobs
        self.num_machines = num_machines
        self.elementos_por_trabajo = elementos_por_trabajo
        self.rate_mode = rate_mode
        self.rate_min = rate_min
        self.rate_max = rate_max
        self.rate_df = rate_df

        # Estos se llenan en run()
        self.rates = None
        self.makespan = None
        self.traza = None

    # ---------------------- generación de rates ---------------------- #
    def _generar_matriz_rates(self) -> pd.DataFrame:
        """
        Devuelve una matriz de tamaño (num_jobs x num_machines) con rates(i,j)
        en unidades u/hr.
        """
        if self.rate_mode.lower().startswith("manual") and self.rate_df is not None:
            # Usar únicamente las primeras filas/columnas según el tamaño actual
            sub = self.rate_df.iloc[: self.num_jobs, : self.num_machines].copy()
            # Reemplaza celdas vacías o no numéricas con un valor por defecto (por ejemplo 1.0)
            sub = sub.apply(pd.to_numeric, errors="coerce").fillna(1.0)
            return sub

        elif self.rate_mode.lower().startswith("mixto") and self.rate_df is not None:
            # Toma matriz manual y completa con aleatorios donde falte
            sub = self.rate_df.iloc[: self.num_jobs, : self.num_machines].copy()
            sub = sub.apply(pd.to_numeric, errors="coerce")
            for i in range(self.num_jobs):
                for k in range(self.num_machines):
                    if pd.isna(sub.iat[i, k]) or sub.iat[i, k] <= 0:
                        sub.iat[i, k] = random.uniform(self.rate_min, self.rate_max)
            return sub

        else:
            # Totalmente aleatoria
            data = [
                [
                    random.uniform(self.rate_min, self.rate_max)
                    for _ in range(self.num_machines)
                ]
                for _ in range(self.num_jobs)
            ]
            cols = [f"M{k+1}" for k in range(self.num_machines)]
            idx = [f"J{j+1}" for j in range(self.num_jobs)]
            return pd.DataFrame(data, index=idx, columns=cols)

    # ---------------------- simulación greedy ECT -------------------- #
    def run(self):
        """
        Ejecuta la secuenciación Greedy ECT y devuelve:
        - makespan (float, en horas)
        - df_traza (DataFrame con la traza completa)
        - rates (DataFrame con la matriz de rates usada)
        """
        rates = self._generar_matriz_rates()

        # Carga acumulada (horas) en cada máquina
        carga_maquinas = [0.0 for _ in range(self.num_machines)]

        registros = []
        orden_global = 1

        # Recorremos trabajos y elementos
        for j in range(self.num_jobs):
            for e in range(self.elementos_por_trabajo):
                tiempos_fin = []

                for m in range(self.num_machines):
                    # Tiempo de proceso de un solo elemento:
                    rate_ij = rates.iat[j, m]  # u/hr
                    if rate_ij <= 0:
                        proc_time = float("inf")
                    else:
                        proc_time = 1.0 / rate_ij  # horas por elemento

                    fin_m = carga_maquinas[m] + proc_time
                    tiempos_fin.append(fin_m)

                # Elegimos la máquina con menor tiempo de terminación
                mejor_maquina = min(range(self.num_machines), key=lambda mm: tiempos_fin[mm])

                inicio = carga_maquinas[mejor_maquina]
                fin = tiempos_fin[mejor_maquina]
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

        makespan = max(carga_maquinas) if carga_maquinas else 0.0

        self.rates = rates
        self.makespan = makespan
        self.traza = pd.DataFrame(registros)

        return makespan, self.traza, rates


# ==========================================================================
# ============================= FUNCIONES AUX ==============================
# ==========================================================================


def correr_experimentos(
    n_simulaciones: int,
    usar_aleatorio: bool,
    trabajos_manual: int,
    maquinas_manual: int,
    elementos_por_trabajo: int,
    rate_mode: str,
    rate_df: pd.DataFrame,
    carpeta_salida: str,
):
    """
    Corre S simulaciones independientes y devuelve:
    - lista_makespans
    - lista_descripciones (líneas tipo 'Sim 01 | Trabajos=..., Máquinas=..., Elem=..., ...')
    """
    os.makedirs(carpeta_salida, exist_ok=True)

    makespans = []
    descripciones = []

    N_TRAB_MIN, N_TRAB_MAX = 20, 30
    N_MAQ_MIN, N_MAQ_MAX = 3, 5

    for s in range(1, n_simulaciones + 1):
        if usar_aleatorio:
            n_jobs = random.randint(N_TRAB_MIN, N_TRAB_MAX)
            n_machines = random.randint(N_MAQ_MIN, N_MAQ_MAX)
        else:
            n_jobs = trabajos_manual
            n_machines = maquinas_manual

        simulador = JobShopGreedyECT(
            num_jobs=n_jobs,
            num_machines=n_machines,
            elementos_por_trabajo=elementos_por_trabajo,
            rate_mode=rate_mode,
            rate_min=1.0,
            rate_max=5.0,
            rate_df=rate_df,
        )

        mk, df_traza, rates = simulador.run()
        makespans.append(mk)

        # Guarda CSV con la traza
        nombre = f"Sim_{s:02d}.csv"
        ruta_csv = os.path.join(carpeta_salida, nombre)
        df_traza.to_csv(ruta_csv, index=False)

        # Descripción del tipo de rates
        if rate_mode.lower().startswith("manual"):
            desc_mode = "Manual (matriz usuario)"
        elif rate_mode.lower().startswith("mixto"):
            desc_mode = "Aleatorio (matriz mixta)"
        else:
            desc_mode = "Aleatorio (matriz generada)"

        descripciones.append(
            f"Sim {s:02d} | Trabajos={n_jobs}, Máquinas={n_machines}, "
            f"Elem={elementos_por_trabajo}, {desc_mode} → Makespan={mk:.3f} h"
        )

    return makespans, descripciones


# ==========================================================================
# ================================ STREAMLIT UI ============================
# ==========================================================================

st.title(
    "Genera 20 simulaciones; heurística Greedy ECT "
    "(asigna cada elemento a la máquina donde TERMINA antes)"
)

st.header("Parámetros")

# ----------- Inicialización de session_state para los controles ---------- #
if "n_trabajos" not in st.session_state:
    st.session_state["n_trabajos"] = 26
if "n_maquinas" not in st.session_state:
    st.session_state["n_maquinas"] = 5
if "n_elementos" not in st.session_state:
    st.session_state["n_elementos"] = 10  # puede ser 10, 20, 30

# Matriz de rates máxima (30 trabajos x 5 máquinas)
MAX_TRABAJOS = 30
MAX_MAQUINAS = 5
if "rate_df" not in st.session_state:
    columnas = [f"M{k+1}" for k in range(MAX_MAQUINAS)]
    index = [f"J{j+1}" for j in range(MAX_TRABAJOS)]
    # Valor por defecto 1.0 u/hr
    st.session_state["rate_df"] = pd.DataFrame(1.0, index=index, columns=columnas)

col_param, col_resultados = st.columns([2, 3])

with col_param:
    usar_aleatorio = st.checkbox("Usar aleatorio (uniforme en rangos)")

    # Botón para randomizar ahora los parámetros dentro de los rangos
    if st.button("Randomizar ahora"):
        st.session_state["n_trabajos"] = random.randint(20, 30)
        st.session_state["n_maquinas"] = random.randint(3, 5)
        st.session_state["n_elementos"] = random.choice([10, 20, 30])

    n_trabajos = st.number_input(
        "N° Trabajos (20–30)",
        min_value=20,
        max_value=30,
        step=1,
        key="n_trabajos",
    )

    elementos_por_trabajo = st.selectbox(
        "Elementos por trabajo",
        options=[10, 20, 30],
        index=[10, 20, 30].index(st.session_state["n_elementos"]),
    )
    st.session_state["n_elementos"] = elementos_por_trabajo

    n_maquinas = st.number_input(
        "N° Máquinas (3–5)",
        min_value=3,
        max_value=5,
        step=1,
        key="n_maquinas",
    )

    rate_mode = st.selectbox(
        "Rates (u/hr)",
        ["Aleatorio", "Manual", "Mixto (manual + aleatorio)"],
    )

    _modo_seq = st.selectbox(
        "Modo de secuenciación",
        ["Greedy ECT"],
        index=0,
        disabled=True,
        help="Se utiliza la heurística Greedy ECT (Earliest Completion Time).",
    )

    st.markdown(
        "*En modo manual se usan los valores de la tabla de rates "
        "(el combo de modo de secuenciación no aplica).*"
    )

    col_b1, col_b2 = st.columns(2)
    ejecutar = col_b1.button("▶ Correr 20 simulaciones")
    limpiar = col_b2.button("Limpiar")

# --------------------- MATRIZ DE RATES (EDITABLE) ------------------------ #
st.subheader("Matriz de rates (Trabajo × Máquina)")
st.caption("Edita M1..M5; el simulador usa solo las primeras N máquinas.")
rate_df_editada = st.data_editor(
    st.session_state["rate_df"],
    key="editor_rates",
    use_container_width=True,
)
st.session_state["rate_df"] = rate_df_editada

# -------------------- LÓGICA DE EJECUCIÓN / LIMPIEZA --------------------- #
CARPETA_SALIDA = os.path.join(os.getcwd(), "ExamenSims")

if limpiar:
    if "resultados_sim" in st.session_state:
        del st.session_state["resultados_sim"]

if ejecutar:
    S = 20
    makespans, descripciones = correr_experimentos(
        n_simulaciones=S,
        usar_aleatorio=usar_aleatorio,
        trabajos_manual=int(n_trabajos),
        maquinas_manual=int(n_maquinas),
        elementos_por_trabajo=int(elementos_por_trabajo),
        rate_mode=rate_mode,
        rate_df=st.session_state["rate_df"],
        carpeta_salida=CARPETA_SALIDA,
    )

    if makespans:
        prom = sum(makespans) / len(makespans)
        mn = min(makespans)
        mx = max(makespans)
    else:
        prom = mn = mx = 0.0

    st.session_state["resultados_sim"] = {
        "makespans": makespans,
        "descripciones": descripciones,
        "promedio": prom,
        "min": mn,
        "max": mx,
        "carpeta": CARPETA_SALIDA,
        "usar_aleatorio": usar_aleatorio,
        "rate_mode": rate_mode,
    }

# -------------------------- MOSTRAR RESULTADOS --------------------------- #
if "resultados_sim" in st.session_state:
    res = st.session_state["resultados_sim"]
    makespans = res["makespans"]
    descripciones = res["descripciones"]

    with col_resultados:
        st.subheader("Resultados por simulación")

        for linea in descripciones:
            st.write(linea)

    st.markdown("---")
    st.write(
        f"**{len(makespans)} simulaciones completadas.**  \n"
        f"**Makespan (horas)** → Prom: {res['promedio']:.3f} | "
        f"Min: {res['min']:.3f} | Máx: {res['max']:.3f}"
    )
    st.write(f"CSVs guardados en: `{res['carpeta']}`")

    st.markdown(
        """
✅ **Simulación terminada.** Revisa los CSVs por simulación.  
🟦 Aleatorio → Trabajos y máquinas se sortearon en los rangos indicados.  
🟧 Modo manual → edita la matriz de rates (M1..M5).  
"""
    )

