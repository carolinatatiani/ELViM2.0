# /carolinatatiani/Working-Space/SuEL/Interface.py
'''
* Last Modified: 18 Sep, 2025  15:7:43
* by Carolina Tatiani
* email: carolina.tatiani@unesp.br
'''

import os
from turtle import bk
from unittest import case
import mdtraj as md
import numpy as np
import bokeh.plotting as bp
from bokeh.models import LinearColorMapper
from bokeh.palettes import Viridis256  # Or any other palette
from semver import match


print("Welcome to SuELEn\n") #TEMPORARY name


print("To continue with the analisis some information will be needed. Remember that your system should not contain water, for speed purposes. and SuAVE must be installed in your computer.\n")

while True:
	print("Do you want to \n"
	"A. continue interactively?\n"
	"B. using a configuration file?\n"
	"C. Plot projection\n"
	"D. exit the program\n")

	option = input()
	match option:
		case "A" | "a":
			print("You chose to continue interactively. \n")

			# Getting trajectory files
			trajectory_file = input("Please, enter the path to the trajectory file : ")
			while not os.path.isfile(trajectory_file):
				print("ERROR: Invalid input. Please enter a valid file path.\n")
				trajectory_file = input("Please, enter the path to the trajectory file: ")
			while os.path.getsize(trajectory_file) == 0:
				print("ERROR: The file is empty. Please provide a valid trajectory file.\n")
				trajectory_file = input("Please, enter the path to the trajectory file: ")
			print(f"Trajectory file '{trajectory_file}' found.\n")

			# Getting topology files
			topology_file = input("Please, enter the path to the topology file: ")
			while not os.path.isfile(topology_file):
				print("ERROR: Invalid input. Please enter a valid file path.\n")
				topology_file = input("Please, enter the path to the topology file: ")
			while os.path.getsize(topology_file) == 0:
				print("ERROR: The file is empty. Please provide a valid topology file.\n")
				topology_file = input("Please, enter the path to the topology file: ")
			print(f"Topology file '{topology_file}' found.\n")	

			# Getting dissimilarity matrix file (optional)	
			dm_exists = input("Do you have a dissimilarity matrix file? (y/n): ")
			if dm_exists.lower() == 'y':
				dm_file = input("Please, enter the path to the dissimilarity matrix file: ")
				while not os.path.isfile(dm_file):
					print("ERROR: Invalid input. Please enter a valid file path.\n")
					dm_file = input("Please, enter the path to the dissimilarity matrix file: ")
				while os.path.getsize(dm_file) == 0:
					print("ERROR: The file is empty. Please provide a valid dissimilarity matrix file.\n")
					dm_file = input("Please, enter the path to the dissimilarity matrix file: ")
				print(f"Dissimilarity matrix file '{dm_file}' found.\n")
			else:
				dm_file = None
				print("A dissimilarity matrix will be computed from the trajectory file.\n")

			elvim_selection=input("Choose the group for the ELViM analysis:\n")
			# Check ELViM atomic group selection
			valid_groups = ["protein", "CA", "all"]
			while elvim_selection not in valid_groups:
				print(f"Invalid ELViM atomic group selection. Please choose from {valid_groups}.\n")
				elvim_selection=input("Choose the group for the ELViM analysis:\n")
			elvim_flags=input("Write all the flags you want to use for the ELViM analysis. For example: -v -odm output.out -s0 0.9\n")
			suave_selection=input("Choose the atomic group for the SuAVE analysis:\n")
			bin=input("Choose the number of bins for the SuAVE analysis: \n")
			suave_flags=input("Write all the commands you want to use for the SuAVE analysis separeated  by ;. For example: s_area; s_thick;s_order\n")
			
			print("Proceeding with the analysis...\n")
			break

		case "B" | "b":
			print("You chose to use a configuration file\n")
			while True:
				input_file = input("Please, enter the path to the configuration file: ")
				if not os.path.isfile(input_file):
					print("Invalid input. Please enter a valid file path.\n")
					continue	
				else:
					print(f"Configuration file '{input_file}' found.\n")
					break					
			if os.path.getsize(input_file) == 0:
				print("The file is empty. Please provide a valid configuration file.\n")
				break
			else:
				config = {}
				with open(input_file, 'r') as file:
					for line in file:
						if '=' in line:
							key, value = line.split('=', 1)
							config[key.strip()] = value.strip().strip('"').strip("'")

				# Required parameters
				try:
					trajectory_file = config["Trajectory file"]
					topology_file = config["Topology file"]
					dm_file = config.get("dissimilarity_matrix_file", None)
					if dm_file == "none":
						dm_file = None
					elvim_selection = config["ELViM atomic group"]
					# Check ELViM atomic group selection
					valid_groups = ["protein", "CA", "all"]
					if elvim_selection not in valid_groups:
						print(f"Invalid ELViM atomic group selection: {elvim_selection}\n")
						exit()
					elvim_flags = config.get("ELViM flags", "")
					suave_selection = config.get("SuAVE atomic group", "")
					bin= config.get("Number of bins", "")
					suave_cmds = config.get("SuAVE commands", "")


					print(f"Trajectory file '{trajectory_file}' and topology file '{topology_file}' loaded from configuration file.\n")
					print("Details of the analysis:\n")
					if dm_file:
						print(f"Dissimilarity matrix file: {dm_file}\n")
					else:
						print("A dissimilarity matrix will be computed from the trajectory file.\n")
						print(f"ELViM atomic group: {elvim_selection}")
						print(f"ELViM flags: {elvim_flags}")
						print(f"SuAVE atomic group: {suave_selection}")
						print(f"Number of bins: {bin}")
						print(f"SuAVE commands: {suave_cmds}")
						break
				except KeyError as e:
					print(f"Missing required parameter in configuration file: {e}\n")
					break	

		case "C" | "c":
			print("You chose to plot the projection\n")
			projection_file = input("Please enter the path to the projection file: ")
			while not os.path.isfile(projection_file):
				print("ERROR: Invalid input. Please enter a valid file path.\n")
				projection_file = input("Please enter the path to the projection file: ")
			while os.path.getsize(projection_file) == 0:
				print("ERROR: The file is empty. Please provide a valid projection file.\n")
				projection_file = input("Please enter the path to the projection file: ")
			print(f"Projection file '{projection_file}' found.\n")
			color_file = input("Please enter the path to the file containing the data to color the projection: ")
			while not os.path.isfile(color_file):
				print("ERROR: Invalid input. Please enter a valid file path.\n")
				color_file = input("Please enter the path to the file containing the data to color the projection: ")
			while os.path.getsize(color_file) == 0:
				print("ERROR: The file is empty. Please provide a valid data file.\n")
				color_file = input("Please enter the path to the file containing the data to color the projection: ")
			print(f"Color data file '{color_file}' found.\n")

			# Load projection data
			proj=np.loadtxt(projection_file, comments='#')
			color_data=np.loadtxt(color_file, comments='#')

			# Create Bokeh plot
			TOOLS="hover,pan,wheel_zoom,zoom_in,zoom_out,reset,tap,save,box_select,poly_select,lasso_select,fullscreen,help"
			p=bp.figure(title="ELViM Projection colored by SuAVE Analysis", tools=TOOLS, active_drag="pan", active_scroll="wheel_zoom")
			
			x, y = proj[:, 0], proj[:, 1]

			color_min, color_max = color_data.min(), color_data.max()
			normalized_colors = (color_data - color_min) / (color_max - color_min)

			# Map normalized values to a colormap (e.g., Viridis256)
			color_mapper = LinearColorMapper(palette=Viridis256, low=0, high=1)
			hex_colors = [Viridis256[int(value * 255)] for value in normalized_colors]
			colors = hex_colors

			# Proceed to plot the projection
			p.scatter(x, y, color=colors, size=2, alpha=0.6)
			bk.output_file("projection.html")
			bk.show(p)
			print("Projection plot generated successfully as 'projection.html'.\n")
			exit()
			
		case "D" | "d":
				print("You chose to exit the program\n")		
				exit()
			
		case _:
			print("Invalid option. Please choose A, B, or C.\n")

