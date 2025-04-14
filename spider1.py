from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver import Chrome
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
from selenium.common.exceptions import NoSuchElementException
import time
import math
import base64
import requests
import json
import pickle  # 添加pickle库
import os  # 添加os库
import random  # 添加random库


user = "admin"
password = "Complexpass#123"
bas64encoded_creds = base64.b64encode(bytes(user + ":" + password, "utf-8")).decode("utf-8")

# Cookie文件路径
COOKIE_FILE = r"D:\AAAlearnings\新建文件夹\learning\dian\智慧医疗组\推荐算法\go-colly-test\chictr_cookies.pkl"

# 加载Cookie函数
def load_cookies(driver):
    """从文件加载Cookie"""
    if os.path.exists(COOKIE_FILE):
        try:
            with open(COOKIE_FILE, "rb") as f:
                cookies = pickle.load(f)
            
            # 添加所有Cookie
            for cookie in cookies:
                # 处理可能导致错误的字段
                cookie_dict = {}
                for key in ['name', 'value', 'domain', 'path', 'expiry', 'secure', 'httpOnly']:
                    if key in cookie:
                        cookie_dict[key] = cookie[key]
                
                # 将expiry转换为整数，如果是浮点数的话
                if 'expiry' in cookie_dict and isinstance(cookie_dict['expiry'], float):
                    cookie_dict['expiry'] = int(cookie_dict['expiry'])
                
                try:
                    driver.add_cookie(cookie_dict)
                except Exception as e:
                    print(f"添加Cookie '{cookie_dict.get('name')}' 失败: {str(e)}")
            
            print(f"成功加载Cookie")
            return True
        except Exception as e:
            print(f"加载Cookie时出错: {str(e)}")
    else:
        print(f"Cookie文件不存在: {COOKIE_FILE}")
    return False

# 随机延迟函数
def random_delay(min_sec=1, max_sec=3):
    """随机延迟，模拟人类行为"""
    delay = random.uniform(min_sec, max_sec)
    time.sleep(delay)
    return delay

# 检查验证码函数
def check_verification(driver):
    """检查是否需要验证"""
    try:
        slider = driver.find_element(By.ID, "aliyunCaptcha-sliding-slider")
        return True  # 需要验证
    except NoSuchElementException:
        return False  # 不需要验证

# 创建一个Service对象
service = Service(ChromeDriverManager().install())
#配置参数
opt = Options()
opt.add_experimental_option('useAutomationExtension', False)
opt.add_experimental_option('excludeSwitches', ['enable-automation'])
opt.add_argument("--disable-blink-features=AutomationControlled")

# 注意：使用自定义配置文件而不是默认用户的配置文件
profile_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "chrome_profile")
if not os.path.exists(profile_dir):
    os.makedirs(profile_dir)
opt.add_argument(f'--user-data-dir={profile_dir}')

# 其他选项设置
opt.add_argument('--no-sandbox')
opt.add_argument('--disable-gpu')
opt.add_argument('--disable-dev-shm-usage')
opt.add_argument('--ignore-ssl-errors=yes')
opt.add_argument('--ignore-certificate-errors')
opt.add_argument('--disable-web-security')

driver = Chrome(service=service, options=opt)
driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
    "source": """
        // 隐藏WebDriver标志
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined
        });
        
        // 添加更多浏览器特征模拟
        Object.defineProperty(navigator, 'plugins', {
            get: () => {
                return [1, 2, 3, 4, 5].map(() => {
                    return {
                        name: 'Plugin',
                        description: 'Plugin desc',
                        filename: 'plugin.dll'
                    }
                });
            }
        });
        
        // 添加Chrome对象
        window.chrome = {
            runtime: {},
            app: { isInstalled: true },
            webstore: {}
        };
        
        // 模拟语言设置
        Object.defineProperty(navigator, 'languages', {
            get: () => ['zh-CN', 'zh', 'en-US', 'en']
        });
        
        // 修改硬件并发数
        Object.defineProperty(navigator, 'hardwareConcurrency', {
            get: () => 8
        });
    """
})

# 先访问主域以设置Cookie
print("访问主域...")
driver.get("https://www.chictr.org.cn")
random_delay(1, 2)

# 加载Cookie
load_cookies(driver)
random_delay(1, 2)

# 访问搜索页
print("访问搜索页面...")
driver.get("https://www.chictr.org.cn/searchproj.html")
random_delay(2, 3)

