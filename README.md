# **PitStop - F1 Race Stats Dashboard**

#### **Video Demo:** [PITSTOP Demo Youtube Video](https://youtu.be/dJKMSVy7hAI)

## **Description:**

### **Project Overview:**

**PitStop** is a Python-based application that provides Formula 1 fans with detailed driver statistics, upcoming race schedules, and a viewing of race timings particular to their local time zones. It connects to a public F1 API to fetch real-time data, including driver information, race schedules, and historical and current team details.

### **Features**:

- **menu()** function displays list of main options for user to select the required or desired task they want to perform.
menu() offers user to select from
- Race Schedule: *(based on user entered specific timezone)* Displays Upcoming races schecule in ascending order and past races schedule in descending order followed by a call to **sub_menu()**
- Race Statistics *(which further divides into)*
    - Team Ranking :        *Showing current/previous team ranking stats.*
    - Driver Ranking:       *Showing current/previous driver ranking stats*
    - Race Result:          *Displaying race result of user selected grand prix race*
    - Fastest-Lap Time:     *Fastest lap time in the user selected grand prix race*
    - Starting Grid:        *Showing the starting grid based on qualifying time of the user selected grand prix race*
    - Return to Menu        *Returns user to Main Menu*
- General Queries *(which further divides into)*
    - Countdown:            *Displays date and time and some other details about upcoming races*
    - Circuit Overview:     *Displaying details of user selected circuit*
    - Team Profile:         *Displaying details of user selected team*
    - Driver Credentials:   *Displaying details of user selected driver*
    - Return to Menu:       *Returns user to Main Menu*

- **sub_menu()** used after every functionality to be called for allowing user to either return to main menu or exit the program.
- **clear_screen()** used to clear the terminal screen.
- **conversion_to_localtime()** used to convert the api called time to user input continent/city time.
- **fetch_timezones()** used to fetch continents and cities to be selected from by the user.
- **fetch_races()** used to fetch race data of particular user input season.
- **fetch_driver_info** used to fetch driver information

**Highlights:**
- View detailed information about F1 drivers, including podium finishes, championships, and career history.
- Get the upcoming F1 race schedule converted to your local timezone.
- Lists drivers currently participating in the F1 season with their credentials.
- Display driver teams by season for more in-depth career analysis.

### Technologies Used:

- **Python:** Main programming language.
- **Rich:** For creating a colorful and user-friendly console interface.
- **Pyfiglet:** For rendering stylish text banners.
- **Pytz:** For handling time zone conversions.
- **Requests:** For making API calls to the F1 API.

### Setup and Installation:

## **Prerequisites:**
Ensure you have Python 3.x installed on your system.

## **Install the required libraries:**

In the root directory of the project, run:

*pip install -r requirements.txt*

Set up the F1 API key: You will need to get an API key from [API-Sports Formula 1 API](https://dashboard.api-football.com). Once you have the key, add it to your environment variables or directly in the code.

## **Usage:**
Run the following command to start the application:

*python project.py*

## **Testing:**
The project includes a tests directory with sample test cases using pytest.
To run the tests:

*pytest test_project.py*

## **Project Structure**

- project/
    - project.py             *Main application logic*
    - requirements.txt       *Required Python libraries*
    - test_project.py        *Test cases for the project*
    - README.md              *Project documentation*

## **Required Libraries**
Listed in **requirements.txt**:

- tqdm
- requests
- rich
- pytz
- pyfiglet
- pytest


## Author:
**Saad Ahmed**

