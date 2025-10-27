import os

book = os.listdir("/home/albert/Public/Program/OmniscientReadersViewpoint")
for File in book:
    with open("OmniscientReadersViewpoint/" + File, "a") as myfile:
        myfile.write("[[Novels/OmniscientReadersViewpoint/Chapter"+ "0"*(4-len(str(int(File[7:-3])+1))) + str(int(File[7:-3])+1)+ "|Next Chapter]]")
       
