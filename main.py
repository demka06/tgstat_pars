import html
import os
import random
import time
import traceback
import telebot
import datetime
import logging
import schedule
from bs4 import BeautifulSoup as bs4
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait

logging.basicConfig(level=logging.INFO,
                    filename="py_log.log",
                    filemode="w",
                    format="%(asctime)s %(levelname)s %(message)s")
try:
  logging.info("STARTING BOT")
  TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
  TG_CHANNEL = int(os.getenv("CHANNEL_ID"))
  ADMINISTRATOR = int(os.getenv("USER_ID"))
  bot = telebot.TeleBot(TELEGRAM_TOKEN)
  logging.info("Initializing  VAR")
  MAIN_URL = "https://tgstat.ru"
  REGIONS = [
      '/tag/altai-region', '/tag/amur-region', '/tag/arkhangelsk-region',
      '/tag/astrakhan-region', '/tag/belgorod-region', '/tag/bryansk-region',
      '/tag/vladimir-region', '/tag/volgograd-region', '/tag/vologda-region',
      '/tag/voronezh-region', '/tag/eao-region', '/tag/zabaikal-region',
      '/tag/ivanovo-region', '/tag/irkutsk-region', '/tag/kbr-region',
      '/tag/kaliningrad-region', '/tag/kaluga-region', '/tag/kamchatka-region',
      '/tag/kchr-region', '/tag/kemerovo-region', '/tag/kirov-region',
      '/tag/kostroma-region', '/tag/krasnodar-region',
      '/tag/krasnoyarsk-region', '/tag/kurgan-region', '/tag/kursk-region',
      '/tag/lipetsk-region', '/tag/magadan-region', '/tag/moscow',
      '/tag/moscow-region', '/tag/murmansk-region', '/tag/nao-region',
      '/tag/nn-region', '/tag/novgorod-region', '/tag/novosibirsk-region',
      '/tag/omsk-region', '/tag/orenburg-region', '/tag/orlov-region',
      '/tag/penza-region', '/tag/perm-region', '/tag/primorsk-region',
      '/tag/pskov-region', '/tag/adigea-region', '/tag/altai',
      '/tag/bashkiria-region', '/tag/buratia-region', '/tag/dagestan-region',
      '/tag/ingushetia-region', '/tag/kalmikia-region', '/tag/karelia-region',
      '/tag/komi-region', '/tag/crimea', '/tag/maryel-region',
      '/tag/mordovia-region', '/tag/yakutia-region', '/tag/alania-region',
      '/tag/tatarstan-region', '/tag/tiva-region', '/tag/hakasia-region',
      '/tag/rostov-region', '/tag/ryazan-region', '/tag/samara-region',
      '/tag/spb', '/tag/saratov-region', '/tag/sakhalin-region',
      '/tag/ekb-region', '/tag/smolensk-region', '/tag/stavropol-region',
      '/tag/tambov-region', '/tag/tver-region', '/tag/tomsk-region',
      '/tag/tula-region', '/tag/tyumen-region', '/tag/udmurtia-region',
      '/tag/ulyanovsk-region', '/tag/khabarovsk-region', '/tag/hmao-region',
      '/tag/chel-region', '/tag/chechnya-region', '/tag/chuvashia-region',
      '/tag/chukotka-region', '/tag/yamal-region', '/tag/yaroslavl-region'
  ]
  used_regions = []

  # SELENIUM OPTIONS
  option = webdriver.ChromeOptions()
  option.add_argument("--no-sandbox")
  option.add_argument("--disable-gpu")
  option.add_argument("--disable-infobars")
  option.add_argument('--headless')
  option.add_argument('--disable-dev-shm-usage')
  prefs = {"profile.managed_default_content_settings.images": 2}
  option.add_experimental_option("prefs", prefs)
  logging.info("SELENIUM OPTIONS WAS SET")
  try:
    browser = webdriver.Chrome(options=option)  # for selenium
    logging.info("SELENIUM BROWSER WAS SET")
  except Exception:
    logging.critical("Can't start selenium", exc_info=True)
    exit(1)

  def login_tgstats(bot):
    logging.info("Login start")
    browser.get(MAIN_URL)
    try:
      WebDriverWait(browser, 3).until(
          EC.presence_of_element_located(
              (By.XPATH, "//*[@class='col notification-list']")))
    except TimeoutException:
      logging.info("Login succsess")
      return True
    browser.find_element(By.XPATH,
                         "//*[@class='col notification-list']").click()
    try:
      WebDriverWait(browser, 3).until(
          EC.presence_of_element_located(
              (By.XPATH, "//*[@class='btn btn-primary auth-btn']")))
    except TimeoutException:
      print("TimeoutException")
    auth = browser.find_element(By.XPATH,
                                "//*[@class='btn btn-primary auth-btn']")
    auth_link = auth.get_attribute("href")
    auth.click()
    browser.switch_to.window(browser.window_handles[1])
    browser.close()
    browser.switch_to.window(browser.window_handles[0])
    bot.send_message(
        chat_id=ADMINISTRATOR,
        text=
        f"Для запуска бота Вам необходимо перейти по [ссылке]({auth_link}) и "
        f"нажать '/start' в течение 2 минут",
        parse_mode="MarkdownV2")
    logging.info("Wait for login")
    try:
      WebDriverWait(browser, 120).until(
          EC.presence_of_element_located(
              (By.XPATH, "//*[@class='dropdown notification-list']")))
    except TimeoutException:
      bot.send_message(
          chat_id=ADMINISTRATOR,
          text="Вы не авторизовались. Перезапустите бота и повторите попытку")
      logging.critical(f"{ADMINISTRATOR} wasn't logined")
      exit(0)
    bot.send_message(chat_id=ADMINISTRATOR, text="Вы успешно авторизовались:)")
    logging.info(f"{ADMINISTRATOR} was logined")
    return True

  login_tgstats

  def get_top_channels():
    logging.info("Start get top channels")
    telegram_channels = []
    if len(used_regions) == len(REGIONS): used_regions.clear()
    region = random.choice(REGIONS)
    while region in used_regions:
      region = random.choice(REGIONS)
    used_regions.append(region)
    browser.get(MAIN_URL + region)
    sortchannel = Select(browser.find_element(By.ID, "sortchannel"))
    category = Select(browser.find_element(By.ID, "categoryid"))
    sortchannel.select_by_value("ci")
    time.sleep(0.2)
    category.select_by_value("2")
    time.sleep(0.4)
    bs = bs4(browser.page_source, "html.parser")
    region_name = bs.find(
        "p", class_="lead text-center text-md-left").text.strip(" \n")
    channels = bs.find_all("a", class_="text-body")
    c = 0
    while len(telegram_channels) < 10:
      subs = channels[c].find("div", class_="font-12 text-truncate")
      if int(subs.find(name="b").text.replace(" ", "")) >= 200:
        try:
          telegram_channels.append(channels[c]["href"])
        except:
          break
        c += 1
    logging.info(f"Top channels have been received from {region_name}")
    return [region_name, telegram_channels]

  def get_all_metrics(tgstat_channel_link):
    logging.info("Start getting all metrics")
    browser.get(f"{tgstat_channel_link}/stat/")
    bs = bs4(browser.page_source, "html.parser")
    charts = bs.find_all(
        "div",
        class_=
        "card card-body pt-1 pb-2 position-relative border min-height-155px")
    ci_chart = None
    subs_chart = None
    cover_chart = None
    for i in charts:
      if "индекс" in i.text.lower():
        ci_chart = i
      elif "подписчики" in i.text.lower():
        subs_chart = i
      elif "средний охват" in i.text.lower():
        cover_chart = i
    subs = int(subs_chart.find("h2", class_="text-dark").text.replace(" ", ""))
    if subs >= 100:
      subs = round(subs, -2)
    try:
      cover = int(
          cover_chart.find("h2", class_="text-dark").text.replace(" ", ""))
      if cover >= 100:
        cover = round(cover, -2)
      cover = cover / 1000
    except:
      cover = 0
    name = html.escape(
        bs.find("h1",
                class_="text-dark text-center text-sm-left").text.strip(" \n"))
    channel_link = bs.find(
        "a",
        class_="btn btn-outline-info btn-rounded px-3 py-05 font-14 mr-1 mb-15"
    )["href"]
    subs = subs / 1000
    now_ci = ci_chart.find("h2", class_="text-dark").text.replace(" ", "")
    logging.info(f"Metrics have been received from {tgstat_channel_link}")
    return [name, channel_link, subs, now_ci, cover]

  def get_CI_week(tgstat_channel_link):
    logging.info("Get CI start")
    browser.get(f"{tgstat_channel_link}/stat/citation-index")
    try:
      WebDriverWait(browser, 5).until(
          EC.presence_of_element_located(
              (By.XPATH, "//*[@class='apexcharts-series-markers']")))
    except TimeoutException:
      logging.error(f"Couldn't get CI for {tgstat_channel_link}")
      print("TimeoutException")
    diagram = browser.find_elements(By.XPATH,
                                    "//*[@class='apexcharts-series-markers']")
    ci_week = 0.0
    if len(diagram) >= 8:
      diagram = [diagram[-2], diagram[-8]]
      data = []
      for i in diagram:

        hover = ActionChains(browser).move_to_element(i)
        hover.perform()
        time.sleep(0.1)
        try:
          WebDriverWait(browser, 5).until(
              EC.presence_of_element_located(
                  (By.XPATH, "//*[@class='apexcharts-tooltip-text-y-value']")))
        except TimeoutException:
          print("TIMEOUT")
        ci = browser.find_element(
            By.XPATH, "//*[@class='apexcharts-tooltip-text-y-value']").text
        data.append(ci)
      if "" in data:
        return float(max(data))
      ci_week = round(float(data[0]) - float(data[1]), 1)
      if ci_week >= 0.0:
        ci_week = f"+{ci_week}"
      elif ci_week < 0.0:
        ci_week = f"-{ci_week}"
    logging.info(f"CI have been received from {tgstat_channel_link}")
    return ci_week

  def create_text_for_post(tgstat_channel_link):
    logging.info("Start create text for post")
    values = get_all_metrics(tgstat_channel_link)
    exmaple = f"<a href='{values[1]}'>{values[0]}</a>, подписчиков: {values[2]}K, ИЦ: {values[3]} ({get_CI_week(tgstat_channel_link)}), средний охват: {values[4]}K"
    logging.info("Text was created")
    return exmaple

  def create_post(bot):
    logging.info("Start create post")
    if login_tgstats(bot):
      top = get_top_channels()
      post_text = f"{top[0]} по уровню цитирования (ИЦ) по состоянию на {datetime.date.today().strftime('%d.%m.%Y')}\n\n"
      n = 1
      for i in top[1]:
        post_text += f"{n}. {create_text_for_post(i)}\n"
        n += 1
      post_text += "*-для обзора берутся общественно-политические тг-каналы, зарегистрированные на статистическом сервисе tgstat с числом подписчиков более 200"
      logging.info("Create post was succsessful")
      return post_text

  def main():
    try:
      logging.info("Login Telegram")
      logging.info("TG login was succsessful")
    except Exception:
      logging.critical("Authorization error", exc_info=True)
      exit(2)
    logging.info(f"Start send message")
    bot.send_message(chat_id=TG_CHANNEL,
                     text=create_post(bot),
                     parse_mode="html",
                     disable_web_page_preview=True)
    logging.info(f"Message was sent")

  schedule.every().day.at("18:00").do(main)
  while True:
    schedule.run_pending()
    time.sleep(1)

except Exception:
  logging.critical("Unknown error", exc_info=True)
  exit(3)
