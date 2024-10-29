import time
import random
from datetime import datetime
import tqdm
import sys
import os
import requests
from rich import console, table, progress
import pytz
from pyfiglet import Figlet
from dotenv import load_dotenv 

load_dotenv()

api_key = os.getenv("API_KEY")
api_url = os.getenv("API_URL")

payload = {}
headers = {
    'x-rapidapi-key': api_key,
    'x-rapidapi-host': 'v1.formula-1.api-sports.io'
}

console_ = console.Console()
figlet = Figlet()
figlet.setFont(font='speed')

def clear_screen():
    if os.name == 'nt':  
        os.system('cls')
    else:  
        os.system('clear')


def main():
    clear_screen()
    console_.print("[bold magenta]🟢 🟡 🔴 Welcome to [/bold magenta]")
    console_.print(figlet.renderText("Pitstop!"))
    time.sleep(6)

    with progress.Progress() as progress_:
        task = progress_.add_task("[cyan]Loading...", total=100)
        while not progress_.finished:
            progress_.update(task, advance=random.randint(1,5))
            time.sleep(random.uniform(0.1, 0.3))

    console_.print("[bold green]The application is ready![/bold green]")
    time.sleep(2)
    menu()

def menu():
    clear_screen()
    try:
        table_ = table.Table(title="\n[yellow]Main Menu")
        table_.add_column("[bold white]Option", justify="center", style="cyan", no_wrap=True)
        table_.add_column("[bold white]Description", justify="center", style="green", no_wrap=True)

        table_.add_row("1", "Race Schedule")
        table_.add_row("2", "Race Statistics")
        table_.add_row("3", "General Queries")
        table_.add_row("4", "Exit")

        console_.print(table_)

        choice = int(input("Input your choice: ").strip())

        match choice:
            case 1:
                race_schedule()
            case 2:
                race_statistics()
            case 3:
                general_queries()
            case 4:
                with console_.status("[bold green]Exiting...", spinner="dots3"):
                    time.sleep(3)
                    clear_screen()
                sys.exit()
            case _:
                console_.log("[bold red]Invalid option selected! Please choose a valid option.[/bold red]")
                time.sleep(2)
                menu()
    except ValueError:
        console_.print("[bold red]Please enter a valid option number.[/bold red]")
        time.sleep(2)
        menu()

def sub_menu():
    while True:
        try:
            opt = int(console_.input("[bold cyan]Select:[/bold cyan]\n[bold green]1.Return to Menu[/bold green]\t\t[bold red]2.Exit[/bold red]\n"))

            if opt == 1:
                with console_.status(f"[italic cyan]Returning to Menu [/italic cyan]", spinner="dots3"):
                    time.sleep(3)
                menu()
                break
            elif opt == 2:
                with console_.status("[bold green]Exiting...", spinner="dots3"):
                    time.sleep(3)
                    clear_screen()
                sys.exit()
            else:
                console_.print("[bold red]Invalid input! Please enter 1 or 2.[/bold red]")
                time.sleep(2)
        except ValueError:
            console_.print("[bold red]Please enter a valid option number.[/bold red]")
            time.sleep(2)

def conversion_to_localtime(utc_time, user_timezone):
    utc_time = datetime.fromisoformat(utc_time.replace("Z", "+00:00"))
    local_zone = pytz.timezone(user_timezone)
    local_dt = utc_time.astimezone(local_zone)
    return local_dt.strftime("%d-%m-%Y %H:%M")

def fetch_timezones():
    url = f"{api_url}/timezone"
    headers = {
        'x-rapidapi-key': 'c13e1dd3151559298a27890618f515d9',
        'x-rapidapi-host': 'v1.formula-1.api-sports.io'
    }

    try:
        response = requests.request("GET", url, headers=headers)
        response.raise_for_status()

        data = response.json()
        if data.get('errors') and 'requests' in data['errors']:
                    raise requests.exceptions.RequestException

        timezones = data.get('response', [])

        structured_timezones = {}
        for tz in timezones:
            continent, city = tz.split('/',1)
            if continent not in structured_timezones:
                structured_timezones[continent] = []
            structured_timezones[continent].append(city)

        return structured_timezones

    except requests.exceptions.RequestException as e:
        console_.print(f"[bold red]Error fetching timezones...⛓️‍💥[/bold red]")
        time.sleep(2)
        sub_menu()


