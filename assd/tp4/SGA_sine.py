
import numpy as np
import matplotlib.pyplot as plt
import random

def apply_lms_filter(x, d, weights):
    mu = weights[-1]
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
        w = w + mu * e[n] * buf
    return y, e

def calculate_snr(signal, noise):
    power_signal = np.mean(signal**2)
    power_noise = np.mean(noise**2)
    return 10 * np.log10(power_signal / power_noise)

class Individual:
    def __init__(self, bitstring, P, m):
        self.bitstring = bitstring
        self.m = m
        self.P = P
        self.fitness = 0

    def decode(self):
        params = []
        for i in range(self.P):
            start = i * self.m
            segment = self.bitstring[start:start + self.m]
            I = int(''.join(str(b) for b in segment), 2)
            val = -1 + 2 * (I / (2**self.m - 1))
            params.append(val)
        return params

    @staticmethod
    def random(P, m):
        bitstring = [random.choice([0, 1]) for _ in range(P * m)]
        return Individual(bitstring, P, m)

def compute_fitness(error, epsilon=1e-12):
    mse = np.mean(error ** 2)
    return 1 / (mse + epsilon)

class GeneticAlgorithm:
    def __init__(self, P, m, pop_size, mutation_rate):
        self.P = P
        self.m = m
        self.pop_size = pop_size
        self.mutation_rate = mutation_rate
        self.population = [Individual.random(P, m) for _ in range(pop_size)]
        self.new_population = [Individual.random(P, m) for _ in range(pop_size)]
        self.fitnesses = np.zeros(pop_size)

    def evaluate(self, x, d):
        for ind in self.population:
            params = ind.decode()
            weights_mu = params
            _, e = apply_lms_filter(x, d, weights_mu)
            ind.fitness = compute_fitness(e)

    def select_parents(self):
        probs = self.fitnesses / self.fitnesses.sum()
        idx = np.random.choice(self.pop_size, size=2, p=probs)
        return self.population[idx[0]], self.population[idx[1]]

    def crossover(self, p1, p2):
        n = len(p1.bitstring)
        pt = random.randint(1, n - 1)
        b1 = p1.bitstring[:pt] + p2.bitstring[pt:]
        b2 = p2.bitstring[:pt] + p1.bitstring[pt:]
        return Individual(b1, self.P, self.m), Individual(b2, self.P, self.m)

    def mutate(self, ind):
        for i in range(len(ind.bitstring)):
            if random.random() < self.mutation_rate:
                ind.bitstring[i] ^= 1

    def run(self, x, d, generations):
        best_fitnesses = []
        max_SNR = []
        for gen in range(1, generations + 1):
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
            best_fitnesses.append(best_fit)
            print(f"[GA] Gen {gen}/{generations} — Best fitness: {best_fit:.6f}")
        self.evaluate(x, d)
        best_ind = max(self.population, key=lambda ind: ind.fitness)
        return (best_ind, best_fitnesses)

def run_ga_on_signals(noisy_signal, clean_signal):
    m = 8
    P = 20
    pop_size = 1000
    generations = 200
    mutation_rate = 1/250

    print(f"Starting GA on synthetic signal: pop={pop_size}, gens={generations}, bits/param={m}, order={P}")
    ga = GeneticAlgorithm(P + 1, m, pop_size, mutation_rate)
    best, best_fitnesses = ga.run(noisy_signal, clean_signal, generations)

    # Plot best fitness per generation
    plt.figure()
    plt.plot(best_fitnesses)
    plt.xlabel('Generation')
    plt.ylabel('Best Fitness')
    plt.title('Best Fitness per Generation')
    plt.grid(True)
    plt.show()

    decoded = best.decode()
    weights_opt = decoded[:-1]
    mu_opt = decoded[-1]
    print(f"Optimized weights: {weights_opt}")
    print(f"Optimized μ: {mu_opt}")

    filtered_signal, _ = apply_lms_filter(noisy_signal, clean_signal, decoded)

    noise_before = noisy_signal - clean_signal
    noise_after = filtered_signal - clean_signal
    snr_before = calculate_snr(clean_signal, noise_before)
    snr_after = calculate_snr(clean_signal, noise_after)

    print(f"SNR antes del filtrado: {snr_before:.2f} dB")
    print(f"SNR después del filtrado: {snr_after:.2f} dB")

    t = np.linspace(0, len(clean_signal) / 10, len(clean_signal))
    plt.figure(figsize=(10, 6))
    plt.plot(t, clean_signal, label='Clean Signal')
    plt.plot(t, noisy_signal, label='Noisy Signal', alpha=0.6)
    plt.plot(t, filtered_signal, label='Filtered (GA + LMS)', color='red')
    plt.legend()
    plt.xlabel("Time")
    plt.ylabel("Amplitude")
    plt.title("Signal Comparison (Clean vs Noisy vs Filtered)")
    plt.show()

if __name__ == "__main__":
    np.random.seed(0)
    t = np.linspace(0, 10, 100)
    clean_signal = np.sign(np.sin(t))
    noise = np.random.normal(0, 0.5, t.shape)
    noisy_signal = clean_signal + noise
    run_ga_on_signals(noisy_signal, clean_signal)