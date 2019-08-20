import bs4, requests, csv, math


def get_data(html, n, city):
    """
    Given an HTML, extracts the data required to write to a CSV (in List form)
    then writes to a CSV


    :param html:
    :return:
    """
    global lat, lon
    # Extracting the data from the address itself, from the listing
    res = requests.get(html)
    bs4_obj = bs4.BeautifulSoup(res.text, features="html.parser")
    address_table = bs4_obj.findAll("div", {"class": "slt_address"})
    price_table = bs4_obj.findAll("div", {"class": "slt_price"})
    baths_table = bs4_obj.findAll("div", {"class": "slt_baths"})
    beds_table = bs4_obj.findAll("div", {"class": "slt_beds"})

    # Extracting the rest of the data by accessing the listing itself
    house_html = address_table[n].find('a', href=True)['href']
    print "House_Html: ", house_html
    house_res = requests.get(house_html)
    house_obj = bs4.BeautifulSoup(house_res.text, features="html.parser")
    features_table = house_obj.findAll("div", {"class": "lpc15"})

    # 1) Address
    # 2) Postal Code
    # 3) Latitude
    # 4) Longitude
    # 5) City
    # 6) Municipality
    # 7) Price
    # 8) Bathrooms
    # 9) Beds
    # 10) Height
    # 11) Kitchens
    # 12) Parking Spaces
    # 13) Lot sizes
    # 14) Total Lot Size
    # 15) Basement
    # 16) House HTML

    # Basement
    try:
        if "Full" in features_table[3].text.split(" ") or "Finished" in features_table[3].text.split(" ")\
                or "Walk-Up" in features_table[3].text.split(" "):
            basement = "Finished"
        elif "Unfinished" in features_table[3].text.split(" "):
            basement = "Unfinished"
        else:
            basement = "No Basement"
    except:
        basement = ""

    # Postal Code
    try:
        postal_code = features_table[0].text.split(',')[-1].strip().split(' ')[-1]
        str(postal_code)
    except:
        postal_code = ""

    # Latitude and Longitude
    lat_file = csv.reader(open("Canadian Postal Codes.csv", "rb"), delimiter=",")
    try:
        for row in lat_file:
            if postal_code == row[0]:
                lat = row[2]
                lon = row[3]
    except:
        lat = ""
        lon = ""

    # Height
    try:
        if "Bungalow-Raised" in features_table[1].text.split(","):
            height = 1
        elif features_table[1].text.split(',')[0][0] == 'B':
            height = 1
        else:
            height = features_table[1].text.split(',')[0][0]
        int(height)
    except:
        height = ""

    # Bedrooms
    try:
        if beds_table[n].text[1] == "+":
            beds = str(int(beds_table[n].text[0]) + int(beds_table[n].text[2]))
        else:
            beds = beds_table[n].text[0]
    except:
        beds = ""

    # Kitchens
    try:
        if features_table[1].text.split(',')[2].strip()[2] == "+":
            kitchen = str(int(features_table[1].text.split(',')[2].strip()[0]) + int(features_table[1].text.split(',')[2].strip()[4]))
        else:
            kitchen = features_table[1].text.split(',')[2].strip()[0]
    except:
        kitchen = ""

    # Lot Size
    try:
        lot_size = str(float(features_table[2].text.split('x')[0]) * float(
                    features_table[2].text.split('x')[1]))
    except:
        lot_size = ""

    # Parking Spaces
    try:
        parking_spaces = features_table[1].text.split(',')[2][-16]
        int(parking_spaces)
    except:
        parking_spaces = ""

    # Total Lot Size
    try:
        lot_size_dim = features_table[2].text
        int(lot_size_dim[0])
    except:
        lot_size_dim = ""

    return [features_table[0].text,
            postal_code,
            lat,
            lon,
            city.capitalize(),
            features_table[0].text.split(',')[1].strip(),
            price_table[n].text[1:-4],
            baths_table[n].text[0],
            beds,
            height,
            kitchen,
            parking_spaces,
            lot_size_dim,
            lot_size,
            basement,
            house_html]


def write_to_csv(lst, file):
    """
    Given the data from the lists, writes them to a CSV file

    """
    with open(file, mode='a') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(lst)


def scrape_from_page(entries, city_num, csv_file, beg_page_html, end_page_html):
    """
    Given the number of house entries in a particular city, scrapes all of them
    and writes them to a CSV file


    :param page_num_html:
    :param entries:
    :return:
    """
    j = 2
    while j < entries:
        page_num_html = beg_page_html + str(j) + end_page_html
        res_2 = requests.get(page_num_html)
        bs4_obj_2 = bs4.BeautifulSoup(res_2.text, features="html.parser")
        address_table_2 = bs4_obj_2.findAll("div", {"class": "slt_address"})
        for i in range(len(address_table_2)):
            write_to_csv(get_data(page_num_html, i, city_lst[city_num]), csv_file)
        j += 1
        print "j: ", j


