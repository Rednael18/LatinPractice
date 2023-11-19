def damerau_levenshtein_distance(s1, s2):
    # Create a matrix to store distances
    d = [[0] * (len(s2) + 1) for _ in range(len(s1) + 1)]

    # Initialize first row and column of the matrix
    for i in range(len(s1) + 1):
        d[i][0] = i
    for j in range(len(s2) + 1):
        d[0][j] = j

    # Populate the matrix
    for i in range(1, len(s1) + 1):
        for j in range(1, len(s2) + 1):
            cost = 0 if s1[i - 1] == s2[j - 1] else 1
            d[i][j] = min(d[i - 1][j] + 1,         # deletion
                          d[i][j - 1] + 1,         # insertion
                          d[i - 1][j - 1] + cost)  # substitution

            # Check if transposition is possible
            if i > 1 and j > 1 and s1[i - 1] == s2[j - 2] and s1[i - 2] == s2[j - 1]:
                d[i][j] = min(d[i][j], d[i - 2][j - 2] + cost)  # transposition

    return d[-1][-1]

def main():
    # Read the input
    s1 = "Cognoveram"
    s2 = "Cognoscobam"

    # Compute the distance
    distance = damerau_levenshtein_distance(s1, s2)

    # Print the result
    print(distance)

if __name__ == "__main__":
    main()
