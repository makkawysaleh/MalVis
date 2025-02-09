# MalVis Tool

  

Welcome to the MalVis tool! This tool is design to convert  Android bytecode .dex files into a visualization a .png file as output. It provides three options for the visualization [Entropy, MalVis-A, and MalVis-B]. For more information about these methods please read the related paper. <URL> 


## Usage

To run the tool, use the following command:

  
```sh

python main.py [options] infile [output]
```

## Options 
- `-c`, `--color`: Select a color scheme. Choose from the following MalVis representation options:
    
    - `entropy`: The entropy representation (default).
    - `malvis_a`: New approach using entropy with classbyte representation.
    - `malvis_b`: New approach using entropy with n-gram representation.
- `-q`, `--quite`: Don't show the progress bar - print the destination file name.
    
- `-s`, `--size`: Image width in pixels. The default is 256.

## Description

The MalVis tool takes a .dex file as input and generates a .png file as output. It provides three different color schemes to represent the data:

- **Entropy**: Uses the original entropy representation.
- **MalVis_A**: Uses entropy with classbyte representation.
- **MalVis_B**: Uses entropy with n-gram representation.

The tool also allows you to specify the size of the output image and whether to show a progress bar during the generation process.

## Requirements

- Python 3.x
- PIL (Python Imaging Library)

## Installation

To install the required dependencies, run:

```bash 
pip install pillow
```
## License

This project is licensed under the MIT License.
