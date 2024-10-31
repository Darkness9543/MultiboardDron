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

Multiboard is an application made with Python integrated in the <a href="https://github.com/dronsEETAC/DroneEngineeringEcosystemDEE">Drone Engineering Ecosystem</a>., for the control and managment of multiple drones and scenarios. The scenarios are composed of geofences that are assigned to each corresponding drone and limits it's horizontal and vertical movement based on each geofence configuration. 

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
To set the environment, open the project and create a virtual environment or use a system interpreter based on the last Python version available (At this time, 3.13). Then proceed to download all the packages that are referenced in the project, using the "Python Packages" section of Pycharm, that can be opened from the bottom left menu.  

Once all of them are installed, try to execute the program. 

### Mosquitto
This will create a bridge to communicate with the drone. After installing mosquitto, go to the folder where it is. There, create a file named `mosquitto1884.conf` with the follwing: 
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

<img src="??" width="700">

### Control
This is the main view of the program. Here you can move the drones, see their positions and data and visualize their movements and geofences. 
<img src="??" width="700">

### Scenario editor
By navigating the left menu, you can access the editor. Here you can create and modify scenarios, by defining a geofence for each of the drones involved. Simply click on the map and create he shape that you desire. To close the polygon, you can either click on the original point or right-click and complete the geofence automatically. Once the inclusion geofence is done, you can follow the same procedure to create exclusion zones, like for exemple obstacles you want to avoid. Switch drones with the right-side list and create the geofence for every drone, then save and your scenario is ready to go!

<img src="https://github.com/user-attachments/assets/43a11abb-6846-4944-9721-5cc2f2962d03" width="700">



### Installation

_Below is an example of how you can instruct your audience on installing and setting up your app. This template doesn't rely on any external dependencies or services._

1. Get a free API Key at [https://example.com](https://example.com)
2. Clone the repo
   ```sh
   git clone https://github.com/github_username/repo_name.git
   ```
3. Install NPM packages
   ```sh
   npm install
   ```
4. Enter your API in `config.js`
   ```js
   const API_KEY = 'ENTER YOUR API';
   ```
5. Change git remote url to avoid accidental pushes to base project
   ```sh
   git remote set-url origin github_username/repo_name
   git remote -v # confirm the changes
   ```

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- USAGE EXAMPLES -->
## Usage

Use this space to show useful examples of how a project can be used. Additional screenshots, code examples and demos work well in this space. You may also link to more resources.

_For more examples, please refer to the [Documentation](https://example.com)_

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- ROADMAP -->
## Roadmap

- [x] Add Changelog
- [x] Add back to top links
- [ ] Add Additional Templates w/ Examples
- [ ] Add "components" document to easily copy & paste sections of the readme
- [ ] Multi-language Support
    - [ ] Chinese
    - [ ] Spanish

See the [open issues](https://github.com/othneildrew/Best-README-Template/issues) for a full list of proposed features (and known issues).

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- CONTRIBUTING -->
## Contributing

Contributions are what make the open source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

If you have a suggestion that would make this better, please fork the repo and create a pull request. You can also simply open an issue with the tag "enhancement".
Don't forget to give the project a star! Thanks again!

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Top contributors:

<a href="https://github.com/othneildrew/Best-README-Template/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=othneildrew/Best-README-Template" alt="contrib.rocks image" />
</a>

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- LICENSE -->
## License

Distributed under the MIT License. See `LICENSE.txt` for more information.

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- CONTACT -->
## Contact

Your Name - [@your_twitter](https://twitter.com/your_username) - email@example.com

Project Link: [https://github.com/your_username/repo_name](https://github.com/your_username/repo_name)

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- ACKNOWLEDGMENTS -->
## Acknowledgments

Use this space to list resources you find helpful and would like to give credit to. I've included a few of my favorites to kick things off!

* [Choose an Open Source License](https://choosealicense.com)
* [GitHub Emoji Cheat Sheet](https://www.webpagefx.com/tools/emoji-cheat-sheet)
* [Malven's Flexbox Cheatsheet](https://flexbox.malven.co/)
* [Malven's Grid Cheatsheet](https://grid.malven.co/)
* [Img Shields](https://shields.io)
* [GitHub Pages](https://pages.github.com)
* [Font Awesome](https://fontawesome.com)
* [React Icons](https://react-icons.github.io/react-icons/search)

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
[contributors-shield]: https://img.shields.io/github/contributors/othneildrew/Best-README-Template.svg?style=for-the-badge
[contributors-url]: https://github.com/othneildrew/Best-README-Template/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/othneildrew/Best-README-Template.svg?style=for-the-badge
[forks-url]: https://github.com/othneildrew/Best-README-Template/network/members
[stars-shield]: https://img.shields.io/github/stars/othneildrew/Best-README-Template.svg?style=for-the-badge
[stars-url]: https://github.com/othneildrew/Best-README-Template/stargazers
[issues-shield]: https://img.shields.io/github/issues/othneildrew/Best-README-Template.svg?style=for-the-badge
[issues-url]: https://github.com/othneildrew/Best-README-Template/issues
[license-shield]: https://img.shields.io/github/license/othneildrew/Best-README-Template.svg?style=for-the-badge
[license-url]: https://github.com/othneildrew/Best-README-Template/blob/master/LICENSE.txt
[linkedin-shield]: https://img.shields.io/badge/-LinkedIn-black.svg?style=for-the-badge&logo=linkedin&colorB=555
[linkedin-url]: https://linkedin.com/in/othneildrew
[product-screenshot]: images/screenshot.png
[Next.js]: https://img.shields.io/badge/next.js-000000?style=for-the-badge&logo=nextdotjs&logoColor=white
[Next-url]: https://nextjs.org/
[React.js]: https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB
[React-url]: https://reactjs.org/
[Vue.js]: https://img.shields.io/badge/Vue.js-35495E?style=for-the-badge&logo=vuedotjs&logoColor=4FC08D
[Vue-url]: https://vuejs.org/
[Angular.io]: https://img.shields.io/badge/Angular-DD0031?style=for-the-badge&logo=angular&logoColor=white
[Angular-url]: https://angular.io/
[Svelte.dev]: https://img.shields.io/badge/Svelte-4A4A55?style=for-the-badge&logo=svelte&logoColor=FF3E00
[Svelte-url]: https://svelte.dev/
[Laravel.com]: https://img.shields.io/badge/Laravel-FF2D20?style=for-the-badge&logo=laravel&logoColor=white
[Laravel-url]: https://laravel.com
[Bootstrap.com]: https://img.shields.io/badge/Bootstrap-563D7C?style=for-the-badge&logo=bootstrap&logoColor=white
[Bootstrap-url]: https://getbootstrap.com
[JQuery.com]: https://img.shields.io/badge/jQuery-0769AD?style=for-the-badge&logo=jquery&logoColor=white
[JQuery-url]: https://jquery.com 