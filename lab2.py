import pandas as pd
import codecs
from bs4 import BeautifulSoup
import os


def main():
    # rename_files() # used once to rename files
    bios_fold = os.listdir("data/biogramy/")
    orgs_fold = os.listdir("data/orgs/")

    bios_df, orgs_df = create_dfs()

    for item in bios_fold:
        name = item[:-5]
        extract_bio("data/biogramy/" + item, name, bios_df)

    for item in orgs_fold:
        name = item[:-5]
        extract_org("data/orgs/" + item, name, orgs_df)

    print(bios_df.head(3))
    print(orgs_df.head(3))

    bios_df.to_csv("bios.csv", encoding="utf-8")
    orgs_df.to_csv("orgs.csv", encoding="utf-8")
    return


def rename_files():
    # use once to rename files
    bios_fold = os.listdir("data/biogramy/")
    orgs_fold = os.listdir("data/orgs/")

    for item in bios_fold:
        name = item[item.find(",") + 1: item.find(".")].replace("-", " ")
        try:
            os.rename("data/biogramy/"+item, "data/biogramy/"+name+".html")
        except FileExistsError:
            os.rename("data/biogramy/"+item, "data/biogramy/" + name + "1" + ".html")

    # orgs had more than double duplicates
    for item in orgs_fold:
        name = item[item.find(",") + 1: item.find(".")].replace("-", " ")
        try:
            os.rename("data/orgs/"+item, "data/orgs/"+name+".html")
        except FileExistsError:
            for i in range(1, 15):
                try:
                    os.rename("data/orgs/"+item, "data/orgs/"+name + str(i) + ".html")
                    continue
                except FileExistsError:
                    continue

def create_dfs():
    bios_fold = os.listdir("data/biogramy/")
    orgs_fold = os.listdir("data/orgs/")

    bios = []
    for item in bios_fold:
        bios.append(item[:-5])

    orgs = []
    for item in orgs_fold:
        orgs.append(item[:-5])

    # below used index file to verify same information
    # Splice list of html items from the first name to last name
    # bios = bios[bios.index('Abgarowicz Łukasz') : bios.index('Żyliński Tadeusz') + 1]
    # orgs = orgs[orgs.index('1 i 3 V 1983 w Nowej Hucie i Krakowie') : orgs.index('Żywią i Bronią') + 1]

    # Now let's put all the bios and orgs into separate dataframes
    # Entities will be rows with their details being columns
    # bios details will be dictionaries of places as keys with list of years being values
    bios_df = pd.DataFrame({"name": bios, "content": None, "author": None, "birth": None, "deathday": None, "region": None,
                            "education": None, "groups": None, "imprisonment": None, })
    orgs_df = pd.DataFrame({"name": orgs, "content": None, "author": None, "region": None,
                            "people": None, "start": None, "end": None})

    bios_df.set_index("name", inplace=True)
    orgs_df.set_index("name", inplace=True)

    return bios_df, orgs_df



def extract_bio(file, name, df):
    index = name
    bio = codecs.open(file, 'r', encoding='utf-8')
    bio = BeautifulSoup(bio, 'html.parser')
    try:
        df.content[index] = get_content(bio)
        df.author[index] = get_authors(bio)
        b_date, d_date = get_dates(bio)
        df.birth[index] = {get_birthloc(bio): b_date}
        df.deathday[index] = d_date
        df.region[index] = get_region(bio)
    except ValueError:
        print(f"Name Error: Couldn't find {name}")
        return
    return


def extract_org(file, name, df):
    index = name
    org = codecs.open(file, 'r', encoding='utf-8')
    org = BeautifulSoup(org, 'html.parser')

    try:
        df.content[index] = get_content(org)
        df.author[index] = get_authors(org)
        df.region[index] = get_region(org)
    except ValueError:
        print(f"Name Error: Couldn't find {name}")
        return
    return


def get_content(html):
    cont = []
    for item in html.find_all("p"):
        # if item is a link break
        if item.get_text() == " " and cont != []:
            break
        # print(item.get_text())
        cont.append(item.get_text())
    return cont


def get_authors(html):
    # Find authors of bio if any
    authors = html.find("p", "author").get_text().split("|") if html.find("p", "author").get_text() else None
    return authors


def get_birthloc(html):
    try:
        # Birth places have high variability with villages being near cities
        # For the sake of generalized statistics, we will only take note of the nearest city
        birth_loc = html.find("p", "icon-placeholder", 1).contents[1].string[1:]
        birth_loc.replace(r"\(.*\)", "")
        if "k." in birth_loc:
            birth_loc = birth_loc[birth_loc.index(".") + 2:]
    except IndexError:
        birth_loc = None
    return birth_loc


def get_dates(html):
    # Find important dates
    b_date = None
    d_date = None
    for date in html.find_all("p", "icon-calendar"):
        text = date.get_text()
        if "urodzenia" in text:
            b_date = text[text.index(" ") + len("urodzenia") + 2:]
        if "śmierci" in text:
            d_date = text[text.index(" ") + len("śmierci") + 2:]
    return b_date, d_date


def get_region(html):
    # Find region
    region = None
    for item in html.find_all("a"):
        # if item is a link break'
        text = item.get_text()
        if "Region" in text:
            region = text[text.index(" ") + 1:]
    return region


# abrv_fold = os.listdir("data/abrv/")

'''
# Redirect path to tesseract.exe
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

for item in abrv_fold:
    img = cv2.imread("data/abrv/" + item)
    text = pytesseract.image_to_string(img)
    print(text)
    '''

if __name__ == "__main__":
    main()