from django.core.management.base import BaseCommand, CommandError
import selenium
import pendulum
import time
import requests
import psycopg2 as ps
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.service import Service
from fake_useragent import UserAgent
from django.conf import settings

def open_connection(local=True):
	conn = ps.connect(
			database="db",
			user="doadmin",
			password="AVNS_cOVLCI0p6Fm4fen-mrC",
			host="app-b76fd332-1465-4d8f-962c-b3e855e8ff80-do-user-13122490-0.b.db.ondigitalocean.com",
			port="25060")
	cur = conn.cursor()
	return conn,cur

def close_connection(conn,cur):
	cur.close()
	conn.close()

def get_existing_links(conn,cur):
	output = []
	cur.execute("SELECT link FROM games_game")
	links = cur.fetchall()
	for l in links:
		output.append(l[0])
	return output

def get_replay_links(game_format, replay_links, replay_logs):
	driver = webdriver.Chrome(service=Service(settings.BASE_DIR+"/static/logs/chromedriver.exe"))
	url = "https://replay.pokemonshowdown.com/search/?format="+game_format
	driver.get(url)

	unconnected_links = open("ReplayLinksUnlogged.txt",'a',encoding='utf-8')

	while True:
		try:
			WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.NAME, "moreResults")))
			more_button = driver.find_element(By.NAME, "moreResults")
			more_button.click()
			time.sleep(0.5)
		except TimeoutException:
			break

	ua = UserAgent()

	l = 1
	while True:
		try:
			replay = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, "/html/body/div[2]/div/ul[2]/li[{0}]/a".format(l))))
			link = replay.get_attribute("href")
			if link not in replay_links:
				try:
					log = requests.get(link+".log",headers={'User-Agent': str(ua.chrome)},timeout=5)
				except requests.exceptions.Timeout:
					unconnected_links.write(link+"\n")
					continue
				except requests.exceptions.ReadTimeout:
					unconnected_links.write(link+"\n")
					continue
				if log.text != "Could not connect":
					replay_logs.write("|link|"+link+"\n")
					replay_logs.write(log.text)
					replay_logs.write("|Game End|\n")
					time.sleep(1)
			l+=1
		except TimeoutException:
			break

	unconnected_links.close()
	driver.quit()

class Command(BaseCommand):

	def handle(*args, **options):
		log_file = open(settings.BASE_DIR+"/static/logs/replay_logs.txt",'a',encoding='utf-8')

		formats_list = ["gen9vgc2023series1","gen9vgc2023series2","gen9battlestadiumdoubles","gen9ou","gen9ubers","gen9battlestadiumsingles",
						"gen9doublesou","gen8ubers","gen8ou","gen8lc","gen8uu","gen8vgc2022","gen8spikemuthcup","gen8doublesou"]

		conn,cur = open_connection()
		links = get_existing_links(conn,cur)
		close_connection(conn,cur)

		for tier in formats_list:
			get_replay_links(tier,links,log_file)

		log_file.close()