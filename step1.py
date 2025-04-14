from playwright.sync_api import sync_playwright
import time
import random
import os

def run_crawler():
    with sync_playwright() as p:
        # 使用Chromium浏览器（更强的反检测能力）
        browser = p.chromium.launch(
            headless=False,  # 显示浏览器便于调试
            args=[
                '--no-sandbox',
                '--disable-web-security',
                '--disable-features=IsolateOrigins,site-per-process',
            ]
        )
        
        # 创建上下文
        context = browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
            viewport={'width': 1280, 'height': 800},
            locale='zh-CN'
        )
        
        # 设置反检测脚本
        context.add_init_script("""
            // Playwright比Selenium有更强的自动化隐藏能力
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
        """)
        
        # 创建页面
        page = context.new_page()
        
        # 访问目标网站
        page.goto("https://www.chictr.org.cn/searchproj.html")
        
        # 等待页面加载
        page.wait_for_load_state('networkidle')