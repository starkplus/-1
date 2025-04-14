import pickle
import json
import os

def manual_cookie_instructions():
    """提供完全手动获取Cookie的指南"""
    print("=====================================================")
    print("        完全手动获取Cookie指南")
    print("=====================================================")
    print("\n步骤1: 安装Cookie导出扩展")
    print("- 打开普通Chrome浏览器")
    print("- 访问: https://chrome.google.com/webstore/detail/editthiscookie/fngmhnnpilhplaeedifhccceomclgfbg")
    print("- 安装'EditThisCookie'扩展")
    
    print("\n步骤2: 获取网站Cookie")
    print("- 打开新标签页访问: https://www.chictr.org.cn/searchproj.html")
    print("- 如果出现滑块验证，手动完成验证")
    print("- 确认成功进入搜索页面")
    
    print("\n步骤3: 导出Cookie")
    print("- 点击浏览器右上角的EditThisCookie图标")
    print("- 点击'导出Cookie'按钮(看起来像一个向外的箭头)")
    print("- Cookie数据会被复制到剪贴板")
    
    print("\n步骤4: 粘贴Cookie数据")
    print("- 请在下面粘贴Cookie数据:")
    
    cookie_json = input("\n请粘贴从EditThisCookie导出的JSON Cookie数据到cookie.json:\n")
    

def manual_cookie_instructions2():
    """提供完全手动获取Cookie的指南"""
    print("=====================================================")
    print("        从cookie.json文件加载Cookie")
    print("=====================================================")
    
    cookie_file_path = "D:/AAAlearnings/新建文件夹/learning/dian/智慧医疗组/获取网页信息学习/cookie.json"
    print(f"正在从文件加载Cookie: {cookie_file_path}")
    
    try:
        # 从文件读取JSON
        with open(cookie_file_path, "r") as f:
            cookies = json.load(f)
        
        print(f"成功读取{len(cookies)}个Cookie")
        
        # 清理不必要的字段，避免Selenium添加Cookie时出错
        for cookie in cookies:
            if 'id' in cookie:
                del cookie['id']
            if 'storeId' in cookie:
                del cookie['storeId']
            if 'hostOnly' in cookie:
                del cookie['hostOnly']
            if 'session' in cookie:
                del cookie['session']
            # 确保sameSite正确
            if 'sameSite' in cookie and cookie['sameSite'] == 'unspecified':
                cookie['sameSite'] = 'None'
        
        # 保存为pickle文件
        with open("chictr_cookies.pkl", "wb") as f:
            pickle.dump(cookies, f)
        
        print(f"成功保存{len(cookies)}个Cookie到: {os.path.abspath('chictr_cookies.pkl')}")
        
    except Exception as e:
        print(f"处理Cookie时出错: {str(e)}")

if __name__ == "__main__":
    #manual_cookie_instructions()
    manual_cookie_instructions2()