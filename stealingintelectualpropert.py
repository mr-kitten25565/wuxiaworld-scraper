import requests
import os
from bs4 import BeautifulSoup
from time import sleep

headers= { 'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36'}
folderName = "OmniscientReadersViewpoint"

def getraw(chapter):
    url = f"https://wuxiaworld.eu/chapter/omniscient-readers-viewpoint-{chapter}" 
    response = requests.get(url, headers=headers)
    return response.text

def unhtml(html):
    soup = BeautifulSoup(html,"html.parser")
    paragraphs = []
    for el in soup.find_all(id="chapterText"):
        paragraphs.append(str(el)[65:-6])

    text = "\n\n".join(paragraphs)
    return text

def fileName(chapterNumber):
    formated = "0000"[0:-len(str(chapterNumber))] + str(chapterNumber)
    return "Chapter" + formated

if __name__ == "__main__":
    os.mkdir(folderName)
    for i in range(1,552):
        sleep(1)
        with open(os.path.join(folderName,fileName(i) + ".md"), 'w', encoding="utf-8") as f:
            f.write(unhtml(getraw(i)))
        print(i)
 