def fetch_races(season, selected_index = None):
    url = f"{api_url}/races?season={season}"

    try:
        race_id = None
        race_name = None
        response = requests.request(
            "GET", url, headers=headers, data=payload)
        response.raise_for_status()

        data = response.json()
        if data.get('errors') and 'requests' in data['errors']:
            raise requests.exceptions.RequestException()

        sorted_race = sorted(
            [race for race in data.get('response', [])
             if (datetime.fromisoformat(race['date']).replace(tzinfo=None) < datetime.now().replace(tzinfo=None)) and race['type'] == 'Race'],
            key=lambda race: datetime.fromisoformat(race['date'])
        )

        if len(sorted_race) == 0:
            raise requests.exceptions.RequestException("No races found for the season.")

        console_.print(f"[bold magenta]Displaying races of the season {season}:[/bold magenta]")

        race_table = table.Table(
            title="[yellow]Season Races", show_lines=True)

        race_table.add_column(
            "[bold white]Index", justify="center", style="cyan", no_wrap=True)
        race_table.add_column(
            "[bold white]Race", justify="center", style="green", no_wrap=True)
        race_table.add_column(
            "[bold white]Date", justify="center", style="magenta", no_wrap=True)

        index = 1
        for race in sorted_race:
            race_name = race['competition']['name']
            race_date_obj = datetime.fromisoformat(race['date'].replace('Z', '+00:00'))
            race_date = race_date_obj.strftime("%d-%m-%Y")
            race_id = str(race['id'])

            race_table.add_row(str(index), race_name, race_date)

            index += 1

        console_.print(race_table)

        if selected_index is None:
            selected_index = int(input("Enter the index of the race you want to see details for: "))
        else:
            selected_index = 1

        if 1 <= selected_index <= len(sorted_race):
            selected_race = sorted_race[selected_index - 1]
            race_id = selected_race['id']
            race_name = selected_race['competition']['name']  # Assign race_name here

        else:
            raise UnboundLocalError("Invalid race index selected.")

        return race_id, race_name

    except requests.exceptions.RequestException as e:
        console_.print(f"[bold red]Error fetching races data: {e}[/bold red]")
        time.sleep(2)
        sub_menu()
    except (KeyError, UnboundLocalError):
        console_.print(f"[bold red]Race ID not Found![/bold red]")
        time.sleep(2)
        sub_menu()
    except (ValueError, IndexError, requests.exceptions.RequestException) as e:
        console_.print(f"[bold red]Error fetching races data: {e}[/bold red]")
        time.sleep(2)
        sub_menu()



def fetch_driver_info(driver_id):
    url1 = f"{api_url}/drivers?id={driver_id}"

    try:
        response = requests.request("GET", url1, headers=headers)
        response.raise_for_status()
        data = response.json()
        '''        if data.get('errors') and 'requests' in data['errors']:
                    raise requests.exceptions.RequestException'''

        driver_details = data.get('response', [])

        if driver_details:
            driver_info = driver_details[0]
            console_.print(f"[magenta]Driver Name: [bold]{driver_info['name']}")
            console_.print(f"[green]Nationality: [bold]{driver_info['nationality']}")
            console_.print(f"[green]Birthdate: [bold]{driver_info['birthdate']}")
            console_.print(f"[green]Podiums: [bold]{driver_info['podiums']}")
            console_.print(f"[green]World Championships: [bold]{driver_info['world_championships']}")
            teams_by_season = []
            for team in driver_info['teams']:
                season = team['season']
                team_name = team['team']['name']
                teams_by_season.append(f"Season: {season} - Team: {team_name}")
            console_.print(f"[green]Teams by seasons: \n[bold]{'\n'.join(teams_by_season)}")

    except requests.exceptions.RequestException as e:
        console_.print(f"[bold red]Error fetching race schedule...⛓️‍💥[/bold red]")
        time.sleep(2)
    except KeyError:
        console_.print("[bold red]Unexpected data format from API...🚨[/bold red]")
        time.sleep(2)

    sub_menu()


