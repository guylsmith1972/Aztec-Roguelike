import numpy as np
import scipy.signal


def find_before(lst, num):
    i = lst.index(num)
    return lst[i - 1] if i > 0 else lst[0]

def find_after(lst, num):
    i = lst.index(num)
    return lst[i + 1] if i < len(lst) - 1 else lst[-1]

def max_index_with_neighboring_avg(arr, window_size=2):
    # Find the maximum value
    max_val = max(arr)
    
    # Find continuous subsequences of this value
    subsequences = []
    start_index = None
    for i, x in enumerate(arr):
        if x == max_val:
            if start_index is None:
                start_index = i
        else:
            if start_index is not None:
                subsequences.append((start_index, i-1))
                start_index = None
    # Handle case where the last element is also max value
    if start_index is not None:
        subsequences.append((start_index, len(arr)-1))
    
    # If there's only one max value, return its index
    if len(subsequences) == 1 and subsequences[0][1] - subsequences[0][0] == 0:
        return subsequences[0][0]
    
    # Identify the center of the subsequences
    candidates = []
    for start, end in subsequences:
        length = end - start + 1
        if length % 2 == 1:
            candidates.append(start + length // 2)
        else:
            candidates.extend([start + length // 2 - 1, start + length // 2])
    
    # Compute the average of the neighbors for each candidate index
    max_avg = float('-inf')
    best_index = None
    for index in candidates:
        start = max(0, index - window_size)
        end = min(len(arr), index + window_size + 1)
        avg = sum(arr[start:end]) / (end - start)
        if avg > max_avg:
            max_avg = avg
            best_index = index
    
    return best_index


def gaussian_blur(array: np.ndarray, kernel_size: int) -> np.ndarray:
    """Apply Gaussian blur on a 2D numpy array with wrapping left to right and auto sigma calculation."""
    
    def gaussian_kernel(size: int) -> np.ndarray:
        """Generate a Gaussian kernel."""
        sigma = size / 6
        
        # Create an array of indices centered around 0
        x = np.linspace(-(size // 2), size // 2, size)
        
        # Create the 1D Gaussian kernel
        kernel_1D = (1/np.sqrt(2*np.pi*sigma**2)) * np.exp(-x**2/(2*sigma**2))
        
        # Create the 2D Gaussian kernel
        kernel_2D = np.outer(kernel_1D, kernel_1D)
        
        # Normalize the kernel
        kernel_2D /= kernel_2D.sum()
        
        return kernel_2D

    # Create Gaussian kernel
    gaussian = gaussian_kernel(kernel_size)
    
    # Expand the array by adding columns from the beginning to its end
    padding = kernel_size // 2
    expanded_array = np.hstack([array[:, -padding:], array, array[:, :padding]])
    
    # Apply convolution without wrapping
    convolved = scipy.signal.convolve2d(expanded_array, gaussian, mode='same', boundary='fill', fillvalue=0)
    
    # Extract the center portion
    blurred_array = convolved[:, padding:-padding]

    return blurred_array