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
import pickle
import os

user = "admin"
password = "Complexpass#123"
bas64encoded_creds = base64.b64encode(bytes(user + ":" + password, "utf-8")).decode("utf-8")
# 创建一个列表用于存储所有数据
all_data = []
# Cookie文件路径
COOKIE_FILE = r"D:\AAAlearnings\新建文件夹\learning\dian\智慧医疗组\推荐算法\go-colly-test\chictr_cookies.pkl"

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

def check_verification(driver):
    """检查是否需要验证"""
    try:
        slider = driver.find_element(By.ID, "aliyunCaptcha-sliding-slider")
        return True  # 需要验证
    except NoSuchElementException:
        return False  # 不需要验证

# 创建一个Service对象
service = Service(ChromeDriverManager().install())
# 配置参数
opt = Options()
opt.add_experimental_option('useAutomationExtension', False)
opt.add_experimental_option('excludeSwitches', ['enable-automation'])
opt.add_argument("--disable-blink-features=AutomationControlled")

# 使用自定义配置文件
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

driver = Chrome(service=service, options=opt)
# 注入反检测脚本，保持无法被识别为自动化浏览器
driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
    "source": """
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined
        });
        window.chrome = {
            runtime: {},
            app: { isInstalled: true },
            webstore: {}
        };
        Object.defineProperty(navigator, 'languages', {
            get: () => ['zh-CN', 'zh', 'en-US', 'en']
        });
        Object.defineProperty(navigator, 'plugins', {
            get: () => [1, 2, 3, 4, 5].map(() => {
                return {
                    name: 'Plugin',
                    description: 'Plugin desc',
                    filename: 'plugin.dll'
                }
            })
        });
    """
})

# 先访问主域以设置Cookie
print("访问主域...")
driver.get("https://www.chictr.org.cn")
time.sleep(2)

# 加载Cookie
load_cookies(driver)
time.sleep(1)

# 访问搜索页
print("访问搜索页面...")
driver.get("https://www.chictr.org.cn/searchproj.html")
driver.implicitly_wait(3)  # 使用与test.py相同的隐式等待

# 检查是否需要验证
if check_verification(driver):
    print("Cookie无效或已过期，尝试滑块验证...")
    try:
        slider = driver.find_element(By.ID, "aliyunCaptcha-sliding-slider")
        # 创建操作链
        action_chains = ActionChains(driver)
        action_chains.move_to_element(slider)
        action_chains.click_and_hold()
        action_chains.move_by_offset(300, 0)  # 简化滑动，与test.py类似
        action_chains.release()
        action_chains.perform()
        time.sleep(2)
        
        # 检查是否仍需验证
        if check_verification(driver):
            print("自动验证失败，请手动完成验证...")
            input("完成验证后按Enter继续...")
    except NoSuchElementException:
        print("未找到滑块元素")
else:
    print("使用Cookie成功绕过验证")

# 下面是爬虫逻辑，采用test.py的频率
hrefs = []
my_dic = {}

topic = driver.find_element(By.ID, "topic")
topic.send_keys("卵巢癌")

button = driver.find_element(By.ID, "handle-search")
button.click()

total = driver.find_element(By.ID, "data-total").text
float_part, page = math.modf(int(total)/10)  
if float_part > 0:
    page = page + 1
print(f"总页数: {int(page)}")

# 爬取所有页面 (与test.py相同)
for i in range(int(page)):
    print(f"正在处理第 {i+1}/{int(page)} 页...")
    links = driver.find_elements(By.PARTIAL_LINK_TEXT, "卵巢癌")
    
    # 收集所有链接 (与test.py相同)
    for element in links:
        print(f"页码: {i+1}")
        print(f"题目: {element.text}")
        print(f"链接: {element.get_attribute('href')}")
        my_dic[element.get_attribute("href")] = element.text
        hrefs.append(element.get_attribute("href"))
    
    # 如果不是最后一页，点击下一页
    if i < int(page) - 1:
        button = driver.find_element(By.XPATH, '//*[@id="pagination"]/ul/li[13]')
        button.click()
        # 不添加多余的延迟，让隐式等待工作

# 等待稍长时间，确保所有页面处理完成
time.sleep(5)  # 与test.py相同

print(f"\n共收集到 {len(hrefs)} 个链接，将访问所有链接")

for idx, href in enumerate(hrefs):
    print(f"\n访问第 {idx+1}/{len(hrefs)} 个详情页: {href}")
    driver.get(href)
    driver.implicitly_wait(3)  # 与test.py相同
    
    # 检查详情页是否需要验证
    try:
        slider = driver.find_element(By.ID, "aliyunCaptcha-sliding-slider")
        print("详情页需要验证，尝试滑块...")
        # 创建操作链
        action_chains = ActionChains(driver)
        action_chains.move_to_element(slider)
        action_chains.click_and_hold()
        action_chains.move_by_offset(300, 0)
        action_chains.release()
        action_chains.perform()
        time.sleep(2)  # 与test.py相同
    except NoSuchElementException:
        print("无需验证")
    
    try:
        data = driver.find_element(By.XPATH, '/html/body/div[1]/div/div[3]/div[6]/table[1]/tbody/tr[22]/td[2]/p')
        standard_text = data.text
        print(f"纳入标准: {standard_text}")
    # 获取排除标准
        try:
            exclusion_data = driver.find_element(By.XPATH, '/html/body/div[1]/div/div[3]/div[6]/table[1]/tbody/tr[24]/td[2]/p')
            exclusion_text = exclusion_data.text
            print(f"排除标准: {exclusion_text}")
        except Exception as ex:
            print(f"提取排除标准失败: {str(ex)}")
            exclusion_text = "提取失败"
        # 创建数据条目并添加到列表
        entry = {
            "链接": href,
            "标题": my_dic[href],
            "纳入标准": standard_text,
            "排除标准": exclusion_text  # 添加排除标准
        }
        all_data.append(entry)
        
    except Exception as e:
        print(f"提取数据失败: {str(e)}")
        # 即使提取纳入标准失败，也添加链接和标题
        entry = {
            "链接": href,
            "标题": my_dic[href],
            "纳入标准": "提取失败",
            "排除标准": "提取失败"  # 也要添加排除标准字段
        }
        all_data.append(entry)
        # 注释掉数据存储部分，仅用于测试
        # headers = {"Content-type": "application/json",  "Authorization": "Basic " + bas64encoded_creds}
        # zinc_url= "http://localhost:4080/api/_bulkv2"
        # res = requests.post(zinc_url, headers=headers, data=json.dumps(params))
        # print(res.text)
# 将所有数据保存到JSON文件
output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ovarian_cancer_data.json")
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(all_data, f, ensure_ascii=False, indent=4)

print(f"\n爬取完成! 数据已保存到 {output_path}")
driver.quit()