import time,random,pyquery,re,json,requests,os
from PIL import Image
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException

useragent = [
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36',
    'Mozilla/5.0 (Windows NT 5.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36',
    ]

class Driver():
    def __init__(self):
        pass
    def open_driver(self):
        options = Options()
        options.add_argument("--headless")
        # options.add_argument("--disable-gpu")
        options.add_argument("user-agent=" + random.choice(useragent))
        options.add_argument("--incognito")
        options.add_argument("--window-size=1200x927")
        # options.add_argument("blink-settings=imagesEnabled=false")
        self.driver = webdriver.Chrome(options=options)
        self.driver.set_page_load_timeout(30)
        self.driver.get("https://www.douyin.com/search/a?source=normal_search&type=user")
        # print(self.driver.get_window_size()) # ??????????????????
        code_path="./image/code.png" # ??????????????????
        if not os.path.exists("./image"):
            os.makedirs("./image")
        print("???????????????????????????...")
        self.pass_verify(code_path)
        print("driver_id:", id(self), "????????????\n=======================")


    def close_driver(self):
        self.driver.close()

    def pass_verify(self,code_path,count=0):
        try:
            WebDriverWait(self.driver, 3).until( # ???????????????????????????????????????3???
                EC.presence_of_element_located((By.CSS_SELECTOR, 'img[class^="captcha_verify_img_slide"]')))
        except TimeoutException:
            return # ???????????????
        if count>8: # ???15??????????????? ????????????
            self.driver.close()
            self.open_driver()
            return
        res = requests.get(
            self.driver.find_element_by_css_selector('img[id="captcha-verify-image"]').get_attribute('src'),  # ""???????????????
            headers={'User-Agent': random.choice(useragent)})
        with open(code_path, 'wb') as f:
            f.write(res.content)
        img=Image.open(code_path)
        img=img.resize((340,212))
        img.save(code_path)
        # self.driver.get_screenshot_as_file(screen_path)
        x, y = self.get_dray_distance(code_path)
        print(count,":",x,y)
        slider = self.driver.find_element_by_css_selector('img[class^="captcha_verify_img_slide"]')
        # ????????????????????????
        L1=[0.3,0.24,0.21,0.14,0.11]
        L2=[0.12,0.18,0.12,0.05,0.08]
        ActionChains(self.driver).click_and_hold(slider).perform()
        for i in L1:
            ActionChains(self.driver).move_by_offset(i,L2.pop()).perform()
            time.sleep(random.randint(20,40)*0.01)
        ActionChains(self.driver).move_by_offset(x, y).perform()
        ActionChains(self.driver).release().perform()
        time.sleep(3)
        # ???????????????????????????
        try:
            self.driver.find_element_by_css_selector('img[class^="captcha_verify_img_slide"]')
            self.pass_verify(code_path,count+1)
        except Exception as e:
            # print(e)
            self.driver.refresh()
            self.driver.refresh()

    def get_dray_distance(self,filepath): # ????????????????????????
        # ????????????????????????
        img = Image.open(filepath).convert("L")
        pixels = img.load()
        w, h = img.size
        for x in range(w):
            for y in range(h):
                # print(pixels[x, y], end=' ')
                if pixels[x, y] < 230:
                    img.putpixel((x, y), 0)
                else:
                    img.putpixel((x, y), 255)
            # print()
        # img.show()
        # ????????????????????????????????????10*1???????????????2???
        for x in range(w - 10):
            for y in range(h - 10):
                if pixels[x, y] == 255:
                    count_white_x = sum(True for i in range(0, 10) for j in range(0, 1) if pixels[x + i, y + j] > 0)
                    if count_white_x < 8: continue
                    count_white_y = sum(True for i in range(-1, 0) for j in range(1, 11) if pixels[x + i, y + j] > 0)
                    if count_white_y < 8: continue
                    count_white = sum(True for i in range(0, 10) for j in range(1, 2) if pixels[x + i, y + j] > 0) + \
                                  sum(True for i in range(1, 2) for j in range(1, 11) if pixels[x + i, y + j] > 0)
                    if count_white < 6:  # ???????????????????????????0
                        # print(x, y) # ?????????????????????
                        return x-3, y # ??????????????????3
        return 111,111 # ?????????

    def isVaild(self): # ??????????????????
        try:
            return self.driver.find_element_by_xpath('//*[@id="root"]/div/div[2]/div/div[2]/div[3]/div/div/div[2]').text!="??????????????????"
        except:
            return True

    def user_search(self,keyword):
        # if random.randint(0,1): # ????????????
        #     raise Exception()
        self.driver.get("https://www.douyin.com/search/" + keyword + "?source=normal_search&type=user")
        print(self.driver.current_url)
        try:
            WebDriverWait(self.driver,2).until(EC.presence_of_element_located((By.CSS_SELECTOR,'div[style="display: block;"] ul li a div button')))
        except TimeoutException:
            if not self.isVaild():  # ?????????????????????driver
                self.close_driver()
                raise Exception()
            return [] # ?????????????????????????????????????????????????????????????????? https://www.douyin.com/search/%01?source=normal_search&type=user

        return self.get_userinfo(self.driver.page_source)

    def get_userinfo(self,page_source): # ????????????
        doc = pyquery.PyQuery(page_source)
        li = doc('div[style="display: block;"] ul li')
        print("?????????{}???????????????".format(len(li)))
        data = []
        for user in li.items():
            try:
                nickname, signature = user('a p span span span span span').items()  # ??????????????????
            except: # ????????????
                nickname,signature='',user('a p span span span span span').text()
            temp = re.split(" +", user('a>div:nth-child(2) span').text())[2:] # ??????????????????????????????
            avatar_thumb=user('a>div>div:nth-child(1) img').attr.src # ??????
            if avatar_thumb.startswith('data:image/'): # ????????????
                avatar_thumb=''
            # ??????????????????????????????????????????????????????????????????
            data.append({'secid':li('a').attr.href.split('?')[0][28:],
                         'nickname': re.sub('(<img.*?alt=")(.*?)(".*?/>)', "\g<2>", nickname.__str__())[6:-7],
                         'custom_verify': user('a>div>div>div p').text(),
                         'unique_id': temp[0],
                         'total_favorited': temp[1],
                         'follower_count': temp[2],
                         'signature': re.sub('(<img.*?alt=")(.*?)(".*?/>)', "\g<2>", signature.__str__())[6:-7],
                         'avatar_thumb': avatar_thumb,
                         })
            # break
        print(data)
        return data

if __name__=="__main__":
    driver=Driver()
    driver.open_driver()
    print(driver.user_search("?????????"))
    # time.sleep(100)
    # for i in range(340,65535):
    #     print(driver.user_search(chr(i)))
    driver.close_driver()