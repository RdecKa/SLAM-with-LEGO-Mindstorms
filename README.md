# SLAM with LEGO Mindstorms
A system that helps a robot exploring the world. By collecting measurements
from the robot's sensors and telling the robot where to go next it constructs a
map of the world.

The robot can be either a real LEGO Mindstorms robot or a simulated one. It
is easier to develop the logic using the simulated robot but it is much more
fun observing a phisical robot wandering around.

## Examples
The GIFs below show two examples - one simulated and one with the LEGO robot.

Explanation of the maps:

- Red dots and the solid black line: Position of the robot through time
- Gray circle around the red dots: The size of the robot
- Orange dots and the black dashed line: Planned path
- Blue dots: Detected obstacles
- Light green dots: Detected free spots (the sensor has a limited view and
  can't see an obstacle further than that)
- Dark green dots: Possible locations to continue exploration
- Blue cells in the grid: Expected obstacle positions
- Brown cells in the grid: Expected free positions

### Simulated robot
![Example of a simulated robot](docs/img/example_simulated.gif)

### LEGO Mindstorms robot
TODO

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

### But I have a LEGO Mindstorms and I want to see it in action!
TODO

## What can be done next?
- Use a better path planning algorithm
- Improve scalability to be able to run on bigger worlds
- Decouple `ObservedWorld`, `Planner` and `PathPlanner`
- Add touch and gyro sensors to the robot to help with orientation

<sup>1</sup>There is not so much Python 3.8 syntax. It should not be that
dificult to rewrite the program to Python 3.7 --- if you really want, feel free
to do so.

<sup>2</sup>Developed on (Arch) Linux. Not tested on different platforms.
