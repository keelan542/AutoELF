# AutoELF

This is a simple python program, that is designed to speed up the workflow of generating Electron Localisation Function (ELF) plots. This program assumes that the attractors file used as input has been generated using Multiwfn, and is in the .pdb file format. 

## Installation

1. Download the main project directory.
2. Extract to a suitable location
3. Add parent directory location to PYTHONPATH environment variable: export PYTHONPATH=[path_to_parent_directory]:$PYTHONPATH e.g. export PYTHONPATH=$HOME/software/python_programming:$PYTHONPATH where python_programming directory contains the autoelf directory with all required project files.

## Usage in a .py script

1. from autoelf import *
2. Directly call function: auto_elf_assign(xyzfile, pdbfile, interest_atoms=[], final_cube=False)
    - xyzfile: Molecular geometry, given as a string e.g. "ethene.xyz"
    - pdbfile: File containing the list of attractors, given as a string e.g. "ethene.pdb"
    - interest_atoms: List of atoms that you are interested in, given as a list of atom indices (counting starts from 0) e.g. [0,1]
    - final_cube: Can be True or False. If set to True, will append attractors corresponding to atoms of interest to ELF isosurface cube file. Requires the presence of the .cub file produced by Multiwfn, where the basename is the same as the xyz file name e.g. "ethene.cub"
3. What is produced ?
    - [basename]_all.xyz --> Contains all CORE and VALENCE attractors appended as dummy atoms to molecular geometry. This is also present in stdout.
    - [basename]_requested.xyz --> Contains all VALENCE attractors corresponding to atoms of interest appended as dummy atoms to molecular geometry.
    - [basename]_updated.cube --> Produced if final_cube was set to True. Contains ELF isosurface, molecular geometry and VALENCE attractors (all or of interest). This can be visualised in programs such as Chemcraft, Avogadro and VMD.


