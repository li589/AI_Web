import os
import time
import json
import lxml
import keyboard
import platform
import argparse
from tqdm import tqdm
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, ElementNotInteractableException, NoSuchElementException

class KeyListener:
    def __init__(self):
        self.key_pressed = False

    def on_key_event(self, event):
        if event.event_type == keyboard.KEY_DOWN:
            print(f"\nkey: {event.name} is pressed")
            self.key_pressed = True
            # raise KeyError("终止调用")
        # if keyboard.is_pressed('any'):
        #     print("Detected a key press, waiting for 'stop' input...")
        #     self.key_pressed = True

    def wait_for_key_press(self):
        while not self.key_pressed:
            time.sleep(0.1)
        return self.key_pressed

    def return_value(self):
        return self.key_pressed

class Auto_core:

    def __init__(self, drvPth, chromePth, jsonchoose, jsonPth):
        self.__driverPath = drvPth
        self.__chromePath = chromePth
        self.__json_output = jsonchoose
        self.__jsonPath = jsonPth
        self.browser = self.__setup_chrome_driver(self.__driverPath, self.__chromePath)
        self.__res = 0

    def open_url(self, url):
        self.browser.get(url)
        print(f"Start: Opening {url}")

    def get_web_title(self):
        self.title = self.browser.title
        return self.title

    def set_json_output(self, choose, path=None):
        self.__json_output = choose
        self.__jsonPath = path if path is not None else self.__jsonPath
        if self.__jsonPath is None:
            print("Warning: JSON output path is not provided.")
            self.__json_output = False

    def quit(self):
        self.browser.quit()
        print("Finish: Shutdown the Browser.")
 
    def detect_os_category(self):
        os_name = platform.system()

        if os_name == 'Windows':
            return 'Windows'
        elif os_name == 'Darwin':
            return 'macOS'
        elif os_name == 'Linux':
            return 'Linux'
        else:
            return f'Unknown ({os_name})'

    def __wait_buttons(self, browser, timeout, opts, name):
        # WebDriverWait(browser, timeout=1).until(
        #     EC.presence_of_element_located((By.ID, 'stop-create-btn'))
        # )
        # print("Waiting: Captured Stop Button Event...")
        waiting_button = WebDriverWait(browser, timeout=timeout).until(
            EC.presence_of_element_located((opts, name))
        )
        print(f"Waiting: Captured {name} Button Event...")
        return waiting_button

    def __html_to_dict(self, element):
        if element.name is None:
            return element
        return {element.name: [self.__html_to_dict(child) for child in element.children]}

    def context2json(self, div_context):
        target_path = os.path.join(self.__jsonPath, 'div_json.json')
        div_dict = {}
        for key, value in div_context.items():
            div_dict[f"{key}"] = value
        # str_data = str(div_dict)
        # with open(os.path.join(target_path, 'output.txt'), 'w', encoding='utf-8') as output:
        #     output.write(str_data)
        json_output = json.dumps(div_dict)
        with open(target_path, 'w') as f:
            f.write(json_output)

    def __get_element_structure(self, element):
        if element is None:
            return None
        structure = {}
        for child in element.find_elements(By.XPATH, "./*"):
            # if child.get_attribute("data-id"):
            structure[child.tag_name] = self.__get_element_structure(child)
        return structure

    def __setup_chrome_driver(self, drv, chrome):
        # driver = webdriver.Chrome()
        drv_path = drv
        chrome_path = chrome
        services = webdriver.ChromeService(executable_path=drv_path)

        options = webdriver.ChromeOptions()
        options.binary_location = chrome_path
        options.add_experimental_option('excludeSwitches', ['enable-automation']) # 阻止Chrome提示自动化脚本控制
        options.add_argument("--no-sandbox")
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3")
        options.add_experimental_option("prefs", {
                                                    "download.default_directory": "./down",
                                                    "download.prompt_for_download": False,
                                                    "download.directory_upgrade": True,
                                                    "safebrowsing.enabled": True
                                        })
        # options.add_argument("--headless") # 图形界面开关
        options.page_load_strategy = 'normal'
        ################################################################
        # normal	complete	默认值, 等待所有资源下载
        # eager	interactive	DOM 访问已准备就绪, 但诸如图像的其他资源可能仍在加载
        # none	Any	完全不会阻塞 WebDriver
        ################################################################
        options.browser_version = 'stable'
        options.platform_name = 'any'
        options.accept_insecure_certs = True
        options.timeouts = { 'implicit': 5000 }

        browser = webdriver.Chrome(service=services, options=options)
        browser.implicitly_wait(10)  # 设置隐式等待时间为10秒
        browser.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": """
          Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined
          })
        """
        }) # 反爬
        return browser

    def sendText_tools(self, input_text):
        try:
            WebDriverWait(self.browser, timeout=10).until(
                EC.presence_of_element_located((By.ID, 'chat-input-box'))
            )
            print("Finish: Input Blank Loaded Successfully!")
            input_textbox = WebDriverWait(self.browser, timeout=10).until(
                EC.presence_of_element_located((By.ID, 'chat-input'))
            )
            # input_textbox.send_keys("Hello, Hailuo AI! Please help me write a piece of yolo5 prediction code (python).")
            input_textbox.send_keys(input_text)
            print("Finish: Text Sent Successfully!")
            time.sleep(1)
            input_button = WebDriverWait(self.browser, timeout=10).until(
                EC.presence_of_element_located((By.ID, 'input-send-icon'))
            )
            try:
                input_button.click()
            except ElementNotInteractableException:
                print("Error: Element Not Interactable. Input Button not found, skipping...")
                return 1
            except NoSuchElementException:
                print("Error: No Such Element. Input Button not found, skipping...")
                return 1
            except Exception as e:
                print("Error: Unknown error", e)
                return 1

            stop_mark = False
            listener = KeyListener()
            # browser.implicitly_wait(1)
            while True:
                if stop_mark:
                    continue_num = 0
                    while True:
                        try:
                            keyboard.unhook_all()
                            print("Finish: keyboard capture stop.")
                        except Exception as e:
                            print("Warning: keyboard capture may stop?: ", e)
                            # break    # 跳出循环
                        user_input = input("\nInput 'stop' to stop output or input 'cancel' to cancel: ")
                        if user_input.lower() == 'stop':
                            try:
                                stop_button = self.__wait_buttons(self.browser, timeout=1, opts=By.ID, name='stop-create-btn')
                                stop_button.click()
                                print("Finish: Captured 'stop', quit.")
                                continue_num = 0
                                break    # 跳出循环
                            except TimeoutException:
                                print("Warning: Timeout. Stop Button display.")
                                continue_num = 0
                                break    # 跳出循环
                        elif user_input.lower() == 'cancel':
                            continue_num = 1
                            break
                        else:
                            print(f"Error: your input \"{user_input}\" !!?")
                    if continue_num == 0:
                        break
                    else:
                        stop_mark = False
                        continue_num = 0
                        continue
                else:
                    try:
                        self.__wait_buttons(self.browser, timeout=0.1, opts=By.ID, name='stop-create-btn')
                    except TimeoutException:
                        print("Warning: Timeout. Stop Button display.")
                        break    # 跳出循环

                    # keyboard.hook_events()
                    keyboard.on_press(listener.on_key_event)
                    if not listener.key_pressed:
                        time.sleep(0.5)
                    # keyboard.unhook_events()
                    # 检查是否是特定按键被按下
                    if listener.return_value():
                        stop_mark = True
                        print("Waiting: Detected a key press, waiting for 'stop' input...")
                    listener.key_pressed = False  # 重置按键状态
            try:
                keyboard.unhook_all()
                print("Finish: Key Listener Unhooked.")
            except:
                print("Warning: Failed to Unhook Key Listener. Maybe it was unhooked ?")
            finally:
                return 0
        except TimeoutException:
            print("Warning: Timeout. Input Blank not found, skipping...")
            return 1

    def get_tools(self):
        try:
            section_element = self.browser.find_element(By.ID, "chat-card-list")
        except:
            print("Error: 'chat-card-list' not found !")
            return None
        div_elements = section_element.find_elements(By.TAG_NAME, "div")
        dialog_structure = {}
        counter = 0
        for element in tqdm(div_elements, desc= "Reading chat"):
            data_id = element.get_attribute("data-id")
            if data_id != None:
                real_id = str('content-' + data_id)
                specific_id_div = element.find_element(By.ID, real_id)
                time.sleep(0.5)
                # WebDriverWait(browser, timeout=2).until(EC.visibility_of_element_located((By.CLASS_NAME, "hailuo-markdown")))
                # specific_class_div = specific_id_div.find_element(By.XPATH, '//div[@class="hailuo-markdown"]')
                # div_structure = get_element_structure(specific_id_div)
                div_outerHTML_context = specific_id_div.get_attribute("outerHTML")
                solve_div_outerHTML_context = BeautifulSoup(div_outerHTML_context,'lxml')
                solve_div_outerHTML_context_dict = self.__html_to_dict(solve_div_outerHTML_context)
                dialog_structure[data_id] = {
                 "order": counter,
                 "structure": solve_div_outerHTML_context_dict,
                 "context_text": solve_div_outerHTML_context.text
                }
                counter += 1
        return dialog_structure

    def main_loop(self):
        try:
            send_state = self.sendText_tools("Hello, Hailuo AI!")
        except Exception as e:
            print("Error: ", e)
            print("Finish: Browser Quit !!")
            self.quit()
            return 1
        self.__res = 0
        while True:
            # send_state = sendText_tools(browser, "Hello, Hailuo AI! Please help me write a piece of yolo5 prediction code (python).")
            print("Please enter what you want to input: ")
            print("1. Please  input 'wquit' to quit.")
            print("2. Please enter 'cls' to clear all previous contexts")
            get_input = str(input(">>> "))
            if get_input.lower() == 'wquit':
                self.quit()
                break
            elif get_input.lower() == 'cls':
                if self.detect_os_category() == 'Windows':
                    os.system('cls')
                    self.__res = 2
                elif self.detect_os_category() == 'Linux':
                    os.system('clear')
                    self.__res = 2
                else:
                    print("Error: Unsupported OS.")
                    self.__res = 1
                    break
            else:
                print('--------------------------------')
                send_state = self.sendText_tools(get_input)
                get_context = {}
                time.sleep(0.5)  # 等一下
                get_context = self.get_tools()
    
                if send_state == 0 and get_context != None:
                    self.__res = 0
                else:
                    print("Error: Something wrong !")
                    self.__res = 1
                # for key, value in get_context.items():
                #     print(key)
                #     print(value)
                self.set_json_output(True, self.__jsonPath)
                if self.__json_output is True:
                    self.context2json(get_context)
                print('--------------------------------')
                last_key, last_value = next(reversed(get_context.items()))
                print(str(last_key)+ ': \n' + str(last_value["context_text"]))
                print('--------------------------------')
            
            if send_state == 0:
                print("Finish: Send Text Successfully!")
                if self.__res == 2:
                    continue
            else:
                print("Error: Something wrong when sending text!")
        
        time.sleep(1) # 啊别关
        return res
    
def main(drv_path, chr_path, open_url, json_choose, context_write_path):
    auto_browser = Auto_core(drv_path, chr_path, json_choose, context_write_path)
    auto_browser.open_url(open_url)
    # time.sleep(1000)
    title = str(auto_browser.get_web_title())
    print(title)
    res = auto_browser.main_loop()
    return res
    

if __name__ == "__main__":
    open_url = "https://hailuoai.com/"
    # json_path = os.path.join('./output')
    # if not os.path.exists(json_path):
    #     os.makedirs(json_path)
    # drv_path = r"D:\New\Python\AI_Web\chromedriver.exe"
    # chr_path = r"C:\FreeRulesPrograms\WebDev_Drv\Chrome\chrome-win64\chrome.exe"
    parser = argparse.ArgumentParser(description='Run Hailuo web hook script.')
    parser.add_argument('--driver', default=r"./base/chrome-driver/chromedriver.exe", type=str, help='chromedriver.exe位置，默认在base下chrome-driver中')
    parser.add_argument('--chrome', default=r"./base/chrome-win64/chrome.exe", type=str, help='chrome.exe位置，默认在base下chrome-win64中')
    parser.add_argument('--json', default="True", type=str, help='是否写入json，默认写入')
    parser.add_argument('--jsonpath', default='./output', type=str, help='指定json写入路径，默认在Output下')
    args = parser.parse_args()
    drv_path = args.driver
    chr_path = args.chrome
    json_choStr = str(args.json).lower()
    if json_choStr == 'true' or json_choStr == 't':
        json_cho = True
    json_path = os.path.join(args.jsonpath)
    if not os.path.exists(json_path):
        os.makedirs(json_path)
    res = 0
    try:
        res = main(drv_path, chr_path, open_url, json_cho, json_path)
    except Exception as e:
        res = 1
        print(f"Error: An error occurred: {str(e)}.")
    finally:
        print(f"Exit with {res}.")