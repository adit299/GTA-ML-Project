import bs4, requests, csv

mar_html = 'https://markham.listing.ca/real-estate-price-history.htm'


def get_listings(html, n):
    """
    Given an HTML (as a string) and the number, returns a list containing
    lists of all the table elements and their values

    """
    rows = []
    res = requests.get(html)
    bs4_obj = bs4.BeautifulSoup(res.text, features="html.parser")
    table = bs4_obj.find_all('table')[n]

    for r in table:
        try:
            rows.append(r.text)
        except:
            pass
    return rows


def write_to_csv(lst, file):
    """
    Given the data from the lists, writes them to an open CSV file

    """
    with open(file, mode='a') as csv_file:
        writer = csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

        for r in lst:
            writer.writerow(r.split('\n'))


if __name__ == '__main__':
    # table = get_listings(mar_html, 1)
    # print(table)
    # write_to_csv(table, 'housing_data.csv')

    lst = []
    res = requests.get(mar_html)
    bs4_obj = bs4.BeautifulSoup(res.text, features="html.parser")
    my_divs = bs4_obj.findAll("div", {"class": "menu_item"})

    for r in range(4, 19):
        if my_divs[r].text[:my_divs[r].text.find(' ')].lower() == \
                "richmond":
            lst.append("richmond-hill")
        else:
            lst.append(my_divs[r].text[:my_divs[r].text.find(' ')].lower())

    b_html = "https://"
    e_html = ".listing.ca/real-estate-price-history.htm"

    for city in lst:
        for n in range(1, 12):
            table = get_listings(b_html + city + e_html, n)
            print("Loading " + city + " data.....")
            write_to_csv(table, city + '_data.csv')