# 检查是否需要验证
if check_verification(driver):
    print("Cookie无效或已过期，尝试手动滑块验证...")
    try:
        slider = driver.find_element(By.ID, "aliyunCaptcha-sliding-slider")
        # 创建操作链
        action_chains = ActionChains(driver)
        # 将鼠标移动到滑块上
        action_chains.move_to_element(slider)
        # 模拟按下鼠标左键并保持不松开
        action_chains.click_and_hold()
        
        # 使用更自然的滑动轨迹
        track = []
        current = 0
        distance = 400
        mid = distance * 4/5
        t = 0.2
        v = 0
        
        while current < distance:
            if current < mid:
                a = random.uniform(2, 3)
            else:
                a = random.uniform(-3, -2)
            v0 = v
            v = v0 + a * t
            move = v0 * t + 1/2 * a * t * t
            current += move
            track.append(round(move))
        
        # 执行滑动
        for x in track:
            action_chains.move_by_offset(x, random.randint(-2, 2))
            time.sleep(random.uniform(0.001, 0.003))
        
        # 松开鼠标左键
        action_chains.release()
        # 执行操作链
        action_chains.perform()
        random_delay(2, 3)
        
        # 检查是否仍需验证
        if check_verification(driver):
            print("自动验证失败，请手动完成验证...")
            input("完成验证后按Enter继续...")
    except NoSuchElementException:
        print("未找到滑块元素")
else:
    print("使用Cookie成功绕过验证")

# 以下是原始的爬虫逻辑
hrefs = []
my_dic = {}

topic = driver.find_element(By.ID, "topic")
topic.send_keys("卵巢癌")
random_delay(0.5, 1)

button = driver.find_element(By.ID, "handle-search")
button.click()
random_delay(2, 3)

total = driver.find_element(By.ID, "data-total").text
float_part, page = math.modf(int(total)/10)  
if float_part > 0:
    page = page + 1
print(f"总页数: {int(page)}")

# 限制只爬取前2页作为测试
max_pages = min(int(page), 2)
print(f"将爬取 {max_pages} 页")

for i in range(max_pages):
    print(f"正在处理第 {i+1} 页...")
    links = driver.find_elements(By.PARTIAL_LINK_TEXT, "卵巢癌")
    
    # 限制每页处理条数
    max_links = min(len(links), 3)  # 每页最多处理3条
    
    for j in range(max_links):
        element = links[j]
        print(f"页码: {i+1}, 项目 {j+1}/{max_links}")
        print(f"题目: {element.text}")
        print(f"链接: {element.get_attribute('href')}")
        my_dic[element.get_attribute("href")] = element.text
        hrefs.append(element.get_attribute("href"))
    
    # 如果不是最后一页，点击下一页
    if i < max_pages - 1:
        button = driver.find_element(By.XPATH, '//*[@id="pagination"]/ul/li[13]')
        button.click()
        random_delay(2, 3)

# 限制只访问前3个链接
max_details = min(len(hrefs), 3)
print(f"\n共收集到 {len(hrefs)} 个链接，将访问前 {max_details} 个")

for idx, href in enumerate(hrefs[:max_details]):
    print(f"\n访问第 {idx+1}/{max_details} 个详情页: {href}")
    driver.get(href)
    random_delay(2, 3)
    
    # 检查详情页是否需要验证
    if check_verification(driver):
        print("详情页需要验证，尝试滑块...")
        try:
            slider = driver.find_element(By.ID, "aliyunCaptcha-sliding-slider")
            action_chains = ActionChains(driver)
            action_chains.move_to_element(slider)
            action_chains.click_and_hold()
            action_chains.move_by_offset(300, 0)
            action_chains.release()
            action_chains.perform()
            random_delay(2, 3)
        except NoSuchElementException:
            print("未找到滑块元素")
    
    try:
        data = driver.find_element(By.XPATH, '/html/body/div[1]/div/div[3]/div[6]/table[1]/tbody/tr[22]/td[2]/p')
        print(f"纳入标准: {data.text}")
        
        params = {
            "index": "test",
            "records": [
                {
                    "link": href,
                    "title": my_dic[href],
                    "standard": data.text
                }
            ]
        }
        # 注释掉数据存储部分，仅用于测试
        # headers = {"Content-type": "application/json",  "Authorization": "Basic " + bas64encoded_creds}
        # zinc_url= "http://localhost:4080/api/_bulkv2"
        # res = requests.post(zinc_url, headers=headers, data=json.dumps(params))
        # print(res.text)
    except Exception as e:
        print(f"提取数据失败: {str(e)}")
    
    # 增加详情页间的延迟
    random_delay(4, 6)

print("\n爬取完成!")
driver.quit()