def race_schedule():

    while True:
        clear_screen()
        season = int(console_.input("Enter the Year of Season [bold red][2012 onwards][/bold red]: ").strip())
        if season < 2012 or season > datetime.now().year:
            console_.print("Sorry No data available before 2012 and after current Year.")
            sub_menu()

        url = f"{api_url}/races?season={season}"

        timezones = fetch_timezones()
        if not timezones:
            console_.print(f"[bold red]Could not fetch timezones.[/bold red]")
            time.sleep(2)
            sub_menu()

        console_.print(f"[bold magenta]Available timezones: [/bold magenta]")
        for continent in timezones.keys():
            console_.print(f"{continent}")

        selected_tz = input("\nSelect your timezone continent: ").strip().title()
        if selected_tz not in timezones:
            console_.print("[bold red]Invalid selection![/bold red]")
            time.sleep(2)
            continue

        console_.print(f"[bold magenta]Available cities in {selected_tz}: [/bold magenta]")
        for city in timezones[selected_tz]:
            console_.print(city)

        selected_city = input("\nSelect your timezone city: ").strip().title()
        if selected_city not in timezones[selected_tz]:
            console_.print("[bold red]Invalid city selection![/bold red]")
            time.sleep(2)
            continue

        break

    user_timezone = f"{selected_tz}/{selected_city}"

    try:
        response = requests.request("GET", url, headers=headers, data=payload)
        response.raise_for_status()

        data = response.json()

        if data.get('errors') and 'requests' in data['errors']:
            raise requests.exceptions.RequestException

        with console_.status(f"[italic cyan]Fetching data for timezone: [/italic cyan] '{selected_tz}/{selected_city}'", spinner="dots3"):
            time.sleep(4)

        clear_screen()

        console_.print("[bold magenta]Race Schedule:[/bold magenta]")
        #print(json.dumps(data, indent=2))


        sorted_races = sorted([race for race in data.get('response', [])
                               if (datetime.fromisoformat(race['date']).replace(tzinfo=None) > datetime.now().replace(tzinfo=None))],
                        key=lambda race: datetime.fromisoformat(race['date']))

        if sorted_races:

            race_table = table.Table(title="[yellow]Upcoming Races", show_lines=True)

            race_table.add_column("[bold white]Race", justify="center", style="cyan", no_wrap=True)
            race_table.add_column("[bold white]Circuit", justify="center", style="green", no_wrap=True)
            race_table.add_column("[bold white]Race Type",  justify="center", style="blue", no_wrap=True)
            race_table.add_column("[bold white]Date/Time", justify="center", style="magenta", no_wrap=True)


            #data.get('response', []), key=lambda race: datetime.fromisoformat(race['date']))
            for race in sorted_races:
                race_name = race['competition']['name']
                circuit_name = race['circuit']['name']
                type_race = race['type']
                race_date = race['date']

                local_race_time = conversion_to_localtime(race_date, user_timezone)

                race_table.add_row(race_name, circuit_name, type_race, local_race_time)

            console_.print(race_table)


        race_table2 = table.Table(title="[yellow]Past Races", show_lines=True)

        race_table2.add_column("[bold white]Race", justify="center", style="cyan", no_wrap=True)
        race_table2.add_column("[bold white]Circuit", justify="center", style="green", no_wrap=True)
        race_table2.add_column("[bold white]Race Type",  justify="center", style="blue", no_wrap=True)
        race_table2.add_column("[bold white]Date/Time", justify="center", style="magenta", no_wrap=True)


        sorted_races2 = sorted([race for race in data.get('response', [])
                                if (datetime.fromisoformat(race['date']).replace(tzinfo=None) < datetime.now().replace(tzinfo=None))],
                    key=lambda race: datetime.fromisoformat(race['date']), reverse = True)

        for race in sorted_races2:
            race_name = race['competition']['name']
            circuit_name = race['circuit']['name']
            type_race = race['type']
            race_date = race['date']

            local_race_time = conversion_to_localtime(race_date, user_timezone)

            race_table2.add_row(race_name, circuit_name, type_race, local_race_time)

        console_.print(race_table2)

    except requests.exceptions.RequestException as e:
        console_.print(f"[bold red]Error fetching race schedule...⛓️‍💥[/bold red]")
        time.sleep(2)
    except KeyError:
        console_.print("[bold red]Unexpected data format from API...🚨[/bold red]")
        time.sleep(2)

    sub_menu()


