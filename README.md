<!-- PROJECT LOGO -->
<br />
<div align="center">
  <a href="https://github.com/Darkness9543/MultiboardDron">
    <img src="https://github.com/user-attachments/assets/bf5e483f-cd85-4912-9144-4a01aff85cf2" alt="Logo" width="200" height="200">
  </a>

  <h3 align="center">Multiboard</h3>

  <p align="center">
    <a href="https://drive.google.com/file/d/1UfWGkg3bQydWXyYSF6ncKXC_Mc4gH8ow/view">View Demo</a>
    ·
    <a href="https://drive.google.com/file/d/1cvNCRe-xUnqd8EoYJnYzz_gvoV45rG_i/view">View technical Demo</a>
  </p>
</div>

<!-- ABOUT THE PROJECT -->
## About The Project

Multiboard is an application made with Python integrated in the <a href="https://github.com/dronsEETAC/DroneEngineeringEcosystemDEE">Drone Engineering Ecosystem</a>, for the control and managment of multiple drones and scenarios. The scenarios are composed of geofences that are assigned to each corresponding drone and limits it's horizontal and vertical movement based on each geofence configuration. 

The main features are:
* A robust and easy to use scenario editor
* The ability to create both inclusion and exclusion geofences
* Drone parameter configuration and managment for multiple drones
* Drone control and monitoring for multiple drones
* Modular code structure



<!-- GETTING STARTED -->
## Getting Started

To replicate this project locally, you can use tools like <a href="https://git-scm.com/">Git</a>, which, once installed, allows you to quickly clone the repository by right clicking your work folder, and using `git bash`. This will open a command window for git instructions, where you can use the following command" to get it locally.
 ```sh
git clone %THIS_REPO_URL%
 ```

Once you have the code itself, continue by downloading <a href="https://ardupilot.org/planner/docs/mission-planner-installation.html">Mission Planner</a>, <a href="https://mosquitto.org/">Mosquitto</a> and setting up the work environment. I recommend using <a href="https://www.jetbrains.com/pycharm/download/?section=windows">Pycharm Community Edition</a>, which is completly free, and will be the one used from now on for the porpuses of this guide.
To set the environment, open the project and create a virtual environment or use a system interpreter based on the last Python version available (currently 3.13). Then proceed to download all the packages that are referenced in the project, by using: 
```sh
py -m pip install -r requirements.txt
```
If any packages are missing or you want to manage them, use the "Python Packages" section of Pycharm, that can be opened from the bottom left menu. Once all of them are installed, try to execute the program from the file `main.py` or by creating a pycharm configuration that does it for you. 

### Mosquitto
This will create a bridge to communicate with the drone. After installing mosquitto, go to the created folder for the program, and create a file named `mosquitto1884.conf` with the following: 
 ```sh
listener 1884
allow_anonymous true
 ```
Then, execute the mosquitto broker by opening a comand client in the same folder and executing:  
```sh
mosquitto -v -c mosquitto1884.conf
 ```

Production mode is for when you want to use actual drones, so it can be used anytime, provided you set up correctly all the ports (like COM) that you are going to use for each one.

If you want to simulate, you have to set up Mission Planner first.

### Mission Planner

Mission Planner is a tool that we will be using along this project for two main reasons:
* Will provide an interface to connect the real drones for calibration and validation porpuses
* Will allow us to perform simulations with multiple drones, check for their parameters and geofences, and debugging in general.
First let's discuss the tabs 
#### Data
This section will be used to move and control the drone. On The left submenu, the following sections can be selected:
  ##### &nbsp;&nbsp;&nbsp;&nbsp; Quick
  &nbsp;&nbsp;&nbsp;&nbsp; This tab will display the drones status, position, heading, etc.. once they are connected, either by simulation or using real drones.
  ##### &nbsp;&nbsp;&nbsp;&nbsp; Actions
  &nbsp;&nbsp;&nbsp;&nbsp; This allows to, after creating the done, do basic operations neededfor a mission, such as **Arm/ Disarm**, **RTL**, etc..

#### Plan
We won't use much this section, just note that you can change your "Home" point here, so everytime you start a simulation, your drones will spawn at that point.
To do so, just right click anywhere in the map and press "Set Home Here".
#### Setup
Used mainly to calibrate the GPS for the Drone when in production. 

This is not needed in Simulation and is necessary only if the drone flies in Loiter mode.
To calibrate just go to:
* Mandatory Hardware / Compass / Start   

Then start moving the drone in random directions (with your hands) to start calibrating.  Once the gauges are full, click Reboot.

#### Config
Here you can check or edit the current drone parameters. The current drone is selected in the top right corner, next to the DISCONNECT/CONNECT icon, using a dropdown menu. 

Mainly we will be using GeoFence, and Full Parameter List.
#### Simulation
To **create the aircraft** you can either start with a single drone, by clicking the "Multirotor" icon, or using the option "Copter Swarm - Multilink", and stating the number of drones. Each drone instance will open a command window that shows the connection IP:Port, in case you are not sure, altough the ones that come by default in the Multiboard are those by default in Mission Planner. It should be something like:
 ```sh
bind port XXXX for SERIALX
 ```
#### Map
Finally, on the map several **actions** can be performed using a right-click, such as "**Takeoff**" and "**Move here**", which will control the drone, which must be armed first (see Data). It is quite important to have some patience with Mission Planner, as it requires the sequence Arm -> Takeoff -> Move to be performed timely and in order. 

## Multiboard setup 
When you start the program, you should be met by the initial screen. You can create a scenario first, or proceed to connect the drones if you already have one. 

### Initial setup

<img src="https://github.com/user-attachments/assets/a92d372f-cbc4-4ce0-9b45-f9986170912d" width="700">

Here, you can choose the number of drones, their connection ports, the scenario and the connection method. A scenario is always required to poceed. 
When using a simulation, the port defined in MissionPlanner should be used, and when live the COM port used for the telemetry antenna must be written. 

### Connection
Here you can edit the parameters and limitations of each individual drone or share one configuration. This is also the moment to check that all drones are connected (green dot), and reconnect those who aren't. 

<img src="https://github.com/user-attachments/assets/cfd2ba57-46b7-4d9d-9e31-2d0a5e314bde" width="700">

### Control
This is the main view of the program. Here you can move the drones, see their positions and data and visualize their movements and geofences. 

<img src="https://github.com/user-attachments/assets/4e6bd428-9a81-4d08-a707-90c9a2c130db" width="700">

### Scenario editor
By navigating the left menu, you can access the editor. Here you can create and modify scenarios, by defining a geofence for each of the drones involved. Simply click on the map and create the shape that you desire. To close the polygon, you can either click on the original point or right-click and complete the geofence automatically. Once the inclusion geofence is done, you can follow the same procedure to create exclusion zones, like for exemple obstacles you want to avoid. Switch drones with the right-side list and create the geofence for every drone, then save and your scenario is ready to go!

<img src="https://github.com/user-attachments/assets/43a11abb-6846-4944-9721-5cc2f2962d03" width="700">


