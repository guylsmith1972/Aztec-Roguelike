
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