def race_statistics():
    clear_screen()

    '''
    1.ranking of teams              -> season
    2.ranking of drivers            -> season
    3.ranking in race               -> race id
    4.ranking fastest lap           -> race id
    5.starting grid                 -> race id
    '''
    console_.print("[bold magenta]Choose from the options:[/bold magenta]")
    table_1 = table.Table(title="\n[yellow]Race Statistics")

    table_1.add_column("[bold white]Option[/bold white]", justify="center", style="cyan", no_wrap=True)
    table_1.add_column("[bold white]Description[/bold white]", justify="center", style="green", no_wrap=True)

    table_1.add_row("1", "Team Ranking")
    table_1.add_row("2", "Driver Ranking")
    table_1.add_row("3", "Race Results")
    table_1.add_row("4", "Fastest-Lap Time")
    table_1.add_row("5", "Starting Grid")
    table_1.add_row("6", "Return to Menu")

    console_.print(table_1)

    choice = int(input("Input your choice: ").strip())
    clear_screen()

    match choice:
        case 1: #Team Ranking
            season = int(console_.input("Enter the Year of Season [bold red][2012 onwards][/bold red]: ").strip())
            if season < 2012 or season > datetime.now().year:
                console_.print("Sorry  No data available before 2012 and after current Year..")
                sub_menu()

            url = f"{api_url}/rankings/teams?season={season}"

            try:
                response = requests.request("GET", url, headers=headers, data=payload)
                response.raise_for_status()

                data = response.json()
                if data.get('errors') and 'requests' in data['errors']:
                    raise requests.exceptions.RequestException

                console_.print(f"[bold magenta]Team Ranking for {season}:[/bold magenta]")
                # print(json.dumps(data, indent=2))

                pos_table = table.Table(title="[yellow]Team Ranking", show_lines=True)

                pos_table.add_column("[bold white]Position", justify="center", style="cyan", no_wrap=True)
                pos_table.add_column("[bold white]Team", justify="center", style="green", no_wrap=True)
                pos_table.add_column("[bold white]Points",  justify="center", style="magenta", no_wrap=True)

                sorted_position = sorted(data.get('response', []), key=lambda race: race['position'])
                for race in sorted_position:
                    team_pos =str(race['position'])
                    team_name = race['team']['name']
                    team_points = str(race['points'])

                    pos_table.add_row(team_pos, team_name, team_points)

                console_.print(pos_table)
            except requests.exceptions.RequestException as e:
                console_.print(
                    f"[bold red]Error fetching team rankings...⛓️‍💥[/bold red]")
                time.sleep(2)
            except KeyError:
                console_.print("[bold red]Unexpected data format from API...🚨[/bold red]")
                time.sleep(2)

            sub_menu()


        case 2: #Driver Ranking
            season = int(console_.input("Enter the Year of Season [bold red][2012 onwards][/bold red]: ").strip())
            if season < 2012 or season > datetime.now().year:
                console_.print("Sorry  No data available before 2012 and after current Year..")
                sub_menu()
            url = f"{api_url}/rankings/drivers?season={season}"

            try:
                response = requests.request("GET", url, headers=headers, data=payload)
                response.raise_for_status()

                data = response.json()
                if data.get('errors') and 'requests' in data['errors']:
                    raise requests.exceptions.RequestException

                console_.print(f"[bold magenta]Driver Ranking for {season}:[/bold magenta]")
                # print(json.dumps(data, indent=2))

                pos_table = table.Table(title="[yellow]Driver Ranking", show_lines=True)

                pos_table.add_column("[bold white]Position", justify="center", style="cyan", no_wrap=True)
                pos_table.add_column("[bold white]Driver Name", justify="center", style="green", no_wrap=True)
                pos_table.add_column("[bold white]Team Name",  justify="center", style="blue", no_wrap=True)
                pos_table.add_column("[bold white]Points", justify="center", style="magenta", no_wrap=True)
                pos_table.add_column("[bold white]Wins",  justify="center", style="purple", no_wrap=True)


                sorted_driver_position = sorted(data.get('response', []), key=lambda race: race['position'])
                for race in sorted_driver_position:
                    driver_pos = str(race['position'])
                    driver_name = race['driver']['name']
                    team_name = race['team']['name']
                    driver_points = str(race['points'])
                    driver_wins = str(race['wins'])

                    pos_table.add_row(driver_pos, driver_name, team_name, driver_points, driver_wins)

                console_.print(pos_table)

            except requests.exceptions.RequestException as e:
                console_.print(
                    f"[bold red]Error fetching driver rankings...⛓️‍💥[/bold red]")
                time.sleep(2)
            except KeyError:
                console_.print(
                    "[bold red]Unexpected data format from API...🚨[/bold red]")
                time.sleep(2)
            sub_menu()

        case 3: #Race Results
            season = int(console_.input("Enter the Year of Season [bold red][2012 onwards][/bold red]: ").strip())
            if season < 2012 or season > datetime.now().year:
                console_.print("Sorry  No data available before 2012 and after current Year..")
                sub_menu()

            race_id, race_name = fetch_races(season)

            url = f"{api_url}/rankings/races?race={race_id}"

            try:
                response = requests.request(
                    "GET", url, headers=headers, data=payload)
                response.raise_for_status()

                data = response.json()
                if data.get('errors') and 'requests' in data['errors']:
                    raise requests.exceptions.RequestException

                console_.print(f"[bold magenta]Displaying race result of {race_name}:[/bold magenta]")
                # print(json.dumps(data, indent=2))

                result_table = table.Table(
                    title= f"[yellow]Race Results", show_lines=True)

                result_table.add_column(
                    "[bold white]Position", justify="center", style="cyan", no_wrap=True)
                result_table.add_column(
                    "[bold white]Driver", justify="center", style="green", no_wrap=True)
                result_table.add_column(
                    "[bold white]Team", justify="center", style="blue", no_wrap=True)
                result_table.add_column(
                    "[bold white]Time", justify="center", style="magenta", no_wrap=True)

                races = data.get('response', [])
                for race in races:
                    driver_pos = str(race['position'])
                    driver_name = race['driver']['name']
                    team_name = race['team']['name']
                    driver_time = race['time']

                    result_table.add_row(driver_pos, driver_name, team_name, driver_time)

                console_.print(result_table)

            except requests.exceptions.RequestException as e:
                console_.print(
                    f"[bold red]Error fetching result of race...⛓️‍💥[/bold red]")
                time.sleep(2)
            except KeyError:
                console_.print(
                    "[bold red]Unexpected data format from API...🚨[/bold red]")
                time.sleep(2)
            sub_menu()

        case 4: #Fastest-Lap Time
            season = int(console_.input("Enter the Year of Season [bold red][2012 onwards][/bold red]: ").strip())
            if season < 2012 or season > datetime.now().year:
                console_.print("Sorry  No data available before 2012 and after current Year..")
                sub_menu()

            race_id, race_name = fetch_races(season)

            url = f"{api_url}/rankings/fastestlaps?race={race_id}"

            try:
                response = requests.request(
                    "GET", url, headers=headers, data=payload)
                response.raise_for_status()

                data = response.json()
                if data.get('errors') and 'requests' in data['errors']:
                    raise requests.exceptions.RequestException

                console_.print(f"[bold magenta]Displaying race result of {race_name}:[/bold magenta]")
                # print(json.dumps(data, indent=2))

                fastlap_table = table.Table(
                    title=f"[yellow]Fastest Lap Results", show_lines=True)

                fastlap_table.add_column(
                    "[bold white]Ranking", justify="center", style="cyan", no_wrap=True)
                fastlap_table.add_column(
                    "[bold white]Driver", justify="center", style="green", no_wrap=True)
                fastlap_table.add_column(
                    "[bold white]Team", justify="center" , style="blue", no_wrap=True)
                fastlap_table.add_column(
                    "[bold white]Fastest Time", justify="center", style="magenta", no_wrap=True)

                races = data.get('response', [])
                for race in races:
                    driver_pos = str(race['position'])
                    driver_name = race['driver']['name']
                    team_name = race['team']['name']
                    driver_time = race['time']

                    fastlap_table.add_row(driver_pos, driver_name, team_name, driver_time)

                console_.print(fastlap_table)

            except requests.exceptions.RequestException as e:
                console_.print(
                    f"[bold red]Error fetching fastest lap data of race...⛓️‍💥[/bold red]")
                time.sleep(2)
            except KeyError:
                console_.print(
                    "[bold red]Unexpected data format from API...🚨[/bold red]")
                time.sleep(2)
            sub_menu()

        case 5: #Starting Grid
            season = int(console_.input("Enter the Year of Season [bold red][2012 onwards][/bold red]: ").strip())
            if season < 2012 or season > datetime.now().year:
                console_.print("Sorry  No data available before 2012 and after current Year..")
                sub_menu()

            race_id, race_name = fetch_races(season)

            url = f"{api_url}/rankings/startinggrid?race={race_id}"

            try:
                response = requests.request(
                    "GET", url, headers=headers, data=payload)
                response.raise_for_status()

                data = response.json()
                if data.get('errors') and 'requests' in data['errors']:
                    raise requests.exceptions.RequestException

                console_.print(f"[bold magenta]Displaying race result of {race_name}:[/bold magenta]")
                # print(json.dumps(data, indent=2))

                startgrid_table = table.Table(
                    title=f"[yellow]Starting Grid Results", show_lines=True)

                startgrid_table.add_column(
                    "[bold white]Position", justify="center", style="cyan", no_wrap=True)
                startgrid_table.add_column(
                    "[bold white]Driver", justify="center", style="green", no_wrap=True)
                startgrid_table.add_column(
                    "[bold white]Team", justify="center", style="blue", no_wrap=True)
                startgrid_table.add_column(
                    "[bold white]Best Qualify Time", justify="center", style="magenta", no_wrap=True)

                races = data.get('response', [])
                for race in races:
                    driver_pos = str(race['position'])
                    driver_name = race['driver']['name']
                    team_name = race['team']['name']
                    driver_time = race['time'] if race['time'] is not None else "DNF"

                    startgrid_table.add_row(
                        driver_pos, driver_name, team_name, driver_time)

                console_.print(startgrid_table)

            except requests.exceptions.RequestException as e:
                console_.print(
                    f"[bold red]Error fetching fastest lap data of race...⛓️‍💥[/bold red]")
                time.sleep(2)
            except KeyError:
                console_.print(
                    "[bold red]Unexpected data format from API...🚨[/bold red]")
                time.sleep(2)
            sub_menu()

        case 6: #Return to Menu
            with console_.status(f"[italic cyan]Returning to Menu [/italic cyan]", spinner="dots3"):
                time.sleep(4)
            menu()
        case _:
            console_.print("[bold red]Invalid option selection![/bold red]")
            time.sleep(2)
            sub_menu()

