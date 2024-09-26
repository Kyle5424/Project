from selenium import webdriver
from time import sleep
from selenium.webdriver.common.keys import Keys
from selenium.webdriver import ActionChains
import sys
#Hàm tìm kiếm thành phố và quốc gia
def Searching():
    Search_City = "Sóc Trăng"
    Search_Country = "Việt Nam"
    Search_Box = Search_City + " " + Search_Country

    #Khởi tạo webdriver
    agoda = webdriver.Chrome(executable_path="./chromedriver")
    agoda.get("https://www.agoda.com/vi-vn/?site_id=1891474&tag=99f03749-3c7e-589e-fa81-305d021c7a12&device=c&network=g&adid=492713364618&rand=11346430354917842775&expid=&adpos=&aud=kwd-2230651387&gclid=EAIaIQobChMIkOfotPqT8AIVAqqWCh1xYAA2EAAYASAAEgKIu_D_BwE")
    sleep(2)

    #Tìm và điền tên thành phố vào ô tìm kiếm
    city=agoda.find_element_by_class_name("SearchBoxTextEditor.SearchBoxTextEditor--autocomplete")
    city.send_keys(Search_Box)
    sleep(5)

    #Tắt quảng cáo
    try:
        ads=ActionChains(agoda)
        ads.move_to_element(agoda.find_element_by_class_name("ab-close-button")).perform()
        ads.click().perform()
        sleep(2)
    except:
        pass

    scroll=ActionChains(agoda)
    scroll.send_keys(Keys.PAGE_DOWN).perform()

    sleep(2)

    #Bấm nút TÌM ở Agoda
    search_button=agoda.find_element_by_xpath("//*[@id='SearchBoxContainer']/div[2]/button")
    ActionChains(agoda).click(search_button).perform()
    sleep(3)

    #Lưu địa chỉ của trang danh sách
    Url = agoda.current_url
    agoda.close()
    return Url


#Hàm trả về url của các khách sạn
def Hotel_List():
    url=Searching()

    #Khởi tạo webdriver mới
    brow = webdriver.Chrome(executable_path="./chromedriver")
    brow.get(url)
    page_number=brow.find_element_by_class_name("pagination2__text")
    page_number=str(page_number.text).split()
    page_number=int(page_number[-1])
    hotel_list = []
    for page in range(1,page_number+1):

        #Lướt chuột xuống cuối trang
        last_height = brow.execute_script("return document.body.scrollHeight")
        while True:
            brow.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            sleep(3)
            new_height = brow.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

        #Tìm các url của các khách sạn và thêm vào danh sách
        links = brow.find_elements_by_class_name("PropertyCard__Link")
        for link in links:
            hotel_list.append(link.get_attribute("href"))

        try:
            next=brow.find_element_by_class_name("btn.pagination2__next")
            ActionChains(brow).click(next).perform()
        except:
            pass
        sleep(2)
    brow.close()
    return hotel_list

hotel_list = Hotel_List()


output=sys.stdout
sys.stdout = open("agoda.txt", "w",encoding="utf-8")

#Khởi tạo webdriver cào khách sạn
crawl = webdriver.Chrome(executable_path="./chromedriver")

for hotel in hotel_list:
    crawl.get(hotel)
    sleep(3)
    print("\n")

    #Cào tên khách sạn
    name = crawl.find_element_by_class_name("HeaderCerebrum__Name")
    print(str(name.text))

    #Cào số sao
    try:
        star = crawl.find_element_by_class_name("HeaderCerebrum__Rating")
        width = star.size.get("width")
        if width == 8:
            print("Khong co sao")
        elif width == 24:
            print("Số sao:"+ str(1))
        elif width == 42:
            print("Số sao:"+ str(2))
        elif width == 62:
            print("Số sao:"+ str(3))
        elif width == 81:
            print("Số sao:"+ str(4))
        elif width == 92:
            print("Số sao:"+ str(4.5))
        elif width == 101:
            print("Số sao:"+ str(5))
    except:
        pass

    #Cào địa chỉ
    location = crawl.find_element_by_class_name("HeaderCerebrum__Location")
    print("Địa chỉ:")
    print(str(location.text))

    #Cào thông tin các loại phòng
    rooms = crawl.find_elements_by_class_name("MasterRoom")
    print("Các loại phòng:")
    for room in rooms:

        kind_room = room.find_element_by_class_name("MasterRoom-headerTitle--text").text
        print(str(kind_room))

        price = room.find_element_by_class_name("finalPrice.swap").text
        print(str(price))

        #payback = room.find_elements_by_class_name("ChildRoomsList-roomFeature.ChildRoomsList-roomFeature--green")
        #print(payback.pop().text.lower())

    #Cào thông tin về tiện nghi của khách sạn
    facilities = crawl.find_elements_by_class_name("sub-section.no-margin.sub-section-with-category")
    for facility in facilities:

        # Tìm và in phần vui chơi giải trí
        if facility.find_element_by_tag_name("h3").text == "Thư giãn & Vui chơi giải trí":
            print("Các dịch vụ giải trí:", end="\n")
            relax = facility.find_elements_by_tag_name("li")
            relax_list = []
            for rl in relax:
                if len(relax_list) < (len(relax) - 1):
                    print(rl.text, end=", ")
                    relax_list.append(rl.text)
                else:
                    print(rl.text)
                    relax_list.append(rl.text)

            spa = "Spa"
            if spa in relax_list:
                print("Dich vu spa:", 1)
            else:
                print("Dich vu spa:", 0)

            pool = "Bể bơi [ngoài trời]"
            if pool in relax_list:
                print("Hồ bơi:", 1)
            else:
                print("Hồ bơi:", 0)

        #Tìm và in phần ăn uống
        if facility.find_element_by_tag_name("h3").text == "Ăn uống":
            eating = facility.find_elements_by_tag_name("li")
            eating_list = []
            for eat in eating:
                eating_list.append(eat.text)

            room_service = "Dịch vụ phòng"
            if room_service in eating_list:
                print("Dịch vụ phòng: ", 1)
            else:
                print("Dịch vụ phòng: ", 0)

            room_service_24h = "Dịch vụ phòng [24 giờ]"
            if room_service_24h in eating_list:
                print("Dịch vụ phòng 24h: ", 1)
            else:
                print("Dịch vụ phòng 24h: ", 0)

            breakfast = "Bữa sáng [miễn phí]"
            if breakfast in eating_list:
                print("Bao ăn sáng:", 1)
            else:
                print("Bao ăn sáng:", 0)

        #Tìm và in phần đi lại
        if facility.find_element_by_tag_name("h3").text == "Đi lại":
            moving = facility.find_elements_by_tag_name("li")
            moving_list = []
            for mv in moving:
                moving_list.append(mv.text)

            park = "Bãi đỗ xe [miễn phí]"
            if park in moving_list:
                print("Đỗ xe miễn phí:", 1)
            else:
                print("Đỗ xe miễn phí:", 0)

    #Cào đánh giá trung bình
    try:
        reviews = crawl.find_element_by_class_name("ReviewScore-Number").text
        print("Đánh giá trung bình:", reviews)
    except:
        print("Không có đánh giá")
        pass
    print("\n")
crawl.close()
sys.stdout.close()