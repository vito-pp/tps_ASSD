

# File: main.py
"""
Example usage: load audio, configure GA, run optimization.
"""
import soundfile as sf
import numpy as np
from ga import GeneticAlgorithm

# Load input and desired signals
x, sr1 = sf.read('input.wav')
d, sr2 = sf.read('desired.wav')
assert sr1 == sr2, "Sampling rates must match!"

# take only left channel (or average both if you prefer)
if x.ndim > 1:
    x = x[:,0]
if d.ndim > 1:
    d = d[:,0]

# GA settings
bounds = [(-3.0, 3.0), (-3.0, 3.0)]  # Example: initial weights range
m = 8
pop_size = 20
generations = 5
K = 1.0
mu = 0.1
mutation_rate = 1/1000

# Run GA
ga = GeneticAlgorithm(bounds, m, pop_size, K, mu, mutation_rate)
best_ind = ga.run(x, d, generations)
best_params = best_ind.decode()
print("Optimized parameters:", best_params)

# (Optional) Save best output
from lms_filter import apply_lms_filter
y, e = apply_lms_filter(x, d, best_params, mu)
sf.write('filtered.wav', y, sr1)