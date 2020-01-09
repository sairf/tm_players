import pandas as pd
import requests
from bs4 import BeautifulSoup
import re
from sqlalchemy import create_engine
import pymysql

headers = {'User-Agent': 
           'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36'}

#get europe leagues page
page = "https://www.transfermarkt.pt/wettbewerbe/europa"
pageTree = requests.get(page, headers=headers)
pageSoup = BeautifulSoup(pageTree.content, 'html.parser')

leagues = pageSoup.find_all("a", href=re.compile("/startseite/wettbewerb/"), title=re.compile("."))

#'#':playersNum, 'Jogador':playersName, 'Posição':playersPos, 'Data Nascimento':playersDate, 'Nacionalidade':playersNat
df = pd.DataFrame(columns=['Num', 'Jogador', 'Posicao', 'Data_Nascimento', 'Nacionalidade'])
#print(df)
#get teams page by league (0=Premier League ... 5=Liga NOS)
for league in leagues:
    clubsPage = "https://www.transfermarkt.pt"+league.get("href")
    clubsTree = requests.get(clubsPage, headers=headers)
    clubsSoup = BeautifulSoup(clubsTree.content, 'html.parser')

    clubList = clubsSoup.find_all("a", href=re.compile("startseite/verein/.*/saison_id"))
    clubUniqueList = []
    for club in clubList:
        if club.get("href") not in clubUniqueList:
            clubUniqueList.append(club.get("href"))

    playersNum = []
    playersName = []
    playersPos = []
    playersDate = []
    playersNat = []
    #get players page by team (0=SLB ...)
    for i,club in enumerate(clubUniqueList):
        playersPage = "https://www.transfermarkt.pt"+club
        playersTree = requests.get(playersPage, headers=headers)
        playersSoup = BeautifulSoup(playersTree.content, 'html.parser')

        #get shirt numbers and append to dataframe
        playersList = playersSoup.find_all("div", class_="rn_nummer")
        for i,tag in enumerate(playersList):
            playersNum.append(tag.text)
            if i == 1:
                break

        #get player names and append to DF
        playersList = playersSoup.find_all("td", itemprop="athlete")
        for i,tag in enumerate(playersList):
            playersName.append(tag.text)
            if i == 1:
                break

        #get player position and append to DF
        playersList = playersSoup.find_all("table", class_="inline-table")
        for i,table in enumerate(playersList):
            playersPos.append(table.find_all("tr")[-1].find("td").text)
            if i == 1:
                break

        #get player birthdate and append to DF
        playersList = playersSoup.find_all("table", class_="items")[0].find_all(lambda tag: tag.name == 'td' and tag.get('class') == ['zentriert'])
        for i,td in enumerate(playersList):
            if td.text:
                playersDate.append(td.text.split()[0])
            if i == 1:
                break

        #get player nationality and append to DF
        playersList = playersSoup.find_all("table", class_="items")[0].find_all("tr", class_=["odd", "even"])
        for i,tr in enumerate(playersList):
            playerNation = ""
            nations = tr.find_all("img", class_="flaggenrahmen")
            #print(nations)
            if len(nations) > 1:
                for n in nations:
                    playerNation = playerNation + "/" + n.get("title")
                    #print(n.get("title"))
                playerNation = playerNation[1:]
            else:
                playerNation = nations[0].get("title")
            playersNat.append(playerNation)
            if i == 1:
                break
        #print(playersName)
        break
    playersDic = {'Num':playersNum, 'Jogador':playersName, 'Posicao':playersPos, 'Data_Nascimento':playersDate, 'Nacionalidade':playersNat}
    #print(playersDic)
    df = df.append(playersDic, ignore_index=True)
    print(df)
    break

#create sqlalchemy engine
#engine = create_engine("mysql+pymysql://root:tElM0!5/@localhost/stats"
#                       .format(user="root",
#                               pw="tElM0!5/",
#                               db="stats"))

# Insert whole DataFrame into MySQL
#df.to_sql('tm_players', con = engine, if_exists = 'append', index=False)
