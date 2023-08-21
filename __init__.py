import math
import shutil
import sys
import os
import re

# Defining covalent radii
cov_radii = {"H":0.31, "He":0.28, "Li":1.28, "Be":0.96, "B":0.85, "C":0.76,
                "N":0.71, "O":0.66, "F":0.57, "Ne":0.58, "Na":1.66, "Mg":1.41,
                "Al":1.21, "Si":1.11, "P":1.07, "S":1.05, "Cl":1.02, "Ar":1.06,
                "K":2.03, "Ca":1.76, "Sc":1.70, "Ti":1.60, "V":1.53, "Cr":1.39,
                "Mn":1.39, "Fe":1.32, "Co":1.26, "Ni":1.24, "Cu":1.32, "Zn":1.22,
                "Ga":1.22, "Ge":1.20, "As":1.19, "Se":1.20, "Br":1.20, "Kr":1.16,
                "Rb":2.20, "Sr":1.95, "Y":1.90, "Zr":1.75, "Nb":1.64, "Mo":1.54,
                "Tc":1.47, "Ru":1.46, "Rh":1.42, "Pd":1.39, "Ag":1.45, "Cd":1.44,
                "In":1.42, "Sn":1.39, "Sb":1.39, "Te":1.38, "I":1.39, "Xe":1.40,
                "Cs":2.44, "Ba":2.15, "La":2.07, "Hf":1.75, "Ta":1.70, "W":1.62,
                "Re":1.51, "Os":1.44, "Ir":1.41, "Pt":1.36, "Au":1.36, "Hg":1.32,
                "Tl":1.45, "Pb":1.46, "Bi":1.48, "Po":1.40, "At":1.50, "Rn":1.50}

# Function to get and return geometry of molecule
def get_geom(xyzfile):
    geometry = []
    with open(xyzfile) as file:
        # Skip first two lines containing header
        next(file)
        next(file)
        
        # Loop through each line and grab the element symbol and coordinates
        for line in file:
            el_symbol, xcoord, ycoord, zcoord = line.split()
            geometry.append([el_symbol, [float(xcoord), float(ycoord), float(zcoord)]])
    
    return geometry

# Function to get and return coordinates of attractors
def get_attractors(pdbfile):
    coords = []
    with open(pdbfile) as file:
        # Loop through each line and grab the attractor number and its coordinates
        for line in file:
            attractor, xcoord, ycoord, zcoord = [line.split()[i] for i in (5,6,7,8)]
            coords.append([attractor, [float(xcoord), float(ycoord), float(zcoord)]])

    return coords

# Function to calculate and return a distance matrix
def calc_distances(geom, attractors):
    distance_matrix = []
    
    for attractor in attractors:
        for atom in geom:
            # Assign variables to make distance calculation more readable
            attractor_num = attractor[0]
            atom_symbol = atom[0]
            attr_xcoord, attr_ycoord, attr_zcoord = attractor[1]
            atom_xcoord, atom_ycoord, atom_zcoord = atom[1]

            # Distance calculation
            distance = math.sqrt((attr_xcoord - atom_xcoord)**2 + (attr_ycoord - atom_ycoord)**2 + (attr_zcoord - atom_zcoord)**2)
            distance_matrix.append((attractor_num, atom_symbol, distance))
    
    # Split distance matrix into separate sublists, each containing the distance to each atom for a specific attractor
    distance_matrix_split = list(chunks(distance_matrix, len(geom)))
    
    return distance_matrix_split

