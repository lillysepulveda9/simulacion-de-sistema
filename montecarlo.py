#----------------------------------MONTECARLO APP----------------------------------#
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
print(simulacion1.retornar_resultados())
