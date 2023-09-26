import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from PIL import Image


# Function to load and preprocess image data
def load_and_preprocess_image(image_path):
    img = Image.open(image_path)
    img = img.convert('RGB')
    img = img.resize((224, 224))  # Resize to a fixed size
    img = np.array(img) / 255.0  # Normalize pixel values to [0, 1]
    return img


# Function to create the dataset
def create_dataset(image_paths, radius):
    inputs = []
    targets = []

    for image_path in image_paths:
        img = load_and_preprocess_image(image_path)
        h, w, _ = img.shape

        for i in range(radius, h - radius):
            for j in range(radius, w - radius):
                # Extract the surrounding pixels in a radius 'r'
                patch = img[i - radius : i + radius + 1, j - radius : j + radius + 1]
                inputs.append(patch)
                # Assuming the target color value is the center pixel's color
                target_color = img[i, j]
                targets.append(target_color)

    return np.array(inputs), np.array(targets)


# Define the CNN model
def create_model(input_shape):
    model = keras.Sequential([
        layers.Input(shape=input_shape),
        layers.Conv2D(32, (3, 3), activation='relu', padding='same'),
        layers.MaxPooling2D((2, 2)),
        layers.Flatten(),
        layers.Dense(64, activation='relu'),
        layers.Dense(3)  # Output layer with 3 channels (RGB)
    ])
    return model


def train_model(image_paths, radius):
    inputs, targets = create_dataset(image_paths, radius)

    # Create and compile the model
    model = create_model((2 * radius + 1, 2 * radius + 1, 3))
    model.compile(optimizer='adam', loss='mse')  # Use Mean Squared Error as the loss

    # Train the model
    model.fit(inputs, targets, epochs=10, batch_size=32)  # Adjust epochs and batch size as needed

    return model


def apply_model(model_filename):
    # Set image dimensions and number of iterations
    image_width = 64
    image_height = 64
    num_iterations = 2

    # Create the initial random noise image
    initial_image = create_random_noise_image(image_width, image_height)

    # Create and compile the CNN model (replace with your trained model)
    model = tf.keras.models.load_model(model_filename)
    model.compile(optimizer="adam", loss="mse")  # Use appropriate optimizer and loss

    # Perform iterative processing using the model
    final_image = iterate_with_model(initial_image, model, num_iterations)

    # Save the final image
    final_image = (final_image * 255).astype(np.uint8)  # Convert to 8-bit integer values
    final_image = Image.fromarray(final_image)
    final_image.save("final_image.png")


# Function to create a random noise image
def create_random_noise_image(width, height):
    return np.random.rand(height, width, 3)


# Function to apply the CNN model to a patch of pixels
def apply_model_to_patch(patch, model):
    # Reshape the patch to match the model's input shape
    patch = patch.reshape((1, patch.shape[0], patch.shape[1], 3))
    # Predict the color for the center pixel of the patch
    predicted_color = model.predict(patch, verbose=0)
    return predicted_color


# Iterate over the image using the model
def iterate_with_model(input_image, model, iterations):
    current_image = input_image.copy()
    h, w, _ = current_image.shape

    patch_radius = model.input_shape[1] // 2

    for _ in range(iterations):
        print('-' * 80)
        new_image = current_image.copy()
        for i in range(patch_radius, h - patch_radius):
            for j in range(patch_radius, w - patch_radius):
                # Extract a patch centered around (i, j)
                patch = current_image[
                    (i - patch_radius):(i + patch_radius + 1),
                    (j - patch_radius):(j + patch_radius + 1),
                ]
                # Apply the model to the patch
                predicted_color = apply_model_to_patch(patch, model)
                # Update the corresponding pixel in the new image
                new_image[i, j] = predicted_color
        current_image = new_image

    return current_image


def main():
    image_paths = ['Assets/Sprites/Terrain/originals/cobble-colored.png']
    radius = 5  # Adjust the radius as needed
    model = train_model(image_paths, radius)
    model.save('Assets/Sprites/Terrain/originals/cobble-colored.5.keras')


if __name__ == '__main__':
    # main()
    apply_model('Assets/Sprites/Terrain/originals/cobble-colored.5.keras')
    