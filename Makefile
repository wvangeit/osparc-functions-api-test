clean:
clean-solver:
	rm -rf solver_files/function_code.py
	rm -rf solver_files/tmp*
	rm -rf solver_files/function_output.json
solver_functions: clean-solver
	./solver_functions.sh
project_functions: clean
	./project_functions.sh
gui_solver: clean
	./gui_solver.sh

