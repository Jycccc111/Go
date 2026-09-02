import numpy as np

file = "dataset/chunk_00197.npz"

data = np.load(file)

states = data["states"]
moves = data["moves"]
results = data["results"]

print("states:", states.shape)
print("moves:", moves.shape)
print("results:", results.shape)

print()
print("第一步 action:", moves[0])
print("第一步 result:", results[0])

print()
print("第一步 state:")
print(states[0])