# Load trajectory
try:
	traj = md.load(trajectory_file, top=topology_file)
	print("Trajectory loaded successfully.\n")
except Exception as e:
	print(f"Error loading trajectory: {e}\n")
	exit()

# Pre-process trajectory: centering and aligning
traj = traj.center_coordinates()
print("Trajectory centered successfully.\n")
traj.save_pdb('centered_ref.pdb')

# Prepare trajectory for ELViM analysis
traj_elvim = traj.atom_slice(traj.topology.select(f"name {elvim_selection}"))
traj_elvim.save('traj_elvim.dcd')
traj_elvim[0].save('ref_elvim.pdb')

# SuAVE analysis
print("Starting SuAVE analysis...\n")

suave_cmds_list = suave_cmds.split(';')
suave_cmds_list.insert(0, "s_index")
suave_cmds_list.insert(0,"s_grid")

for cmd in suave_cmds_list:
	match cmd:
		case "s_index":
			bash_command = f"{cmd} -in centered_ref.pdb"
		case "s_grid":
			bash_command = f"{cmd} -in centered_ref.pdb -ind ind1.ndx -bin -rmsd"
		case "s_area":
			cmd += f" -in centered_ref.pdb -ind1 ind1.ndx -ind2 ind2.ndx -bin -rmsd"
		case "s_thick":
			cmd += f" -in centered_ref.pdb -ind1 ind1.ndx -ind2 ind2.ndx -bin -rmsd -range"
		case "s_order":
			cmd += f" -in centered_ref.pdb -ind1 ind1.ndx -bin -rmsd"
		case "s_dens":
			cmd += f" -in centered_ref.pdb -ind1 ind1.ndx -ind2 ind2.ndx -dens lp1.ndx -bin -rmsd -slices"
		case "s_topog":
			cmd += f" -in centered_ref.pdb -ind1 ind1.ndx -ind2 ind2.ndx -bin"
		case _:
			print("Invalid SuAVE command. Skipping...\n")
	 
	print(f"Executing SuAVE command: {bash_command}\n")
	os.system(bash_command)
	# Check if the command was successful
	if os.WEXITSTATUS(os.system(bash_command)) == 0:
		print("SuAVE command executed successfully.\n")
	else:
		print("Error occurred while executing SuAVE command.\n")	

print("SuAVE analysis completed successfully.\n")

print("Proceeding with ELViM analysis...\n")

# ELViM analysis
if dm_file:
	elvim_flags += f" -dm {dm_file}"
else:
	elvim_flags += " -f traj_elvim.dcd -t ref_elvim.pdb"

bash_command_elvim = f" python ELViM.py {elvim_flags}"
os.system(bash_command_elvim)

print("ELViM analysis completed successfully.\n")

print("SuELEn analysis finished. Thank you for using SuELEn!\n")