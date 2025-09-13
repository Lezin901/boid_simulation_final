import matplotlib.pyplot as plt
from matplotlib import animation
from matplotlib.animation import FuncAnimation
from config import XMAX, YMAX, STEPS_TOTAL


def visualize(position_array):
    # Matplotlib-Setup
    fig, ax = plt.subplots()
    scat = ax.scatter(position_array[0, :, 0], position_array[0, :, 1])
    ax.set_xlim(0, XMAX)
    ax.set_ylim(0, YMAX)
    ax.set_title("Boid-Simulation")

    # Update-Funktion
    def update(frame):
        scat.set_offsets(position_array[frame, :, :])
        return scat,

    # Animation starten
    ani = FuncAnimation(fig, update, frames=STEPS_TOTAL, interval=50, blit=True)
    writer = animation.PillowWriter(fps=15)
    ani.save(f'output/output.gif')