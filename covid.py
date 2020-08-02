from tkinter import *
from tkinter import messagebox
from PIL import Image, ImageTk

from bs4 import BeautifulSoup
import requests
import pycountry
import pickle
import os
import codecs
import threading

MAIN_URL = "https://www.worldometers.info/coronavirus/"
COUNTRIES_URL = "https://www.worldometers.info/coronavirus/country/"

MAIN_INFO_FONT = ("Helvetica", 15, "bold")
MAIN_INFO_FONT_SMALL = ("Helvetica", 12, "bold")
FONT = ("Helvetica", 12)

WHITE = "#ffffff"
LIGHT_GRAY = "#ebebeb"
LIGHT_YELLOW = "#ffe987"

FILENAME = "my_countries.txt"
WRITE = "wb"
READ = "rb"
MAX_COUNTRIES = 10

def get_soup(url):
	
	response = requests.get(url)
	print(url)
	response = response.text
	return BeautifulSoup(response, "lxml")

def to_number(string):

		number = string.text
		number = number[1:]
		if "," in number:
			number = number.replace(",", "")
		number = int(number)

		return number

def show_all_cases():

	soup = get_soup(MAIN_URL)
	covid_info = soup.findAll("div", class_ = "maincounter-number")

	for index, info in enumerate(covid_info):
		info = info.find("span")
		info = info.text.strip()

		covid_info[index] = info

	updated = soup.find("div", style = "font-size:13px; color:#999; margin-top:5px; text-align:center")
	updated = updated.text

	total_sum = 0
	new = soup.findAll("td", style = "background-color:#FFEEAA; color:#000;")
	for index, cases in enumerate(new):

		cases = to_number(cases)

		if cases == total_sum:
			new_cases = new[index].text
			break

		total_sum += cases

	total_sum = 0
	new = soup.findAll("td", style = "background-color:red; color:#fff")
	for index, deaths in enumerate(new):

		deaths = to_number(deaths)

		if deaths == total_sum:
			new_deaths = new[index].text
			break

		total_sum += deaths

	total_cases = covid_info[0]
	total_deaths = covid_info[1]
	total_recoveries = covid_info[2]

	return total_cases, total_deaths, total_recoveries, new_cases, new_deaths, updated

def show_following_cases(countries, country_codes, cases, deaths, recoveries, new):

	following = Tk()
	following.title("Followed Countries")
	following.focus_force()

	following["bg"] = WHITE

	background_colors = ["#ffffff", "#ee4035", "#f37736", "#fdf498", "#7bc043", "#0392cf", 
		"#ee4035", "#f37736", "#fdf498", "#7bc043", "#0392cf", "#ffffff"]

	if len(countries) == 1:
		messagebox.showinfo("COVID-19 Info",
			"You haven't followed any countries yet.")

	for country_number in range(len(countries)):

		try:
			flag = ImageTk.PhotoImage(Image.open(f"Flags/{country_codes[country_number]}.png"), master = following)
			flag_label = Label(following, image = flag, bg = background_colors[country_number])
			flag_label.image = flag
			flag_label.grid(row = country_number, column = 0)

		except Exception as e:
			flag_label = Label(following, text = "Flag\nnot found.", bg = background_colors[country_number])
			flag_label.grid(row = country_number, column = 0, sticky = "nswe")

		name_label = Label(following, font = (FONT), text = countries[country_number],
			bg = background_colors[country_number], borderwidth = 5)
		name_label.grid(row = country_number, column = 1, sticky = "nswe")

		cases_label = Label(following, font = (FONT), text = cases[country_number], 
			bg = background_colors[country_number], borderwidth = 5)
		cases_label.grid(row = country_number, column = 2, sticky = "nswe")

		deaths_label = Label(following, font = (FONT), text = deaths[country_number], 
			bg = background_colors[country_number], borderwidth = 5)
		deaths_label.grid(row = country_number, column = 3, sticky = "nswe")

		recoveries_label = Label(following, font = (FONT), text = recoveries[country_number], 
			bg = background_colors[country_number], borderwidth = 5)
		recoveries_label.grid(row = country_number, column = 4, sticky = "nswe")

		news = Label(following, font = (FONT), text = new[country_number],
			bg = background_colors[country_number], borderwidth = 5)
		news.grid(row = country_number, column = 5, sticky = "nswe")

		if country_number != 0:

			unfollow_button = Button(following, font = (FONT), text = "Click to\nUnfollow", 
				bg = WHITE, borderwidth = 2, relief = "ridge", 
				command = lambda country_number=country_number: unfollow(country_number, following))
			unfollow_button.grid(row = country_number, column = 6, sticky = "nswe")

	update = Button(following, font = (FONT), text = "Refresh Info", 
		bg = WHITE, borderwidth = 2, relief = "ridge", command = lambda: update_info(following))
	update.grid(row = 11, column = 0, columnspan = 7, sticky = "ns")

	following.mainloop()

