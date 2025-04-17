import numpy as np

def main(x=None,y=None):
    return {"2D sinc": np.sinc(x) * np.sinc(y)}