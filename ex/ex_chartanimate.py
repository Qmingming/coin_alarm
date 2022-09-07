import datetime as dt
from random import randint

import matplotlib.pyplot as plt
import matplotlib.animation as animation



# Create figure for plotting
fig = plt.figure()
ax = []

#ax2 = fig.add_subplot(1, 2, 2)

# This function is called periodically from FuncAnimation
def animate(i, coin1, coin2):

    # Draw x and y lists
    time = dt.datetime.now().strftime('%H:%M:%S.%f')
    coin1.getPrice()
    coin1.getTime(time)
    ax.clear()
    ax.plot(coin1.xs, coin1.ys, label=coin1.name)

    coin2.getPrice()
    coin2.getTime(time)
    ax.plot(coin2.xs, coin2.ys, label=coin2.name)

    #ax2.clear()
    #ax2.plot(coin2.xs, coin2.ys)

    # Format plot
    plt.xticks(rotation=45, ha='right')
    plt.subplots_adjust(bottom=0.30)
    plt.title('TMP102 Temperature over Time')
    plt.ylabel('Temperature (deg C)')
    plt.legend()

# Set up plot to call animate() function periodically
coin1 = Coin("btc")
coin2 = Coin("eth")

ani = animation.FuncAnimation(fig, animate, fargs=(coin1, coin2), interval=100)
plt.show()
