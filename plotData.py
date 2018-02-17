#!/usr/bin/env python3
"""
Plot tabular output data from many separate files(*.out), using a spectral color map in matplotlib
The spectral color map allows the user to clearly distinguish between many lines on the plot,
while clearly observing the time history of the data for multiple data sets simultaneously.
Uses regular expressions to extract the X/Y axis labels from the tabulated data files

Python version: 3.6.4
Author: Prashanth Rao
Date: 02/16/2018
"""
import matplotlib.pyplot as plt
import numpy as np
import os
import re
import time

def getFiles(ext, filepath):
    """
    Get a list of all files of a specified extension in the local directory.
    """
    filenames = next(os.walk(os.path.abspath(filepath)))[2]
    fileList = [f for f in filenames if f.endswith(ext)]

    return fileList

def sortFiles(l):
    """
    os.walk() returns a randomly arranged list of filenames with a specified extension.
    This function performs a "natural" sorting of the filenames so that plot legend appears alphabetically.
    """
    convert = lambda text: int(text) if text.isdigit() else text.lower()
    alphanum_key = lambda key: [convert(c) for c in re.split('([0-9]+)', key)]

    return sorted(l, key = alphanum_key)

def readFile(filename, lineskip=1):
    """
    Read in *.out file as per tabular output and parse the required data.
    lineskip is the number of header lines we want to skip when reading data
    """
    column1 = []
    column2 = []
    with open(filename) as f:
        for line in f:
            column1.append(line.split()[0])
            column2.append(line.split()[1])

    del column1[:lineskip]
    del column2[:lineskip]

    op1 = [float(i) for i in column1]
    op2 = [float(i) for i in column2]

    output = [op1, op2]

    return output

def getHeader(filepath, file):
    """
    Get header information from the tabular .out file without user interaction.
    """
    flag = 0
    expression = re.compile(r'"(.*?)"\s?"(.*?)"') # Pre-compile regular expression before using in loop

    with open(filepath + "/" + file) as f:    # Open file
        for line in f:       # Iterate through lines of file
            pattern = expression.match(line) # Match the pattern "AnyText" "AnyText"
            if pattern:     # Only store headers if the pattern is matched
                header = [pattern.groups()[0], pattern.groups()[1]]   # Store the first and second terms of header
                print("Identified X/Y axes of the .out files as '%s' and '%s'" % (pattern.groups()[0], pattern.groups()[1]))

                # Check if the header has the word "Temperature" to display its units in deg Celsius
                if header[1].find("Temperature") > 0:
                    header[1] += " ($^\circ$C)"
                    flag = 1
                else:
                    flag = 2
            else:
                flag = -1
                header = ["Unknown", "Unknown"]

    return flag, header

def plotData(filepath, outFiles, out_extension, plotname, flag, header):
    """
    Plot data using Matplotlib and output tabular data to a text file.
    """
    fig = plt.figure()
    ax = fig.add_subplot(111)
    L = len(outFiles)
    color_idx = np.linspace(0, 1, L)    # Divide the colorbar into "L" number of divisions, where "L" is the number of outFiles

    # Open text file to dump out last-value of each temperature monitor as a table
    with open("TableData.dat", "w") as f:
        for index, inputfile in enumerate(outFiles):
            output = readFile(filepath + "/" + inputfile, lineskip=2) # readFile(filename, lineskip): lineskip MUST be an integer

            if flag == 1:   # Convert temperature column to deg Celsius (we know the input was in Kelvin)
                output[1] = [i-273.15 for i in output[1]]
                title_field = "Temperature history in $^\circ$C"
            else: title_field = "Solution Variable History in SI Units"

            # Begin plotting (line color is chosen based on color-splitting the spectral color map)
            ax.plot(output[0], output[1], linestyle='-', label=inputfile.replace(".out", ""), color=plt.cm.spectral(color_idx[index]))
            handles, labels = ax.get_legend_handles_labels()
            lgd = ax.legend(handles, labels, loc='upper center', fontsize=7, bbox_to_anchor=(1.2, 1))
            ax.grid(b='on', linestyle='--', linewidth=0.75)

            # Round last entry to 1 decimal for output to table
            rounded_temp = round(output[1][-1], 2)
            f.write(inputfile.replace(out_extension, "") + "\t\t"+ str(rounded_temp)+"\n")

        plt.title(title_field)
        plt.xlabel(header[0])
        plt.ylabel(header[1])
        fig.savefig(plotname, bbox_inches='tight')

    return

# Run
if __name__ == '__main__':

    a = time.time() # Start timer

    filepath = "ExampleData/"
    out_extension = ".out"   # Extension of out files we want to read data from
    plotname = "convergencePlot.png"    # name of output Plot file

    outFiles = getFiles(out_extension, filepath)   # Get list of out files in current directory
    outFiles = sortFiles(outFiles)       # natural-sort file names alphabetically and store that in a list
    flag, header = getHeader(filepath, outFiles[0])  # Get header info from the first .out file (for plotting)
    plotData(filepath, outFiles, out_extension, plotname, flag, header)    # Plot Data

    print("Parsed %i out files in %.8f seconds...\n" %(len(outFiles), time.time() - a))
