def is_safe(board, row, col, n):
    # Check if there's a queen in the same column
    for i in range(row):
        if board[i][col] == 1:
            return False
    
    # Check upper left diagonal
    for i, j in zip(range(row, -1, -1), range(col, -1, -1)):
        if board[i][j] == 1:
            return False
    
    # Check upper right diagonal
    for i, j in zip(range(row, -1, -1), range(col, n)):
        if board[i][j] == 1:
            return False
    
    return True

def solve_n_queens(board, row, n):
    if row >= n:
        return 1
    
    count = 0
    for col in range(n):
        if is_safe(board, row, col, n):
            board[row][col] = 1
            count += solve_n_queens(board, row + 1, n)
            board[row][col] = 0
    
    return count

def n_queens_solution_count(n):
    board = [[0 for _ in range(n)] for _ in range(n)]
    return solve_n_queens(board, 0, n)

if __name__ == "__main__":
    try:
        n = int(input("Enter the size of the chessboard (n x n): "))
        if n <= 0:
            print("Please enter a positive integer.")
        else:
            result = n_queens_solution_count(n)
            print(f"Number of ways to place queens on a {n}x{n} chessboard: {result}")
    except ValueError:
        print("Invalid input. Please enter a positive integer.")
