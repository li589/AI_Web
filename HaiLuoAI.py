import os
import time
import json
import lxml
import keyboard
import platform
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

def detect_os_category():
    os_name = platform.system()
    
    if os_name == 'Windows':
        return 'Windows'
    elif os_name == 'Darwin':
        return 'macOS'
    elif os_name == 'Linux':
        return 'Linux'
    else:
        return f'Unknown ({os_name})'

def wait_buttons(browser, timeout, opts, name):
    # WebDriverWait(browser, timeout=1).until(
    #     EC.presence_of_element_located((By.ID, 'stop-create-btn'))
    # )
    # print("Waiting: Captured Stop Button Event...")
    waiting_button = WebDriverWait(browser, timeout=timeout).until(
        EC.presence_of_element_located((opts, name))
    )
    print(f"Waiting: Captured {name} Button Event...")
    return waiting_button

def html_to_dict(element):
    if element.name is None:
        return element
    return {element.name: [html_to_dict(child) for child in element.children]}

def context2json(div_context, target_path):
    div_dict = {}
    for key, value in div_context.items():
        div_dict[f"{key}"] = value
    # str_data = str(div_dict)
    # with open(os.path.join(target_path, 'output.txt'), 'w', encoding='utf-8') as output:
    #     output.write(str_data)
    json_output = json.dumps(div_dict)
    with open(os.path.join(target_path, 'div_json.json'), 'w') as f:
        f.write(json_output)

def get_element_structure(element):
    if element is None:
        return None
    structure = {}
    for child in element.find_elements(By.XPATH, "./*"):
        # if child.get_attribute("data-id"):
        structure[child.tag_name] = get_element_structure(child)
    return structure

def setup_chrome_driver():
    # driver = webdriver.Chrome()
    drv_path = r"D:\New\Python\AI_Web\chromedriver.exe"
    chrome_path = r"C:\FreeRulesPrograms\WebDev_Drv\Chrome\chrome-win64\chrome.exe"
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

def sendText_tools(browser, input_text):
    try:
        WebDriverWait(browser, timeout=10).until(
            EC.presence_of_element_located((By.ID, 'chat-input-box'))
        )
        print("Finish: Input Blank Loaded Successfully!")
        input_textbox = WebDriverWait(browser, timeout=10).until(
            EC.presence_of_element_located((By.ID, 'chat-input'))
        )
        # input_textbox.send_keys("Hello, Hailuo AI! Please help me write a piece of yolo5 prediction code (python).")
        input_textbox.send_keys(input_text)
        print("Finish: Text Sent Successfully!")
        time.sleep(1)
        input_button = WebDriverWait(browser, timeout=10).until(
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
                            stop_button = wait_buttons(browser, timeout=1, opts=By.ID, name='stop-create-btn')
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
                    wait_buttons(browser, timeout=0.1, opts=By.ID, name='stop-create-btn')
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

def get_tools(browser):
    try:
        section_element = browser.find_element(By.ID, "chat-card-list")
    except:
        print("Error: 'chat-card-list' not found !")
        return None
    div_elements = section_element.find_elements(By.TAG_NAME, "div")
    dialog_structure = {}
    counter = 0
    for element in div_elements:
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
            solve_div_outerHTML_context_dict = html_to_dict(solve_div_outerHTML_context)
            dialog_structure[data_id] = {
             "order": counter,
             "structure": solve_div_outerHTML_context_dict,
             "context_text": solve_div_outerHTML_context.text
            }
            counter += 1
    return dialog_structure

def main(browser, url, context_write_path):
    browser.get(url)
    # time.sleep(1000)
    print(browser.title + '\n')
    send_state = sendText_tools(browser, "Hello, Hailuo AI!")
    res = 0
    while True:
        # send_state = sendText_tools(browser, "Hello, Hailuo AI! Please help me write a piece of yolo5 prediction code (python).")
        print("Please enter what you want to input: ")
        print("1. Please  input 'wquit' to quit.")
        print("2. Please enter 'cls' to clear all previous contexts")
        get_input = str(input(">>> "))
        if get_input.lower() == 'wquit':
            browser.quit()
            break
        elif get_input.lower() == 'cls':
            if detect_os_category() == 'Windows':
                os.system('cls')
                res = 2
            elif detect_os_category() == 'Linux':
                os.system('clear')
                res = 2
            else:
                print("Error: Unsupported OS.")
                res = 1
                break
        else:
            print('--------------------------------')
            send_state = sendText_tools(browser, get_input)
            get_context = {}
            time.sleep(0.5)  # 等一下
            get_context = get_tools(browser)

            if send_state == 0 and get_context != None:
                res = 0
            else:
                print("Error: Something wrong !")
                res = 1
            # for key, value in get_context.items():
            #     print(key)
            #     print(value)
            context2json(get_context, context_write_path)
            print('--------------------------------')
            last_key, last_value = next(reversed(get_context.items()))
            print(str(last_key)+ ': \n' + str(last_value["context_text"]))
            print('--------------------------------')
        
        if send_state == 0:
            print("Finish: Send Text Successfully!")
            if res == 2:
                continue
        else:
            print("Error: Something wrong when sending text!")
    
    time.sleep(1000) # 啊别关
    return res

if __name__ == "__main__":
    open_url = "https://hailuoai.com/"
    json_path = os.path.join('./output')
    if not os.path.exists(json_path):
        os.makedirs(json_path)
    chrome_browser = setup_chrome_driver()
    try:
        main(chrome_browser, open_url, json_path)
    except Exception as e:
        print(f"Error: An error occurred: {str(e)}.")
        if input() == "quit":
            chrome_browser.quit()
            print("Finish: Browser closed by user.")