def get_following_cases():
	
	my_countries = following_load()
	countries, country_codes = ["Country"], ["world"]

	for country in my_countries:
		countries.append(country[0])
		country_codes.append(country[1])

	cases = ["Cases"]
	deaths = ["Deaths"]
	recoveries = ["Recoveries"]
	new = ["News"]

	try:
		for index, country in enumerate(countries):

			if index > 0:
				country_name = country.lower()
				country_name = country_name.replace(" ", "-")

				soup = get_soup(COUNTRIES_URL + country_name)

				not_found = soup.find("span", class_ = "style4")
				if not_found:

					country_code = country_codes[countries.index(country)]
					soup = get_soup(COUNTRIES_URL + country_code)

					not_found = soup.find("span", class_ = "style4")
					if not_found:
						messagebox.showerror("COVID-19 Info", f"Country ({country}) not found.")
						return

				latests_update = soup.find("div", class_ = "news_date")
				latests_update = latests_update.find("h4")
				latests_update = latests_update.text

				new_list = soup.find("li", class_ = "news_li")
				new_list = new_list.findAll("strong")
				new_cases = new_list[0].text
				new_deaths = new_list[1].text
				new_info = ""

				if len(new_cases) != 0:
					new_info += new_cases

				if len(new_deaths) != 0 and country_name not in new_deaths.lower():
					new_info += f" add {new_deaths} "

				if len(latests_update) != 0:
					new_info += f" ({latests_update})"

				if "(GMT)" in new_info:
					new_info = new_info.replace("(GMT)", "")

				covid_info = soup.findAll("div", class_ = "maincounter-number")
				for index, info in enumerate(covid_info):
					info = info.find("span")
					info = info.text.strip()

					covid_info[index] = info

				country_cases = covid_info[0]
				country_deaths = covid_info[1]
				country_recoveries = covid_info[2]

				cases.append(country_cases)
				deaths.append(country_deaths)
				recoveries.append(country_recoveries)
				new.append(new_info)

	except Exception as e:
		cases.append("Error")
		deaths.append("Error")
		recoveries.append("Error")
		new.append("Error")	

	show_following_cases(countries, country_codes, cases, deaths, recoveries, new)

def show_following_countries():

	thread = threading.Thread(target = get_following_cases)
	thread.start()

def get_all_countries():

	countries = list(pycountry.countries)
	country_codes = []

	for index, country in enumerate(countries):
		countries[index] = country.name.lower()
		country_codes.append(country.alpha_2.lower())

	return countries, country_codes

def open_file():
	os.startfile("all_countries.txt")

def show_country_list():

	save_country_list()
	thread = threading.Thread(target = open_file)
	thread.start()

def save_country_list():

	with codecs.open("all_countries.txt", "w", "utf-8-sig") as file:
		file.write("Some of these countries may not have COVID-19 updates avalible.\n")
		file.write(get_country_list())

def get_country_list():

	countries = list(pycountry.countries)
	country_list = ""

	for index, country in enumerate(countries, start = 1):

		country_list += f"{index}: {country.name}\n"

	return country_list

