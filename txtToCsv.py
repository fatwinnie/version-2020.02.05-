import csv


with open('2.csv','w',newline='', encoding ='utf-8') as csvfile:
    writer = csv.writer(csvfile)    # 建立csv檔案寫入器，writer為csv文件寫入對象
    data = open('2.txt', encoding ='utf- 8')    # txt文件內容存入data中
    for each_line in data:
        a = each_line.split('\t')   #把txt每一行的數據轉換為list, split
        writer.writerow(a)  #把list添加到csv文件中
    data.close()

    # https://www.chzzz.club/post/50.html
    # newline-http://pykynix.blogspot.com/2013/01/csvwriterow.html
   