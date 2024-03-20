from argparse import ArgumentParser
from pathlib import Path
from model_timer import Timer 
from lpinstance import LPSolver,dietProblem
import json
import math

# Stencil created by Anirudh Narsipur March 2023


def main(args):
    # dietProblem()

    filename = Path(args.input_file).name
    timer = Timer()
    timer.start() 
    lpsolver = LPSolver(args.input_file)
    sol = lpsolver.solve()
    timer.stop()
  
    printSol = {
        "Instance" : filename,
        "Time" : round(timer.getElapsed(), 2),
        "Result" : math.ceil(sol), 
        "Solution" : "OPT"
    }

    print(json.dumps(printSol))


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("input_file", type=str)
    args = parser.parse_args()
    main(args)
