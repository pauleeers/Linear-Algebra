import numpy as np
import sympy
import re
from fractions import Fraction
from tkinter import *

rows = 0
cols = 0

root = Tk()
root.title("Systems of Linear Equations Calculator")
default_font = ("Arial Rounded MT Bold", 10) 

# Set the default font for the root window
root.option_add("*Font", default_font)
root.config(bg='azure2')
root['padx']=10

root['pady']=10

input_values = []
const_values = []
equation_labels = []


#FUNCTIONS
#function to print the grid
def print_grid():
    global rows, cols
    
    rows = int(input_1.get())
    cols = int(input_2.get())

    #clear the window first before creating the matrix
    new_matrix()

    if 2 <= rows <= 5 and 2 <= cols <= 5:
        #Creating the label for each variable
        for j in range(cols):

            label = Label(root, text=f"x_{j+1}")
            label.grid(row=1, column=j+1, padx=5, pady=5)
            label.config(bg="azure2")

        #Label for const
        const_label = Label(root, text="constants")
        const_label.grid(row=1, column=cols+1)
        const_label.config(bg="azure2")

        matrix_label = Label(root, text=f"Your {rows} x {cols} Matrix")
        matrix_label.grid(row=1, column=0)
        matrix_label.config(bg="azure2")


        for i in range(rows):
            #Label for each equation
            equation_label = Label(text=f"equation {i+1}")
            equation_label.grid(row=i+5)
            equation_label.config(bg="azure2")
            equation_labels.append(equation_label)

            for j in range(cols):
                values = Entry(root, width=10)
                values.grid(row=i+5, column=j+1, padx=5, pady=5)
                #values.config( borderwidth=0)
        
                input_values.append(values)
            
            # New column for constant entries
            const_entry = Entry(root, width=10)
            const_entry.config(bg="lightblue")
            const_entry.grid(row=i+5, column=cols+1, padx=5, pady=5)
            const_values.append(const_entry)

    elif  rows < 2 or cols < 2 :
        err_1 = Label(text="Please Enter a Valid input : minimum of 2 coefficients and equations")
        err_1.grid(row=1, column=0,  columnspan=10)
        err_1.config(fg='red')
    elif  rows > 5 or cols >5 :
        err_2 = Label(text="Please Enter a Valid input : maximum of 5 coefficients and equations")
        err_2.grid(row=1, column=0,  columnspan=10)
        err_2.config(fg='red')

    sol_row = rows+1


#function to remove the previous matrix
def new_matrix():
    for label in root.grid_slaves(row=1):
        label.grid_forget()

    for values in input_values:
        values.destroy()

    for label in equation_labels:
        label.grid_forget()

    for const_entry in const_values:
        const_entry.grid_forget()
   
    input_1.delete(0,END)
    input_2.delete(0,END)

    input_values.clear()
    const_values.clear()
    equation_labels.clear()

    for widget in solution_frame.winfo_children():
        widget.destroy()
        solution_frame.config(bg="azure2")


# Function to get the value from a specific cell
def get_cell_value(row, col):
    index = row * cols + col
    return input_values[index].get()


# Solution function
def solve_linear_equations(coefficients, constants):
    # Augment the coefficients matrix with the constants vector
    augmented_matrix = np.hstack((coefficients, constants.reshape(-1, 1)))
    # Convert to a sympy Matrix and compute the RREF
    rref_matrix, pivot_columns = sympy.Matrix(augmented_matrix).rref()
    rref_matrix = np.array(rref_matrix.tolist(), dtype=float)

    # Check for inconsistency: a row of zeros in coefficients with a non-zero constant
    for i in range(len(rref_matrix)):
        if np.allclose(rref_matrix[i, :-1], 0) and not np.isclose(rref_matrix[i, -1], 0):
            return None, "No solution"

    num_rows, num_cols = rref_matrix.shape
    free_vars = num_cols - num_rows - 1  # -1 for the constants column

    if free_vars > 0:
        
        # Infinite solutions, proceed to express in terms of free variables
        solution_set = []
        for i in range(num_rows):
            if i in pivot_columns:
                leading_coeff = rref_matrix[i][i]
                expression = f"{rref_matrix[i, -1]/leading_coeff}"
                for j in range(i + 1, num_cols - 1):
                    if rref_matrix[i, j] != 0:
                        expression += f" - {rref_matrix[i, j]/leading_coeff}*x{j+1}"
                solution_set.append(expression)
        # Add expressions for free variables
        for i in range(num_rows, num_cols - 1):  # -1 to exclude the constants column
            if i not in pivot_columns:
                solution_set.append(f"x{i+1} is a free variable")
        
        parametric_solution = ', '.join(solution_set)
        return parametric_solution, "Infinite solutions"
    elif len(pivot_columns) == num_rows:
        # Unique solution, extract it from the last column of the RREF
        unique_solution = rref_matrix[:, -1]
        return unique_solution, "Unique solution"
    else:
        # Underdetermined system with no unique solution
        return None, "Infinite solutions, cannot express as unique solution"



