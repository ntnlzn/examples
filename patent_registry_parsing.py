# Импортируем библиотеки для работы с временем, регулярными выражениями,
# таблицами, управления браузером с помощью питона и вызова окон указания
# пути к файлу
import time
import regex
import pandas as pd
from selenium import webdriver
from tkinter import filedialog as fd 

# Создаем таблицу, которую будем заполнять именем правообладателя и ссылкой
# на его товарный знак
brand_holders = pd.DataFrame({'brand_holder' : [],
                              'url_brand' : [],
                              'brand_name' : []
                              })

def ocr_tbl():
    """Эта функция заполняет таблицу распознанными именами брендов"""
    open_browser_ocr()
    brand_holders['brand_name'] = brand_holders.url_brand.apply(ocr)
    
def open_browser_ocr():
    """Эта функция открывает окно браузера, который будет использоваться для распознавания"""
    global browser_ocr
    browser_ocr = webdriver.Chrome()

def open_browser():
    """Эта функция открывает Google Chrome и переходит на страницу реестра товарных знаков"""
    global browser

    browser = webdriver.Chrome()

    # Открываем браузер на странице открытых реестров
    browser.get('https://new.fips.ru/registers-web/')

    # Переходим в реестр товарных знаков
    browser.find_element("xpath", '//*[@id="mainpagecontent"]/div[2]/div/div[2]/div/table/tbody/tr[5]/td[2]/span[1]/a')\
                                  .click()

def ocr(url_pic):
    """Эта функция берет URL картинки с товарным знаком, передает её в поиск по
    изображениям google и извлекает распознанный текст"""
    try:
        browser_ocr.get('https://www.google.com/imghp?sbi=1')

        # Нажимаем кнопку "поиск по картинке"
        browser_ocr.find_element("xpath", '/html/body/div[1]/div[3]/form/div[1]/div[1]/div[1]/div/div[3]/div[4]/svg/g/path[1]')\
                                          .click()
        
        #browser_ocr.find_element("xpath", '/html/body/div[1]/div[3]/form/div[1]/div[1]/div[1]/div/div[3]/div[4]/img')\
         #                                 .click()

        # Ждем завершения анимации
        time.sleep(0.5)

        # Вводим ссылку на картинку
        browser_ocr.find_element("xpath", '//*[@id="ow6"]/div[3]/c-wiz/div[2]/div/div[3]/div[2]/c-wiz/div[2]/input')\
                                          .send_keys(url_pic)

        # Нажимаем "поиск"
        browser_ocr.find_element("xpath", '//*[@id="ow6"]/div[3]/c-wiz/div[2]/div/div[3]/div[2]/c-wiz/div[2]/div')\
                                          .click()

        browser_ocr.find_element("xpath", '//*[@id="ucj-4"]/span[1]').click()

        # Ждем пока прогрузятся скрипты
        time.sleep(1) # При подключении через vpn надо увеличивать
        browser_ocr.find_element("xpath", '//*[@id="yDmH0d"]/div[3]/c-wiz/div/c-wiz/c-wiz/div/div[2]/div/div/div/div[1]/div/div/div[2]/div/button/span')\
                                          .click()

        # Присваиваем распознанный текст переменной, которую возвращает функция
        name_brand = browser_ocr.find_element("xpath",'//*[@id="yDmH0d"]/div[3]/c-wiz/div/c-wiz/c-wiz/div/div[2]/div/div/span/div/div[2]')\
                     .text

        name_brand = regex.compile('[^ a-zA-Zа-яА-Я0-9!,.-]')\
                     .sub('', name_brand).strip()

        return name_brand

    except BaseException:
        name_brand = ''
        return name_brand

def scan_document(): 
    """Эта функция  извлекает из патента URL изображения с товарным знаком
    и правообладателя, затем помещает эти данные в таблицу brand_holders"""
    
    global i_scan###
    for i in range(1, 5):
        for k in range(1, 26):
            try:
                # Если патент действителен, то работаем с ним, иначе проверяем следующий
                if browser\
                   .find_element("xpath",\
                                 '//*[@id="mainpagecontent"]/div[2]/div/div[4]/div/table/tbody/tr[' \
                                 + str(k) + ']/td[' + str(i) + ']/span[1]')\
                                 .get_attribute('class') == 'dots q_green':

                    path = '//*[@id="mainpagecontent"]/div[2]/div/div[4]/div/table/tbody/tr['\
                           + str(k) + ']/td[' + str(i) + ']/span[2]/a'

                    browser.find_element("xpath", path).click()

                    # "Запоминаем" текущее активное окно
                    current_window = browser.current_window_handle

                    # Определяем идентификаторы открытых окон
                    second_window = browser.window_handles

                    # Определяем идентификатор окна с патентом
                    second_window.remove(current_window)

                    # Переходим в окно с патентом
                    browser.switch_to.window(second_window[0])

                    # Получаем html код окна с патентом
                    x = browser.page_source

                    # Убираем лишнее
                    x = x[ x.find('<p class="bib">(540)') \
                           : x.find('(732) <i>') + 500 ]

                    # Достаем URL картинки с товарным знаком
                    url_brand = x[ x.find('img src=\"') + 9 \
                                   : x.find('" style="height') ] 

                    # Достаем имя и адрес юрлица
                    brand_holder = x[ x.find('<b>') + 3 : x.find('</b>') ]

                    # Добавляем в таблицу имя правообладателя и ссылку
                    # на картинку с его товарным знаком
                    brand_holders.loc[ len(brand_holders.index )] \
                                       = [brand_holder, url_brand,'']

                    browser.close()
                    browser.switch_to.window(current_window)

                    # Бездействуем 3 секунды, чтобы не спровоцировать
                    # появления окна с капчей и бана нашего IP
                    time.sleep(3)

            except BaseException:
                pass

    #Переход на предыдущее окно
    browser.find_element("xpath", '//*[@id="mainpagecontent"]/div[2]/div/div[2]/div[2]/div[2]/a[2]/nobr')\
                                  .click()

