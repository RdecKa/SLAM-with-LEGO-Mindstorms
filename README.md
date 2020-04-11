# SLAM with LEGO Mindstorms
A system that helps a robot to explore the world. By collecting measurements
from the robot's sensors and telling the robot where to go next it constructs a
map of the world.

The robot can be either a real LEGO Mindstorms robot or a simulated one. It
is easier to develop the logic using the simulated robot but it is much more
fun observing a phisical robot wandering around.

## Examples
The GIFs below show two examples - one with the LEGO robot (left/top) and one simulated (right/bottom).
For the explanation of symbols, see below.

![Example of the LEGO robot](docs/img/example_lego.gif)
![Example of a simulated robot](docs/img/example_simulated.gif)

Here is how the LEGO robot actually looks like:

![LEGO robot in action](docs/img/example_lego_robot.gif)

### Explanation of the maps:

- Red dots and the solid black line: Position of the robot through time
- Gray circle around the red dots: The size of the robot
- Orange dots and the black dashed line: Planned path
- Blue dots: Detected obstacles
- Light green dots: Detected free spots (the sensor has a limited view and
  can't see an obstacle further than that)
- Dark green dots: Possible locations to continue exploration
- Blue cells in the grid: Expected obstacle positions
- Brown cells in the grid: Expected free positions

## How do I run it?
1. If the most recent version of Python that you have installed is below 3.8,
   you can't<sup>1</sup>. I'm sorry.
2. Clone this repository.
3. In the root directory, run:
   1. `make init` to create a virtual environment and install requirements,
   2. `make run` to run the program.
4. In the subsequent runs, only `make run` is needed.

That's it for the simulated robot! Nothing difficult, you should try it
out<sup>2</sup>!

### But I have a LEGO EV3 Brick and I want to see it in action!
1. Check that you have Python 3.8 (or higher) installed on your computer.
2. Clone this repository.
3. Set HOST and PORT in `slam/config.py` and `slam/mindstorms/slam_lego/config.py`.
   HOST should be the IP address of the EV3. Make sure the ports in both files
   are the same.
4. Upload the content of `slam/mindstorms/slam_lego` to your EV3 Brick (I'm
   using [ev3dev](https://www.ev3dev.org)).
5. Run `python3 main.py` on the EV3.
6. On your computer, run the following from the root directory:
   1. `make init`
   2. `make runlego`
7. In the subsequent runs, only `make runlego` is needed.

## What can be done next?
- Use a better path planning algorithm
- Improve scalability to be able to run on bigger worlds
- Decouple `ObservedWorld`, `Planner` and `PathPlanner`
- Add touch and gyro sensors to the robot to help with orientation

<sup>1</sup>There is not so much Python 3.8 syntax. It should not be that
dificult to rewrite the program to Python 3.7 --- if you really want, feel free
to do so.

<sup>2</sup>Developed on (Arch) Linux. Not tested on different platforms.
