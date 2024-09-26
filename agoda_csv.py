from selenium import webdriver
from time import sleep
from selenium.webdriver.common.keys import Keys
from selenium.webdriver import ActionChains
import csv
from selenium.webdriver.support.ui import WebDriverWait as wait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import sys
import operator

with open("city.txt",encoding="utf8") as f:
    VN=[]
    for line in f:
        line=line.strip("\n")
        VN.append(line)
f.close()



with open("agoda.csv", "w", encoding="utf16") as output:

    Columns = ["Tên thành phố", "Số Khách sạn", "Khách sạn có giá rẻ nhất", "Giá rẻ nhất", "Khách sạn có giá mắc nhất",
               "Giá mắc nhất", "Khách sạn được đánh giá thấp nhất", "Đánh giá thấp nhất",
               "Khách sạn được đánh giá cao nhất", "Đánh giá cao nhất", "Số tiền trung bình",
               "Điểm đánh giá trung bình"]
    writer = csv.DictWriter(output, fieldnames=Columns)
    writer.writeheader()
    for city in VN:
        Search_City = city
        Search_Country = "Việt Nam"
        Search_Box = Search_City + " " + Search_Country

        #Khởi tạo webdriver
        agoda = webdriver.Chrome(executable_path="./chromedriver")
        agoda.get("https://www.agoda.com/vi-vn/country/vietnam.html?asq=Pw87gxddcXIPGhuafpB1trOC%2FuRmwIsiMmt%2BhvVuFAYWC77HAetvX%2FgDlaqamRgDr7eB6givMJyMJ0x5qnt6m4vbyfxAU59PHa%2BfwvQB4NK%2BwzeBekNSqp390BrVk7x6")
        sleep(2)

        #Tìm và điền tên thành phố vào ô tìm kiếm
        box=agoda.find_element_by_class_name("SearchBoxTextEditor.SearchBoxTextEditor--autocomplete")
        box.send_keys(Search_Box)
        sleep(2)

        #Bấm nút TÌM ở Agoda
        search_button=agoda.find_element_by_xpath("//*[@id='SearchBoxContainer']/div/div/button")
        ActionChains(agoda).click(search_button).perform()
        sleep(3)

        try:
            ads=agoda.find_element_by_class_name("closeNotificationTapZone")
            ActionChains(agoda).click(ads).perform()
        except:
            pass


        page_number = agoda.find_element_by_class_name("pagination2__text")
        page_number = str(page_number.text).split()
        page_number = int(page_number[-1])
        hotel_list={}
        for page in range(1, page_number + 1):
            sleep(5)
            for num in range(1,1000):
                hotels = wait(agoda, 1).until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'PropertyCard.PropertyCardItem')))
                height = num*4
                while num < len(hotels):
                    try:
                        agoda.execute_script('arguments[0].scrollIntoView();', hotels[height])
                        # Wait for more names to be loaded
                        wait(agoda, 5).until(lambda agoda: len(wait(agoda, 5).until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'PropertyCard.PropertyCardItem')))) > len(hotels))
                        # Update names list
                        hotels = wait(driver, 5).until(EC.presence_of_element_located((By.CLASS_NAME, 'PropertyCard.PropertyCardItem')))
                    except:
                        break
                if height > len(hotels):
                    break

                sleep(1)
            for hotel in hotels:
                try:
                    name=hotel.find_element_by_class_name("PropertyCard__HotelName").text

                    price=hotel.find_element_by_class_name("PropertyCardPrice__Value").text
                    price=int(price.replace('.',''))

                    try:
                        star = hotel.find_element_by_class_name("ReviewWithDemographic").text
                        star=str(star).split()
                        star=float(star[-1].replace(',','.'))
                    except:
                        pass

                    hotel_list[name]=[price,star]
                except:
                    pass

            try:
                next = agoda.find_element_by_class_name("btn.pagination2__next")
                ActionChains(agoda).click(next).perform()
            except:
                pass
            sleep(2)


        ht_max_price=max(hotel_list.items(), key=operator.itemgetter(1))[0]
        for name, (price, cmt) in hotel_list.items():
            if name == ht_max_price:
                max_price=price


        ht_min_price=min(hotel_list.items(), key=operator.itemgetter(1))[0]
        for name, (price, cmt) in hotel_list.items():
            if name == ht_min_price:
                min_price=price


        min_star = 10
        for name,(price,cmt) in hotel_list.items():
            if cmt < min_star:
                min_star = cmt
        for name, (price, cmt) in hotel_list.items():
            if cmt == min_star:
                ht_min_star = name


        max_star = 0
        for name, (price, cmt) in hotel_list.items():
            if cmt > max_star:
                max_star = cmt
        for name, (price, cmt) in hotel_list.items():
            if cmt == max_star:
                ht_max_star = name


        avr_price = 0
        for name, (price, cmt) in hotel_list.items():
            avr_price+=price
        avr_price=avr_price/len(hotel_list)
        avr_price=round(avr_price)


        avr_rating = 0
        for name, (price, cmt) in hotel_list.items():
            avr_rating += cmt
        avr_rating = avr_rating / len(hotel_list)



        writer.writerow({"Tên thành phố": city, "Số Khách sạn": len(hotel_list), "Khách sạn có giá rẻ nhất":ht_min_price,
                        "Giá rẻ nhất":min_price, "Khách sạn có giá mắc nhất":ht_max_price, "Giá mắc nhất":max_star, "Khách sạn được đánh giá thấp nhất":ht_min_star,
                        "Đánh giá thấp nhất":min_price, "Khách sạn được đánh giá cao nhất":ht_max_star, "Đánh giá cao nhất":max_star,
                        "Số tiền trung bình":avr_price, "Điểm đánh giá trung bình":round(avr_rating,2)})

        agoda.close()

output.close()