#!/usr/bin/env python3
"""
SGA-driven LMS noise-cancelling system 
implementation.
"""
import random
import numpy as np
import soundfile as sf

class Individual:
    def __init__(self, bitstring, P, m):
        # bitstring: list of 0/1
        # m: number of bits per parameter
        self.bitstring = bitstring
        self.m = m
        self.P = P
        self.fitness = 0

    # Metodo de decodificacion de los pesos del algoritmo
    def decode(self):
        params = []
        for i in range(self.P):
            start = i * self.m
            segment = self.bitstring[start:start + self.m]
            # Convertir segmento a entero sin signo
            I = int(''.join(str(b) for b in segment), 2)
            # Escalar a punto flotante en [-1, 1]
            val = -1 + 2 * (I / (2**self.m - 1))
            params.append(val)
        return params

    # Metodo estatico para la generacion de individuos aleatorios
    @staticmethod
    def random(P, m):
        bitstring = [random.choice([0, 1]) for _ in range(P * m)]
        return Individual(bitstring, P, m)


# --- LMS filter implementation ---
def apply_lms_filter(x, d, weights):
    # The last parameter is mu
    mu = weights[-1]
    # Restrict mu to [0, 0.1] for stability
    mu = max(0, min(mu, 0.1))
    fir_weights = weights[:-1]
    P = len(fir_weights)
    w = np.array(fir_weights, dtype=np.float64)
    N = x.shape[0]
    y = np.zeros(N, dtype=np.float64)
    e = np.zeros(N, dtype=np.float64)
    buf = np.zeros(P, dtype=np.float64)
    for n in range(N):
        buf[1:] = buf[:-1]
        buf[0] = x[n]
        y[n] = np.dot(buf, w)
        e[n] = d[n] - y[n]
        # Adaptive LMS update
        w = w + mu * e[n] * buf
    return y, e

# --- Fitness computation ---
def compute_fitness(error, epsilon=1e-12):
    mse = np.mean(error ** 2)
    return 1 / (mse + epsilon)

# --- Genetic Algorithm core ---
class GeneticAlgorithm:
    def __init__(self, P, m, pop_size, mutation_rate):
        self.P = P
        self.m = m
        self.pop_size = pop_size
        self.mutation_rate = mutation_rate
        self.population = [Individual.random(P, m) for _ in range(pop_size)]
        self.new_population = [Individual.random(P, m) for _ in range(pop_size)]
        self.fitnesses = np.zeros(pop_size)

    # Modifica el fitness de toda la poblacion
    # Fucionamiento correcto
    def evaluate(self, x, d):
        for ind in self.population:
            params = ind.decode()
            weights_mu = params
            _, e = apply_lms_filter(x, d, weights_mu)
            ind.fitness = compute_fitness(e)

    # Funcionamiento correcto
    # Funcion de Seleccion ponderada de padres
    def select_parents(self):
        probs = self.fitnesses / self.fitnesses.sum()
        idx = np.random.choice(self.pop_size, size=2, p=probs)
        return self.population[idx[0]], self.population[idx[1]]

    # Funcionamiento Correcto parece
    def crossover(self, p1, p2):
        n = len(p1.bitstring)
        pt = random.randint(1, n - 1)
        b1 = p1.bitstring[:pt] + p2.bitstring[pt:]
        b2 = p2.bitstring[:pt] + p1.bitstring[pt:]
        return Individual(b1, self.P, self.m), Individual(b2, self.P, self.m)

    # Okey
    def mutate(self, ind):
        for i in range(len(ind.bitstring)):
            if random.random() < self.mutation_rate:
                ind.bitstring[i] ^= 1


    def run(self, x, d, generations):
        for gen in range(1, generations + 1):
            # Generacion de Fitness en la poblacion inicial
            self.evaluate(x, d)
            self.fitnesses = np.array([ind.fitness for ind in self.population])
            self.new_population = [None] * self.pop_size
            i = 0
            while i < self.pop_size:
                p1, p2 = self.select_parents()
                c1, c2 = self.crossover(p1, p2)
                self.mutate(c1)
                self.mutate(c2)
                self.new_population[i] = c1
                if i + 1 < self.pop_size:
                    self.new_population[i + 1] = c2
                i += 2
            self.population = self.new_population[:self.pop_size]
            best_fit = max(self.fitnesses)
            print(f"[GA] Gen {gen}/{generations} — Best fitness: {best_fit:.6f}")

        self.evaluate(x, d)
        best_ind = max(self.population, key=lambda ind: ind.fitness)
        return best_ind

# --- Main entrypoint ---
def main():
    # Load and preprocess audio
    x, sr1 = sf.read('input.wav')
    d, sr2 = sf.read('desired.wav')
    assert sr1 == sr2, 'Sampling rates must match'
    if x.ndim > 1: x = x.mean(axis=1)
    if d.ndim > 1: d = d.mean(axis=1)

    # Optional: short test clip
    # max_samples = int(0.1 * sr1)
    # x, d = x[:max_samples], d[:max_samples]

    m = 8
    P = 10
    pop_size = 40
    generations = 4
    mutation_rate = 1/1000

    print(f"Starting GA: pop={pop_size}, gens={generations}, bits/param={m}, order={P}")
    ga = GeneticAlgorithm(P, m, pop_size, mutation_rate)
    best = ga.run(x, d, generations)

    decoded = best.decode()
    weights_opt = decoded[:-1] 
    mu_opt = decoded[-1]
    print(f"Optimized weights: {weights_opt}")
    print(f"Optimized mu: {mu_opt}")

    # Save filtered output using optimized weights and mu
    y, _ = apply_lms_filter(x, d, decoded)
    sf.write('filtered_bebe.wav', y, sr1)
    print('Filtered audio saved to filtered.wav')

    # Print MSE between filtered output and desired
    mse_d_y = np.mean((d - y) ** 2)
    print(f"MSE between desired and filtered output: {mse_d_y:.6f}")

    # Print MSE between input and filtered output
    mse_x_y = np.mean((x - y) ** 2)
    print(f"MSE between input and filtered output: {mse_x_y:.6f}")

if __name__ == '__main__':
    main()
