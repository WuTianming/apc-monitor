import os
import datetime as dt
import matplotlib.pyplot as plt
import matplotlib.ticker as plticker
from matplotlib.dates import DateFormatter, MinuteLocator
import matplotlib.animation as animation
import numpy as np

# Create figure for plotting
fig = plt.figure()
ax = fig.add_subplot(1, 1, 1)

period = 20
threshold = 3000
starttime = dt.datetime.now()

xs = np.zeros(period+2, dtype='datetime64[ms]')
ys = np.zeros(period+2)

APC_IP = os.environ['APC_IP']
if APC_IP == None:
    print("set the environment variable \"APC_IP\" to be the IP of the PDU.")
    exit(1)

# run shell command and capture output:
# snmpwalk -v 1 -c public <IP> .1.3.6.1.4.1.318.1.1.12.2.3.1.1.2.1
# the output should look like:
# SNMPv2-SMI::enterprises.318.1.1.12.2.3.1.1.2.1 = Gauge32: 71
# extract the last number in the line, then divide it by 10
def get_amps():
    import subprocess
    cmd = "snmpwalk -v 1 -c public {} .1.3.6.1.4.1.318.1.1.12.2.3.1.1.2.1".format(APC_IP)
    output = subprocess.check_output(cmd, shell=True)
    amps = output.split()[-1]
    return float(amps) / 10

# This function is called periodically from FuncAnimation
def animate(i, xs, ys):
    data = get_amps() * 230

    nowtime = dt.datetime.now()

    # Add x and y to lists
    xs[:-1] = xs[1:]
    xs[-1] = nowtime
    ys[:-1] = ys[1:]
    ys[-1] = data

    # Draw x and y lists
    ax.clear()
    ax.plot(xs, ys)

    # Format plot
    plt.title('Power over time')
    plt.ylabel('Power (Watts)')
    plt.xticks(rotation=45, ha='right')
    plt.subplots_adjust(bottom=0.20)
    ax.xaxis.set_major_locator(MinuteLocator(interval=1))
    ax.xaxis.set_major_formatter(DateFormatter("%H:%M"))

    # set x axis
    if nowtime - dt.timedelta(seconds=period) > starttime:
        ax.set_xlim(nowtime - dt.timedelta(seconds=period), nowtime)
    else:
        ax.set_xlim(starttime, starttime + dt.timedelta(seconds=period))

    # set y axis
    plt.ylim(0, 6000)

    # color the part between x axis and the data line
    ax.fill_between(xs, ys, color='blue', alpha=0.2)

    # color the part exceeding the threshold
    ax.fill_between(xs, threshold, ys, where=(ys > threshold), color='orange')


# Set up plot to call animate() function periodically
ani = animation.FuncAnimation(fig, animate, fargs=(xs, ys), interval=1100)
plt.show()
