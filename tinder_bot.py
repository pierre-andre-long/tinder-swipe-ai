from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from time import sleep

from secrets import username, password

from beauty_predict import scores

import requests, os


APP_ROOT = os.path.dirname(os.path.abspath(__file__))

def download_image(source, destination):
    img_data = requests.get(source).content
    with open(destination, 'wb') as out:
        out.write(img_data)

class TinderBot():
    def __init__(self, threshold=6.5):
        self.driver = webdriver.Chrome(ChromeDriverManager().install())
        self.threshold = threshold
        self.begining = True

    def login(self):
        self.driver.get('https://tinder.com')

        sleep(3)

        fb_btn = self.driver.find_element_by_xpath('//*[@id="modal-manager"]/div/div/div/div/div[3]/div[2]/button')
        fb_btn.click()

        # switch to login popup
        base_window = self.driver.window_handles[0]
        self.driver.switch_to_window(self.driver.window_handles[1])

        email_in = self.driver.find_element_by_xpath('//*[@id="email"]')
        email_in.send_keys(username)

        pw_in = self.driver.find_element_by_xpath('//*[@id="pass"]')
        pw_in.send_keys(password)

        login_btn = self.driver.find_element_by_xpath('//*[@id="u_0_0"]')
        login_btn.click()

        self.driver.switch_to_window(base_window)

        sleep(1)
        popup_1 = self.driver.find_element_by_xpath('//*[@id="modal-manager"]/div/div/div/div/div[3]/button[1]')
        popup_1.click()

        sleep(1)
        popup_2 = self.driver.find_element_by_xpath('//*[@id="modal-manager"]/div/div/div/div/div[3]/button[1]')
        popup_2.click()
        sleep(10)

    def like(self):
        like_btn = self.driver.find_element_by_xpath('//*[@id="content"]/div/div[1]/div/main/div[1]/div/div/div[1]/div/div[2]/button[3]')
        like_btn.click()

    def dislike(self):
        dislike_btn = self.driver.find_element_by_xpath('//*[@id="content"]/div/div[1]/div/main/div[1]/div/div/div[1]/div/div[2]/button[1]')
        dislike_btn.click()

    def auto_swipe(self):
        while True:
            sleep(0.5)
            try:
                self.like()
            except Exception:
                try:
                    self.close_popup()
                except Exception:
                    self.close_match()

    def choose(self):
        scrs = self.current_scores()
        choice = "DISLIKE"
        if len(scrs) == 0:
            self.dislike()
        elif [scr > self.threshold for scr in scrs] == len(scrs) * [True]:
            self.like() # if there are several faces, they must all have
            choice = "LIKE" # better score than threshold to be liked
        else:
            self.dislike()

        print("Scores : ",
              scrs,
              " | Choice : ",
              choice,
              " | Threshold : ",
              self.threshold)

    def ai_swipe(self):
        while True:
            sleep(3)
            try:
                self.choose()
            except Exception as err:
                try:
                    self.close_popup()
                except Exception:
                    try:
                        self.close_match()
                    except Exception:
                         print("Error: {0}".format(err))


    def close_popup(self):
        popup_3 = self.driver.find_element_by_xpath('//*[@id="modal-manager"]/div/div/div[2]/button[2]')
        popup_3.click()

    def close_match(self):
        match_popup = self.driver.find_element_by_xpath('//*[@id="modal-manager-canvas"]/div/div/div[1]/div/div[3]/a')
        match_popup.click()

    def get_image_path(self):
        body = self.driver.find_element_by_xpath('//*[@id="Tinder"]/body')
        bodyHTML = body.get_attribute('innerHTML')
        startMarker = '<div class="Bdrs(8px) Bgz(cv) Bgp(c) StretchedBox" style="background-image: url(&quot;'
        endMarker = '&'

        if not self.begining:
            urlStart = bodyHTML.rfind(startMarker)
            urlStart = bodyHTML[:urlStart].rfind(startMarker)+len(startMarker)
        else:
            urlStart = bodyHTML.rfind(startMarker)+len(startMarker)

        self.begining = False
        urlEnd = bodyHTML.find(endMarker, urlStart)
        return bodyHTML[urlStart:urlEnd]

    def current_scores(self):
        url = self.get_image_path()
        outPath = os.path.join(APP_ROOT, 'images', os.path.basename(url))
        download_image(url, outPath)
        return scores(outPath)

bot = TinderBot()
bot.login()
bot.ai_swipe()