#Formatting the solution
def format_parametric_solution(solution_str):
    # Split the solution string into individual variable components
    variables = solution_str.split(',')

    # Define a pattern to match the variables like 'x4' and 'x5'
    var_pattern = re.compile(r'x\d+')

    formatted_solution = []

    for i, var in enumerate(variables):
        # Find all free variables in the expression
        free_vars = var_pattern.findall(var)

        # Correctly identify negative and positive floats
        expr = re.sub(r'(?<!\w)-?\d+\.\d+', lambda m: str(Fraction(float(m.group(0))).limit_denominator()), var)

        # If the variable part is a free variable, format it accordingly
        if i + 1 in [int(free_var[1:]) for free_var in free_vars]:
            formatted_solution.append(f"x{i+1} is a free variable")
        else:
            # Remove unnecessary pluses and correct double negatives
            expr = expr.replace(' - -', ' + ').replace('+-', '-')
            formatted_solution.append(f"x{i+1} = {expr.strip()}")

    return formatted_solution




# Add this new function to display the solution
def display_solution(solution, status):
    # Clear the previous solution display if any
    for widget in solution_frame.winfo_children():
        widget.destroy()

    # Display the status
    status_label = Label(solution_frame, text=f"Status: {status}")
    status_label.pack()
    status_label.config(bg="darkseagreen1")

    # Display the solution
    if status != "No solution":
        # Ensure solution is passed as a string representation to the formatting function
        formatted_solution_list = format_parametric_solution(str(solution))
        
        # Concatenate the formatted solutions into a single string with line breaks
        formatted_solution_str = "\n".join(formatted_solution_list)
        
        solution_label = Label(solution_frame, text=f"Solution:\n{formatted_solution_str}")
        solution_label.pack()
        solution_label.config(bg="darkseagreen1")
    else:
        solution_label = Label(solution_frame, text="No solution exists for the given system.")
        solution_label.pack()
        solution_label.config(bg="darkseagreen1")



# Modify this existing function to solve the equations and display the results
def arr2d_func():
    global coefficient_arr, const_arr
    const_arr = []
    coefficient_arr = []

    for i in range(rows):
        row_values = []
        for j in range(cols):
            value = get_cell_value(i, j)
            try:
                value = Fraction(value)  # Use fractions for exact arithmetic
            except ValueError:
                value = Fraction(0)
            row_values.append(value)
        coefficient_arr.append(row_values)

        const_value = const_values[i].get()
        try:
            const_value = Fraction(const_value)
        except ValueError:
            const_value = Fraction(0)
        const_arr.append(const_value)

        solution_frame.config(bg="darkseagreen1")

    # Convert the arrays to NumPy arrays
    coefficients_array = np.array(coefficient_arr, dtype=float)
    constants_array = np.array(const_arr, dtype=float)

    # Solve the system of equations
    solution, status = solve_linear_equations(coefficients_array, constants_array)

    # Display the results
    display_solution(solution, status)

#GUI INPUTS
# Taking user input for dimensions
label_row = Label(text="Enter number of equations:", justify="left")
label_row.grid(row=0, column=0)
label_row.config(bg="azure2")
input_1 = Entry(root, width=10)
input_1.grid(row=0, column=1)
input_1.config(borderwidth=0)

label_col = Label(text="Enter number of coefficients:", justify="left")
label_col.grid(row=0, column=2)
label_col.config(bg="azure2")

input_2 = Entry(root, width=10)
input_2.grid(row=0, column=3, padx=2)
input_2.config(borderwidth=0)
 
#Create matrix button
grid_button = Button(root, text="Create Matrix", command=print_grid)
grid_button.grid(row=0, column=4, padx=5)
grid_button.config(bg="royalblue", fg="white")

#New Matrix button
new_button = Button(root, text="Clear All", command=new_matrix, width=10)
new_button.grid(row=0, column=5,  padx=5)
new_button.config(bg="royalblue", fg="white")

#print array
solve_button = Button(root, text="Solve", command=arr2d_func, width=10)
solve_button.grid(row=0, column=6, padx=5)
solve_button.config( bg="royalblue", fg="white")

# Create a frame to display the solution
solution_frame = Frame(root)
solution_frame.grid(row=rows+8, column=0, columnspan=10, pady=(10, 0))
solution_frame.config(bg="darkseagreen1")

root.mainloop()