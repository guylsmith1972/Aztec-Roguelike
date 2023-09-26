import numpy as np


class SelfOrganizingMap:
    def __init__(self, input_size, n_neurons):
        self.input_size = input_size
        self.n_neurons = n_neurons
        self.weights = np.random.rand(n_neurons, input_size)

    def find_bmu(self, input_vector):
        # Compute the Euclidean distance between input_vector and all neurons
        distances = np.linalg.norm(self.weights - input_vector, axis=1)
        # Find the index of the neuron with the smallest distance (Best Matching Unit)
        bmu_index = np.argmin(distances)
        return bmu_index

    def update_weights(self, input_vector, bmu_index, learning_rate, neighborhood_radius):
        for i in range(self.n_neurons):
            # Compute the influence of the neuron on the BMU based on the neighborhood radius
            distance_squared = np.square(np.linalg.norm([i % int(np.sqrt(self.n_neurons)) - bmu_index % int(np.sqrt(self.n_neurons)),
                                                         i // int(np.sqrt(self.n_neurons)) - bmu_index // int(np.sqrt(self.n_neurons))]))
            influence = np.exp(-distance_squared / (2 * np.square(neighborhood_radius)))
            
            # Update the weights of the neuron
            self.weights[i] += learning_rate * influence * (input_vector - self.weights[i])

    def train(self, data, learning_rate=0.1, epochs=100, initial_neighborhood_radius=None):
        if initial_neighborhood_radius is None:
            initial_neighborhood_radius = max(self.n_neurons // 2, 1)
            
        for epoch in range(epochs):
            for input_vector in data:
                bmu_index = self.find_bmu(input_vector)
                neighborhood_radius = initial_neighborhood_radius * np.exp(-epoch / epochs)
                self.update_weights(input_vector, bmu_index, learning_rate, neighborhood_radius)

    def predict(self, input_vector):
        bmu_index = self.find_bmu(input_vector)
        return self.weights[bmu_index]

