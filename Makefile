clean:
clean-solver:
	rm -rf solver_files/function_code.py
	rm -rf solver_files/tmp*
	rm -rf solver_files/function_output.json
clean-gui-solver:
	rm -rf gui_solver_files/function_code.py
	rm -rf gui_solver_files/tmp*
	rm -rf gui_solver_files/function_output.json
solver_functions: clean-solver
	./solver_functions.sh
project_functions: clean
	./project_functions.sh
gui_solver: clean-gui-solver
	./gui_solver.sh

