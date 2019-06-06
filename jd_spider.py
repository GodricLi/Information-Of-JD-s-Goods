# _*_ coding=utf-8 _*_


import pymongo
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from urllib.parse import quote

# 配置Selenium
browser = webdriver.Chrome(executable_path=r'D:\Google\Chrome\Application\chromedriver')
wait = WebDriverWait(browser, 10)
keyword = 'iPhone'

# 配置MongoDB
MONGO_URL = 'localhost'
MONGO_DB = 'JD'
MONGO_COLLECTION = 'goods'
client = pymongo.MongoClient(MONGO_URL)
db = client[MONGO_DB]

# Chrome Headless模式
# chrome_options = webdriver.ChromeOptions()
# chrome_options.add_argument('--headless')
# browser = webdriver.Chrome(chrome_options=chrome_options)

# 对接Firefox浏览器
# browser = webdriver.Firefox()

# 使用photamojs
# browser = webdriver.PhantomJS()


def get_page(page):
    """
    获取页面
    :param page: 页码
    :return:
    """
    print('正在爬取第', page, '页')
    try:
        url = 'https://search.jd.com/Search?keyword=' + quote(keyword)
        browser.get(url)

        if page >= 1:
            # 页码搜索框加载成功
            search_page = wait.until(
                EC.presence_of_element_located(
                    (By.XPATH, '//div[@id="J_searchWrap"]//div[@id="J_bottomPage"]//span[2]/input'))
            )
            # 页码确认按钮加载成功
            submit = wait.until(
                EC.element_to_be_clickable((By.XPATH, '//div[@id="J_searchWrap"]//div[@id="J_bottomPage"]//span[2]/a')))
            print('button')
            search_page.clear()
            search_page.send_keys(page)
            submit.click()

        # 当前页码显示标识加载成功,对比我们传入的page，结果一致就返回True，证明是跳转到了传入的page页面
        wait.until(
            EC.text_to_be_present_in_element(
                (By.XPATH, '//div[@id="J_searchWrap"]//div[@id="J_bottomPage"]/span//a[@class="curr"]'), str(page))

        )
        # 商品列表加载成功
        wait.until(
            EC.presence_of_element_located((By.XPATH, '//div[@id="J_searchWrap"]//div[@id="J_goodsList"]/ul//li'))
        )
        print('Goods show successfully')
        get_goods()
    except TimeoutException:
        get_page(page)


def get_goods():
    """
    获取商品数据
    :return:
    """
    items = browser.find_elements_by_xpath('//div[@id="J_searchWrap"]//div[@id="J_goodsList"]/ul//li')
    for item in items:
        goods = {
            'img': item.find_element_by_xpath('//div[@class="p-img"]/a/img').get_attribute('src'),
            'price': item.find_element_by_xpath('//div[@class="p-price"]/strong').text,
            'commit': item.find_element_by_xpath('//div[@class="p-commit"]/strong').text,
            'title': item.find_element_by_xpath('//div[@class="p-name p-name-type-2"]/a').text,
            'shop': item.find_element_by_xpath('//div[@class="p-shop"]/span/a').text,
        }
        print(goods)
        save_to_mongo(goods)


def save_to_mongo(result):
    """
    保存到MongoDB
    :param result: 抓取到的结果：单个商品信息
    :return:
    """
    try:
        if db[MONGO_COLLECTION].insert(result):
            print('储存到MongoDB成功！')
    except Exception:
        print('存储到MongoDB失败！')


if __name__ == '__main__':
    for i in range(1, 10):
        get_page(i)
