import requests
import os
from bs4 import BeautifulSoup
from time import sleep
from tqdm import tqdm
import shutil

name        ="Circle of Inevitability"
headers     ={ 'User-Agent': 'Mozilla/4.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36'}
# chapter link without number:
link        ="https://readnovel.eu/chapter/lord-of-mysteries-2-circle-of-inevitability-"
folderName  = name
# starts by 1!
startch     = 1150
endch       = 1180
removallist =["&lt;sup&gt;1&lt;/sup&gt;","&lt;sup&gt;2&lt;/sup&gt;","&lt;sup&gt;3&lt;/sup&gt;","Please continue reading on ΒOXΝʘVEL.ϹΟM .","<nulli>","</nulli>"]

def getraw(chapter):
    return requests.get( link + str(chapter), headers=headers).text

def unhtml(html):
    soup = BeautifulSoup(html,"html.parser")
    text = ""                                                                          
    for el in soup.find_all(id="chapterText"):                                               
        if el.string == None:
            continue
        paragraph = el.string
        for termination in removallist:
            paragraph.replace(termination,"")

        text += paragraph + "\n\n"
    return text

def fileName(chapterNumber):
    formated = "0000"[0:-len(str(chapterNumber))] + str(chapterNumber)
    return "Chapter" + formated

def addLink(chaptertext,chapternumber):
    if chapternumber == endch:
        return chaptertext
    return chaptertext + f"[[Novels/{name}/{fileName(chapternumber + 1)}|next chapter]]" 

if __name__ == "__main__":
    os.makedirs(folderName,exist_ok=True)
    
    for chapter in tqdm(range(startch,endch + 1)):
        with open(os.path.join(folderName,fileName(chapter) + ".md"), 'w', encoding="utf-8") as f:
            f.write(addLink(unhtml(getraw(chapter)),chapter))
    shutil.make_archive(name,"zip",folderName)