# Функции scan_2 - scan_5 выполняют обход дерева реестра.  
def scan_5():        # "Обход" по веткам дерева level=5
    for i in range(1, 12):
        try:
            path = '//*[@id="mainpagecontent"]/div[2]/div[2]/div/ul/ul/ul/ul/ul/li['\
                   + str(i) + ']/a'

            browser.find_element("xpath", path).click()

            scan_document()

        except BaseException:
            pass

def scan_4():        # "Обход" по веткам дерева level=4
    for i in range(1, 12):
        try:
            path = '//*[@id="mainpagecontent"]/div[2]/div[2]/div/ul/ul/ul/ul/li['\
                   + str(i) + ']/a[2]'

            browser.find_element("xpath", path).click()

            scan_5()

        except BaseException:
            pass

def scan_3():        # "Обход" по веткам дерева level=3
    for i in range(1, 11):
        try:
            path = '//*[@id="mainpagecontent"]/div[2]/div[2]/div/ul/ul/ul/li['\
                   + str(i) + ']/a[2]'

            browser.find_element("xpath", path).click()

            scan_4()

        except BaseException:
            pass

def scan_2():        # "Обход" по веткам дерева level=2
    for i in range(1, 11):
        try:
            path = '//*[@id="mainpagecontent"]/div[2]/div[2]/div/ul/ul/li['\
                   + str(i) + ']/a[2]'

            browser.find_element("xpath", path).click()

            scan_3()

        except BaseException:
            pass

def brand_holders_screening():
    
    """Эта функция меняет кавыки "елочки" на обычные, удаляет строки с физ.лицами, 
    оставляет в brand_holder только название организации без адреса"""
    global brand_holders
    
    brand_holders.brand_holder = brand_holders.brand_holder\
    .apply(lambda str: str.replace('«','"').replace('»','"'))
    
    brand_holders = brand_holders[(brand_holders.brand_holder\
    .apply(lambda x : True if ((x.partition(',')[0].find('"') != -1) \
                          and (x.find('(RU)') != -1 \
                               or x.find('(BY)')!= -1 \
                               or x.find('(KZ)') != -1)) \
                          or (x.find('(RU)') == -1 \
                              and x.find('(BY)') == -1 \
                              and x.find('(KZ)') == -1) \
                          else False))]
    
    u = brand_holders.loc[brand_holders.index,['brand_holder',
                                               'url_brand',
                                               'brand_name']]
    
    u.loc[u.index,['brand_holder']] = brand_holders\
    .loc[brand_holders.index,['brand_holder', 'url_brand', 'brand_name']]\
    .brand_holder.apply(lambda m : m.partition(',')[0] \
                        if m.find('(RU)' or '(BY)' or '(KZ)') != -1 \
                        else m.split(',')[0] + ',' + m.split(',')[1] \
                            if m.lower().find('лтд') != -1 
                            else m.partition(',')[0])
    
    brand_holders = u.dropna().loc[u['brand_name'] != ''].reset_index()\
                    .iloc [: , 1:]

def import_csv():
    """Выбираем путь сохранения файла в окне"""
    path = fd.asksaveasfilename(defaultextension='csv',
                                initialfile='brand_holders.csv')

    if path.find('.csv') == -1:
        path = path + '.csv'
    brand_holders.to_csv(path, sep=';', encoding='windows-1251', index=False)
    if path != '.csv':
        print('Файл сохранен в {}'.format(path))
    else:
        print('Файл не сохранен')

def start(n):
    """Меню выбора функций программы"""
    
    if n == 0:
        print_text()
    elif n == 1:
        open_browser()
        scan_2()
    elif n == 2:
        ocr_tbl()
        brand_holders_screening()
    elif n == 3:
        print(brand_holders[['brand_holder', 'brand_name']])
    elif n == 4:
        import_csv()
    else:
        print('Выберите от 0 до 4')
    start(int(input()))

def print_text():
    print(
'------------------------------------------------------------------------\n\
# Эта программа выполняет обход дерева реестра товарных знаков и знаков\n\
# обслуживания Российской Федерации, расположенного на сайте Федерального\n\
# института промышленной собственности (https://new.fips.ru), извлекает\n\
# из каждого патента имя правообладателя и URL изображения его товарного\n\
# знака (функция 1), распознает товарный знак на изображении (функция 2) и\n\
# составляет таблицу вида:\n\
# brand_holder | url_brand | name_brand\n\
------------------------------------------------------------------------\n\
Введите:\n\
0. Показать стартовое сообщение\n\
1. Собрать исходные данные (Имя правообладателя и URL изображения с его\n\
   товарным знаком)(для остановки закройте браузер)\n\
2. Распознать товарные знаки и добавить их имя в таблицу (для остановки\n\
   закройте браузер)\n\
3. Показать таблицу\n\
4. Импорт таблицы в csv с выбором пути для сохранения\n')    

print_text()
start(int(input()))