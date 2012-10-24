from galry import *
import numpy.random as rdn

class ColoredPointsPaintManager(PaintManager):
    def initialize(self):
        # generate random points
        positions = .25 * rdn.randn(100000, 2)
        # generate random colors (with alpha channel)
        colors = rdn.rand(len(positions), 4)
        # add plot
        self.add_plot(positions[:, 0], positions[:, 1], colors)

if __name__ == '__main__':
    # create window
    window = show_basic_window(paint_manager=ColoredPointsPaintManager)