if __name__ == '__main__':
    # Just some code to be able to extract all the different city names which
    # I will be scraping, as well as a dictionary containing the city name and
    # the associated number of houses in that city. I will also create a
    # seperate dictionary containing the beginning and ending HTMLs to navigate
    # to each of the pages of the various cities

    bare_html = "https://listing.ca/"
    city_lst = []
    city_dict = {}
    city_html = {}

    res = requests.get(bare_html)

    res_2 = requests.get(bare_html)
    bs4_obj_2 = bs4.BeautifulSoup(res_2.text, features="html.parser")
    nums = bs4_obj_2.findAll("sup")

    bs4_obj = bs4.BeautifulSoup(res.text, features="html.parser")
    my_divs = bs4_obj.findAll("div", {"class": "menu_item"})

    for r in range(4, 19):
        if my_divs[r].text[:my_divs[r].text.find(' ')].lower() == \
                "richmond":
            city_lst.append("richmond-hill")
        elif my_divs[r].text[:my_divs[r].text.find(' ')].lower() == \
                "kawartha":
            city_lst.append("kawartha-lakes")
        else:
            city_lst.append(my_divs[r].text[:my_divs[r].text.find(' ')].lower())

    for n in range(len(nums[4:19])):
        try:
            city_dict[city_lst[n]] = int(nums[4:19][n].text)
        except:
            num = int(str(nums[4:19][n].text).replace('.', '').replace('k', '')) * 10
            city_dict[city_lst[n]] = num

    # Setting up the beginning and ending HTMLs of each of the cities
    city_html[city_lst[0]] = ["https://listing.ca/mls/?.1n.........", "..$"]
    city_html[city_lst[1]] = ["https://listing.ca/mls/?.v.........", "..$"]
    city_html[city_lst[2]] = ["https://listing.ca/mls/?.10.........", "..$"]
    city_html[city_lst[3]] = ["https://listing.ca/mls/?.17.........", "..$"]
    city_html[city_lst[4]] = ["https://listing.ca/mls/?.1s.........", "..$"]
    city_html[city_lst[5]] = ["https://listing.ca/mls/?.m.........", "..$"]
    city_html[city_lst[6]] = ["https://listing.ca/mls/?.3b.........", "..$"]
    city_html[city_lst[7]] = ["https://listing.ca/mls/?.x.........", "..$"]
    city_html[city_lst[8]] = ["https://listing.ca/mls/?.3d.........", "..$"]
    city_html[city_lst[9]] = ["https://listing.ca/mls/?.l.........", "..$"]
    city_html[city_lst[10]] = ["https://listing.ca/mls/?.11.........", "..$"]
    city_html[city_lst[11]] = ["https://listing.ca/mls/?.3f.........", "..$"]
    city_html[city_lst[12]] = ["https://listing.ca/mls/?.cy.........", "..$"]
    city_html[city_lst[13]] = ["https://listing.ca/mls/?.3h.........", "..$"]
    city_html[city_lst[14]] = ["https://listing.ca/mls/?.16.........", "..$"]

    # Setting up my HTML and readying myself to write the data from the website
    b_html = "https://"
    e_html = ".listing.ca"

    f = open('housing_data.csv', 'w')
    f.write('Address,Postal Code,Latitude,Longitude,City,'
            'Neighbourhood,Price(in CAD),# of Bathrooms,# of Bedrooms,'
            'Height(in stories),# of Kitchens,# of Parking Spaces,Lot-Size(in km^2), '
            'Total Lot Size(in km^2),Basement(finished or not),House HTML\n')
    f.close()

    # Scrapes data from the first page of each city,
    # since the URL is slightly different than the other pages
    for j in range(len(city_lst)):
        beg_html = b_html + city_lst[j] + e_html
        res = requests.get(beg_html)
        bs4_obj = bs4.BeautifulSoup(res.text, features="html.parser")
        address_table = bs4_obj.findAll("div", {"class": "slt_address"})
        for i in range(len(address_table)):
            write_to_csv(get_data(beg_html, i, city_lst[j]), 'housing_data.csv')

    # After the first page is fully scraped of each city, we need to go to the rest of the
    # pages to fully scrape all the data

    for k in range(len(city_lst)):
        scrape_from_page(int(math.ceil(city_dict[city_lst[k]] / 20.0)),
                         k, "housing_data.csv", city_html[city_lst[k]][0],
                         city_html[city_lst[k]][1])