# Function that splits a list into evenly sized chunks
def chunks(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

# Generate range of floats to used for range of scaling factors
def frange(radius, scaling_factor=1.00):
    while scaling_factor < 1.40:
        yield (radius * scaling_factor)
        scaling_factor += 0.05

# Function to assign attractors to atoms, and specify whether they are CORE or VALENCE
def assign(distance_matrix, core_threshold=0.4):
    assignments = []
    problems = []
    for attractor in distance_matrix:
        core_atom_list = []
        valence_atom_list = []
        for atom_index, atom in enumerate(attractor):
            # Get distance to current atom
            distance = atom[2]

            # Generate list of scaled covalent radii for current atom (scaling_factor = 1.0, 1.05, ... , 1.40)
            cov_radius_scaled = list(frange(cov_radii[atom[1]]))

            if distance > core_threshold:
                # Check if the distance is within any of the scaled radii for the current atom
                # If so, break from the loop to avoid going to higher scaling factors
                # This is a very safe way to test scaling factors --> Confined to individual atoms rather than using global scaling factor
                # This means that in theory, the same elements in different chemical environments will be accounted for
                for scaled_radius in cov_radius_scaled:
                    if distance < scaled_radius:
                        valence_atom_list.append((atom[1], atom_index))
                        break
            elif distance < core_threshold:
                core_atom_list.append((atom[1], atom_index))
        
        if len(core_atom_list) == 1:
            assignments.append((atom[0], "CORE", core_atom_list))
        elif 0 < len(valence_atom_list) <= 2: 
            assignments.append((atom[0], "VALENCE", valence_atom_list))

    return assignments

# Function to output all CORE and VALENCE assignments to stdout and also to file
def output_assignments(assignments, xyzfile):
    assignments = sorted(assignments, key = lambda x: x[1], reverse=True)
    # Header line for listing out all attractors and their assignments
    print(f"Attractor    Core/Valence    Atoms    Indices")
        
    # Writing each assignment to file and to stdout
    for assignment in assignments:  
        print(f"{assignment[0]:<13}{assignment[1]:<16}{','.join(atom[0] for atom in assignment[2]):<9}{','.join(str(atom_index[1]) for atom_index in assignment[2]):<7}")   
    
# Function to write only the relevant requested attractor assignments to a xyz
def write_attractor_xyz(assignments, attractors, xyzfile, interest_atoms):
    attractors_bohrs = []

    if len(interest_atoms) > 0:
        shutil.copyfile(xyzfile, f"{xyzfile[:-4]}_requested.xyz")
        with open(f"{xyzfile[:-4]}_requested.xyz", "a") as file:
            for i, assignment in enumerate(assignments):
                assigned_atom_indices = [atom_index[1] for atom_index in assignment[2]]
                if assignment[1] == "VALENCE":
                    for index in assigned_atom_indices:
                        if index in interest_atoms:
                            file.write(f"X\t{attractors[i][1][0]:.8f}\t{attractors[i][1][1]:.8f}\t{attractors[i][1][2]:.8f}")
                            file.write("\n")
                            attractors_bohrs.append([attractors[i][1][0]*1.88973, attractors[i][1][1]*1.88973, attractors[i][1][2]*1.88973])

    shutil.copyfile(xyzfile, f"{xyzfile[:-4]}_all.xyz")
    with open(f"{xyzfile[:-4]}_all.xyz", "a") as file:
        for i, assignment in enumerate(assignments):
            file.write(f"X\t{attractors[i][1][0]:.8f}\t{attractors[i][1][1]:.8f}\t{attractors[i][1][2]:.8f}")
            file.write("\n")
            if assignment[1] == "VALENCE":
                attractors_bohrs.append([attractors[i][1][0]*1.88973, attractors[i][1][1]*1.88973, attractors[i][1][2]*1.88973])
    
    return attractors_bohrs

# Function to append requested attractors to cube file for visualistion
def append_cube(cubefile, attractors_bohrs):
    # Opening original cubefile
    contents = None
    with open(cubefile, "r") as original_cube:
        contents = original_cube.readlines()
    
    # Gettings number of atoms to know the position at which to start inserting attractors
    num_atoms = int(contents[2].split()[0])
    start_position = 6 + num_atoms
   
    # Replacing number of atoms to reflect added attractors
    new_num_atoms = num_atoms + len(attractors_bohrs)
    num_atom_line = re.split(f"(\s+)", contents[2])
    num_atom_line[2] = str(new_num_atoms)
    contents[2] = "".join(num_atom_line)

    # Loop through list of attractors, adding to original_cube_contents
    for attractor in attractors_bohrs:
        formatted_attractor = f"{'0':>5}{0.0:>12.6f}{attractor[0]:>12.6f}{attractor[1]:>12.6f}{attractor[2]:>12.6f}\n"
        contents.insert(start_position, formatted_attractor)
        start_position += 1

    # Create new cubefile, containing attractors
    with open(f"{cubefile[:-4]}_updated.cub", "w") as new_cube:
        new_cube.write("".join(contents))

# Main function of program
def auto_elf_assign(xyzfile, attractorfile, interest_atoms = [], final_cube=False):
    # Printing a message to indicate the start of assignment
    print("="*120)
    print(f"Starting assignment for {xyzfile[:-4]}")
    print("="*120)

    # Get geometry from xyz file
    geom = get_geom(xyzfile)

    # Get attractors from pdb file
    attractors = get_attractors(attractorfile)

    # Get distance matrix
    distance_matrix = calc_distances(geom, attractors)
    
    # Get assignments of attractors to CORE and VALENCE
    assignments = assign(distance_matrix)
    
    # Write relevelant assignments to xyz file  
    attractors_bohrs = write_attractor_xyz(assignments, attractors, xyzfile, interest_atoms)

    # Output assignments to txt file
    output_assignments(assignments, xyzfile)
        
    # Confirmation messages 
    print("="*120)
    print(f"Success! Ending Assignment for {xyzfile[:-4]}\n")
    print(f"Valence attractors corresponding to atoms of interest (if specified) were written to {xyzfile[:-4]}_requested.xyz")
    print(f"All valence attractors were written to {xyzfile[:-4]}_all.xyz")
    
    # Begin process of editing cube file to contain relevant attractors if final_cube has been set to True
    if final_cube == True and os.path.isfile(f"{xyzfile[:-4]}.cub"):
        append_cube(f"{xyzfile[:-4]}.cub", attractors_bohrs)
        print(f"{xyzfile[:-4]}_updated.cub created, where (requested) valence attractors have been apppended to cube file.")
    else:
        print(f"\nWarning: No file named {xyzfile[:-4]}.cub was found for appending attractors to.")
    print("="*120)