def follow(countries, country_codes, country):

	enter_country.delete(0, END)

	if "Enter country name..." in country:
		country = country.replace("Enter country name...", "")


	for country_name in countries:

		if country.lower() in country_name:
			following_save(country, country_codes[countries.index(country_name)])
			return

	messagebox.showerror("COVID-19 Info", f"Country was not found.")

def unfollow(country_number, following):

	countries = following_load()
	countries.remove(countries[country_number - 1])

	file_save(countries)	
	update_info(following)

def following_save(country, country_code):

	if following_exists():
		countries = following_load()

		if len(countries) >= MAX_COUNTRIES:

			messagebox.showerror("COVID-19 Info",
				f"You can only follow up to {MAX_COUNTRIES} countries.")
			return

		if (country, country_code) not in countries:
			countries.append((country, country_code))
			pickle.dump(countries, open(FILENAME, WRITE))

			messagebox.showinfo("COVID-19 Info", f"{country} is now being followed.\n"
				f"You will get updates on the COVID-19 situation in {country}.")

		else:
			messagebox.showerror("COVID-19 Info",
				f"You are already following {country}.")

	else:
		following_create(country, country_code)

def following_create(country, country_code):

	my_countries = [(country, country_code)]
	pickle.dump(my_countries, open(FILENAME, WRITE))

def following_load():

	return pickle.load(open(FILENAME, READ))

def following_exists():

	return os.path.isfile(FILENAME)

def file_save(countries):

	pickle.dump(countries, open(FILENAME, WRITE))

def update_info(window):
	
	window.destroy()
	get_following_cases()

main = Tk()
main.title("COVID-19 Info")

main["bg"] = WHITE

total_cases, total_deaths, total_recoveries, new_cases, new_deaths, updated = show_all_cases()
countries, country_codes = get_all_countries()

cases = Label(main, font = (MAIN_INFO_FONT), text = f"TOTAL CASES:\n{total_cases}", bg = WHITE, anchor = "center")
cases.grid(row = 0, column = 0, sticky = "we")

new = Label(main, font = (MAIN_INFO_FONT_SMALL), text = f"New cases today:\n{new_cases}", bg = LIGHT_YELLOW, anchor = "center")
new.grid(row = 1, column = 0, sticky = "we")

deaths = Label(main, font = (MAIN_INFO_FONT), text = f"\nDEATHS:\n{total_deaths}", bg = WHITE, anchor = "center")
deaths.grid(row = 2, column = 0, sticky = "we")

new = Label(main, font = (MAIN_INFO_FONT_SMALL), text = f"New deaths today:\n{new_deaths}", bg = LIGHT_YELLOW, anchor = "center")
new.grid(row = 3, column = 0, sticky = "we")

recoveries = Label(main, font = (MAIN_INFO_FONT), text = f"\nRECOVERIES:\n{total_recoveries}\n", bg = WHITE, anchor = "center")
recoveries.grid(row = 4, column = 0, sticky = "we")

last_update = Label(main, font = (MAIN_INFO_FONT_SMALL), text = f"{updated}\n", bg = WHITE, anchor = "center")
last_update.grid(row = 5, column = 0, sticky = "we")

enter_country = Entry(main, font = (FONT), bg = LIGHT_GRAY, borderwidth = 2, relief = "groove", width = 30)
enter_country.grid(row = 6, column = 0)
enter_country.insert(0, "Enter country name...")

add_country = Button(main, font = (FONT), text = " Follow Country ", bg = WHITE, borderwidth = 2, relief = "groove",
	padx = 50, command = lambda: follow(countries, country_codes, enter_country.get()))
add_country.grid(row = 7, column = 0)

see_following = Button(main, font = (FONT), text = "See followed countries", bg = WHITE, borderwidth = 2, relief = "groove",
	padx = 26, command = show_following_countries)
see_following.grid(row = 8, column = 0)

see_list = Button(main, font = (FONT), text = "See Country list", bg = WHITE, borderwidth = 2, relief = "groove",
	padx = 50, command = show_country_list)
see_list.grid(row = 9, column = 0)

if following_exists():
	get_following_cases()

main.mainloop()