def general_queries():
    clear_screen()
    '''
    1.next race
    2.circuit
    3.team
    4.driver
    '''
    console_.print("[bold magenta]Choose from the options:[/bold magenta]")

    table_option = table.Table(title="\n[yellow]General Queries")

    table_option.add_column("[bold white]Option[/bold white]",
                       justify="center", style="cyan", no_wrap=True)
    table_option.add_column("[bold white]Description[/bold white]",
                       justify="center", style="green", no_wrap=True)

    table_option.add_row("1", "Countdown")
    table_option.add_row("2", "Circuit Overview")
    table_option.add_row("3", "Team Profile")
    table_option.add_row("4", "Driver Credentials")
    table_option.add_row("5", "Return to Menu")

    console_.print(table_option)

    choice = int(input("Input your choice: ").strip())

    match choice:
        case 1: #Countdown
            clear_screen()
            season = datetime.now().year
            url = f"{api_url}/races?season={season}"

            while True:
                timezones = fetch_timezones()
                if not timezones:
                    console_.print(f"[bold red]Could not fetch timezones.[/bold red]")
                    time.sleep(2)
                    sub_menu()

                console_.print(f"[bold magenta]Available timezones: [/bold magenta]")
                for continent in timezones.keys():
                    console_.print(f"{continent}")

                selected_tz = input("\nSelect your timezone continent: ").strip().title()
                if selected_tz not in timezones:
                    console_.print("[bold red]Invalid selection![/bold red]")
                    time.sleep(2)
                    continue

                console_.print(f"[bold magenta]Available cities in {selected_tz}: [/bold magenta]")
                for city in timezones[selected_tz]:
                    console_.print(city)

                selected_city = input("\nSelect your timezone city: ").strip().title()
                if selected_city not in timezones[selected_tz]:
                    console_.print("[bold red]Invalid city selection![/bold red]")
                    time.sleep(2)
                    continue

                break

            user_timezone = f"{selected_tz}/{selected_city}"

            try: #hellochanges
                response = requests.request("GET", url, headers=headers, data=payload)
                response.raise_for_status()

                data = response.json()
                if data.get('errors') and 'requests' in data['errors']:
                    raise requests.exceptions.RequestException

                with console_.status(f"[italic cyan]Fething data for timezone: [/italic cyan] '{selected_tz}/{selected_city}'", spinner="dots3"):
                    time.sleep(3)

                clear_screen()

                console_.print("[bold magenta]Race Countdown:[/bold magenta]")
                # print(json.dumps(data, indent=2))

                countdown_table = table.Table(title="[yellow]Countdown to Next Races", show_lines=True)

                countdown_table.add_column("[bold white]Index", justify="center", style="cyan", no_wrap=True)
                countdown_table.add_column("[bold white]Race", justify="center", style="green", no_wrap=True)
                '''countdown_table.add_column("Circuit", justify="center", style="green")
                countdown_table.add_column("Race Type", justify="center", style="white")
                countdown_table.add_column("Date/Time", justify="center", style="magenta")'''

                sorted_races = sorted(
                    [race for race in data.get('response', []) if (datetime.fromisoformat(race['date']).replace(tzinfo=None) > datetime.now().replace(tzinfo=None) and race['type'] == 'Race')],
                    key=lambda race: datetime.fromisoformat(race['date'])
                )

                index = 1
                for race in sorted_races:
                    race_name = race['competition']['name']
                    race_date = race['date']
                    '''
                    circuit_name = race['circuit']['name']
                    type_race = race['type']
                    '''
                    local_race_time = conversion_to_localtime(race_date, user_timezone)

                    countdown_table.add_row(str(index), race_name)

                    index += 1

                console_.print(countdown_table)

                selected_index = int(input("Enter the index of the race you want to see details for: "))

                if 1 <= selected_index <= len(sorted_races):
                    selected_race = sorted_races[selected_index - 1]

                    race_name = selected_race['competition']['name']
                    circuit_name = selected_race['circuit']['name']
                    race_date = selected_race['date']
                    local_race_time = conversion_to_localtime(race_date, user_timezone)

                    # Print detailed info about the selected race
                    console_.print(f"\n[magenta]Details for: [bold]{race_name}")
                    console_.print(f"[green]Circuit: [bold]{circuit_name}")
                    console_.print(f"[green]Date/Time: [bold]{local_race_time}")
                    local_race_time = datetime.strptime(local_race_time, "%d-%m-%Y %H:%M")
                    current_time = datetime.now()
                    diff = local_race_time - current_time
                    console_.print(f"[green]Time Left: [bold]{diff}")
                else:
                    console_.print("[bold red]Invalid index. Please enter a valid race index. [/bold red]")
                    sub_menu()

            except requests.exceptions.RequestException as e:
                console_.print(
                    f"[bold red]Error fetching race schedule...⛓️‍💥[/bold red]")
                time.sleep(2)
            except KeyError:
                console_.print("[bold red]Unexpected data format from API...🚨[/bold red]")
                time.sleep(2)
            sub_menu()


        case 2: # Circuits
            url = f"{api_url}/circuits"
            try:
                response = requests.request("GET", url, headers=headers, data=payload)
                response.raise_for_status()

                data = response.json()
                if data.get('errors') and 'requests' in data['errors']:
                    raise requests.exceptions.RequestException

                console_.print("[bold magenta]Circuits :[/bold magenta]")
                # print(json.dumps(data, indent=2))

                circuit_table = table.Table(title="[yellow]Circuit Selection", show_lines=True)

                circuit_table.add_column("[bold white]Index", justify="center", style="cyan", no_wrap=True)
                circuit_table.add_column("[bold white]Circuit", justify="center", style="green", no_wrap=True)
                '''circuit_table.add_column("Race", justify="center", style="cyan", no_wrap=True)
                circuit_table.add_column("Race Type", justify="center", style="white")
                circuit_table.add_column("Date/Time", justify="center", style="magenta")'''

                circuits =  data.get('response', [])

                index = 1
                for circuit in circuits:
                    circuit_name = circuit['name']
                    '''
                    race_name = race['competition']['name']
                    race_date = race['date']
                    type_race = race['type']
                    '''
                    circuit_table.add_row(str(index), circuit_name)

                    index += 1

                console_.print(circuit_table)

                selected_index = int(input("Enter the index of the race you want to see details for: "))

                if 1 <= selected_index <= len(circuits):
                    selected_circuit = circuits[selected_index - 1]

                    circuit_name = selected_circuit['name']
                    race_name = selected_circuit.get('competition', {}).get('name', 'N/A')
                    race_country = selected_circuit.get('competition', {}).get('location', {}).get('country', 'N/A')
                    race_city = selected_circuit.get('competition', {}).get('location', {}).get('city', 'N/A')
                    first_gp = selected_circuit.get('first_grand_prix', 'N/A')
                    no_laps = selected_circuit.get('laps', 'N/A')
                    race_length = selected_circuit.get('length', 'N/A')
                    race_dist = selected_circuit.get('race_distance', 'N/A')

                    lap_record = selected_circuit.get('lap_record', {})
                    lap_rec_time = lap_record.get('time', 'N/A')
                    lap_rec_driver = lap_record.get('driver', 'N/A')
                    lap_rec_year = lap_record.get('year', 'N/A')

                    console_.print(f"[magenta]Circuit: [bold]{circuit_name}")
                    console_.print(f"[green]Race Name: [bold]{race_name}")
                    console_.print(f"[green]Country: [bold]{race_country}[/bold]\tCity: [bold]{race_city}[/bold]")
                    console_.print(f"[green]First Grand Prix: [bold]{first_gp}")
                    console_.print(f"[green]No. of laps: [bold]{no_laps}")
                    console_.print(f"[green]Circuit Length: [bold]{race_length}[/bold]\tDistance: [bold]{race_dist}[/bold]")

                    console_.print(f"[bold magenta]Fastest Lap Record:")
                    console_.print(f"[green]Time: [bold]{lap_rec_time}[/bold]\t\tby: [bold]{lap_rec_driver}[/bold]\t\t Year: [bold]{lap_rec_year}[/bold]")
                else:
                    console_.print("[bold red]Invalid index. Please enter a valid race index.")

            except requests.exceptions.RequestException as e:
                console_.print(
                    f"[bold red]Error fetching race schedule...⛓️‍💥[/bold red]")
                time.sleep(2)
            except KeyError:
                console_.print("[bold red]Unexpected data format from API...🚨[/bold red]")
                time.sleep(2)
            sub_menu()

        case 3: # Teams
            url = f"{api_url}/teams"
            try:
                response = requests.request("GET", url, headers=headers, data=payload)
                response.raise_for_status()

                data = response.json()
                if data.get('errors') and 'requests' in data['errors']:
                    raise requests.exceptions.RequestException

                console_.print("[bold magenta]Circuits :[/bold magenta]")
                # print(json.dumps(data, indent=2))

                team_table = table.Table(title="[yellow]Team Selection", show_lines=True)

                team_table.add_column("[bold white]Index", justify="center", style="cyan", no_wrap=True)
                team_table.add_column("[bold white]Team", justify="center", style="green", no_wrap=True)
                '''team_table.add_column("Race", justify="center", style="cyan", no_wrap=True)
                team_table.add_column("Race Type", justify="center", style="white")
                team_table.add_column("Date/Time", justify="center", style="magenta")'''

                teams =  data.get('response', [])

                index = 1
                for team in teams:
                    team_name = team['name']
                    '''
                    race_name = race['competition']['name']
                    race_date = race['date']
                    type_race = race['type']
                    '''
                    team_table.add_row(str(index), team_name)

                    index += 1

                console_.print(team_table)

                selected_index = int(input("Enter the index of the race you want to see details for: "))

                if 1 <= selected_index <= len(teams):
                    selected_team = teams[selected_index - 1]

                    team_name = selected_team['name']
                    team_base = selected_team['base']
                    team_championships = selected_team.get('world_championships','N/A')
                    team_poles = selected_team.get('pole_positions','N/A')
                    team_fastest_laps = selected_team.get('fastest_laps','N/A')
                    team_president = selected_team['president']
                    team_director = selected_team['director']
                    team_manager = selected_team['technical_manager']
                    team_chassis = selected_team['chassis']
                    team_engine = selected_team['engine']

                    console_.print(f"[magenta]Team: [bold]{team_name}")
                    console_.print(f"[green]Base: [bold]{team_base}")
                    console_.print(f"[green]World Championships: [bold]{team_championships}")
                    console_.print(f"[green]Team Poles: [bold]{team_poles}")
                    console_.print(f"[green]Fastest Laps: [bold]{team_fastest_laps}")
                    console_.print(f"[green]President: [bold]{team_president}")
                    console_.print(f"[green]Director: [bold]{team_director}")
                    console_.print(f"[green]Manager: [bold]{team_manager}")
                    console_.print(f"[green]Chassis: [bold]{team_chassis}[/bold]\tEngine: [bold]{team_engine}[/bold]")
                else:
                    console_.print("[bold red]Invalid index. Please enter a valid race index.")

            except requests.exceptions.RequestException as e:
                console_.print(
                    f"[bold red]Error fetching race schedule...⛓️‍💥[/bold red]")
                time.sleep(2)
            except KeyError:
                console_.print("[bold red]Unexpected data format from API...🚨[/bold red]")
                time.sleep(2)
            sub_menu()

        case 4:
            season = datetime.now().year
            url = f"{api_url}/rankings/drivers?season={season}"

            try:
                response = requests.request("GET", url, headers=headers, data=payload)
                response.raise_for_status()

                data = response.json()
                if data.get('errors') and 'requests' in data['errors']:
                    raise requests.exceptions.RequestException

                driv_table = table.Table(title="[yellow]Drivers", show_lines=True)

                driv_table.add_column("[bold white]Index", justify="center", style="cyan", no_wrap=True)
                driv_table.add_column("[bold white]Driver Name", justify="center", style="green", no_wrap=True)
                '''
                pos_table.add_column("[bold white]Team Name",  justify="center", style="blue", no_wrap=True)
                pos_table.add_column("[bold white]Points", justify="center", style="magenta", no_wrap=True)
                pos_table.add_column("[bold white]Wins",  justify="center", style="purple", no_wrap=True)
                '''

                index = 1
                drivers = data.get('response', [])
                for driver in drivers:
                    driver_name = driver['driver']['name']
                    '''driver_pos = str(race['position'])
                    team_name = race['team']['name']
                    driver_points = str(race['points'])
                    driver_wins = str(race['wins'])'''

                    driv_table.add_row(str(index), driver_name)

                    index += 1

                console_.print(driv_table)

                selected_index = int(input("Enter the index of the driver you want to see details for: "))

                if 1 <= selected_index <= len(drivers):
                    selected_driver= drivers[selected_index - 1]
                    driver_id = str(selected_driver['driver']['id'])

                fetch_driver_info(driver_id)

            except requests.exceptions.RequestException as e:
                console_.print(
                    f"[bold red]Error fetching driver rankings...⛓️‍💥[/bold red]")
                time.sleep(2)
            except KeyError:
                console_.print(
                    "[bold red]Unexpected data format from API...🚨[/bold red]")
                time.sleep(2)
            sub_menu()


        case 5:
            with console_.status(f"[italic cyan]Returning to Menu [/italic cyan]", spinner="dots3"):
                time.sleep(4)
            clear_screen()
            menu()

        case _:
            console_.print("[bold red]Invalid city selection![/bold red]")
            time.sleep(2)
            sub_menu()



if __name__ == "__main__":
    main()
