import os
import sys
import analysis

def batchAnalysis(cellDirectory):
    fileExt = ".abf"
    recFiles = [os.path.join(cellDirectory, recFile) for recFile in os.listdir(cellDirectory) if recFile.endswith(fileExt)]

    for files in recFiles:
        analysis.main(files)

if __name__ == "__main__":
    cellDirectory = os.path.abspath(sys.argv[1])
    batchAnalysis(cellDirectory)


