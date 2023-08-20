# AutoELF

This is a simple python program, that is designed to speed up the workflow of generating Electron Localisation Function (ELF) plots. This program assumes that the attractors file used as input has been generated using Multiwfn, and is in the .pdb file format. 

## Installation

1. Download the main project directory.
2. Extract to a suitable location
3. Add parent directory location to PYTHONPATH environment variable: export PYTHONPATH=$HOME/software/[parent_directory]/:$PYTHONPATH

## Dependencies

The [ASH](https://github.com/RagnarB83/ash) multiscale modelling program is utilised to carry out cube file manipulations. So if the final_cube flag is set to True, ASH is a requirement.

## Usage

1. Add to any .py script: from autoelf import *
2. Directly call function: auto_elf_assign(xyzfile, pdbfile, interest_atoms=[], final_cube=False)
    - xyzfile: Molecular geometry, given as a string e.g. "ethene.xyz"
    - pdbfile: File containing the list of attractors, given as a string e.g. "ethene.pdb"
    - interest_atoms: List of atoms that you interested in, given as a list of atom indices (counting starts from 0) e.g. [0,1]
    - final_cube: Can be True or False. If set to True, will append attractors corresponding to atoms of interest to ELF isosurface cube file. Requires the presence of the .cub file produced by Multiwfn, where the basename is the same as the xyz file name e.g. "ethene.cub"

