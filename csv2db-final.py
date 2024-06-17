import pandas as pd
import sqlite3 as sql
from functools import partial

def IDnobel(row):
    return nobelID[(row["category"],row["awardYear"])]

def ID(dict, field, row):
    return dict[row[field]]

def portion2float(row):
    frac = row["portion"]
    if frac == "1": return 1
    a,b = frac.split("/")
    return int(a)/int(b)

complete = pd.read_csv("complete-a.csv")

# This Section merges birth_location to organization location
complete.loc[complete["birth_city"].isnull(), ["birth_city"]] = complete["org_founded_city"]
complete.loc[complete["birth_country"].isnull(), ["birth_country"]] = complete["org_founded_country"]
complete.loc[complete["birth_continent"].isnull(), ["birth_continent"]] = complete["org_founded_continent"]

# Changes Null_location to "Unspecified"
complete.loc[complete["birth_city"].isnull(), ["birth_city"]] = "Unspecified"
complete.loc[complete["birth_country"].isnull(), ["birth_country"]] = "Unspecified"
complete.loc[complete["birth_continent"].isnull(), ["birth_continent"]] = "Unspecified"

con = sql.connect("Nobels.db")
cur = con.cursor()

# Category
categories = complete.loc[:,["category","categoryFullName"]].drop_duplicates(ignore_index=True)
categories.index += 1
catID = {}
for i,category in categories.iterrows():
     catID[category["category"]] = i
res = cur.executemany(" INSERT INTO category VALUES (?,?,?)", categories.itertuples(name=None))
     
# Nobels
nobels = complete.loc[:,["category","awardYear","motivation","prizeAmount","prizeAmountAdjusted","prizeStatus","dateAwarded"]].drop_duplicates(ignore_index=True)
nobels.index += 1
nobelID = {}
for i,nobel in nobels.iterrows():
    nobelID[(nobel["category"],nobel["awardYear"])] = i
nobels["category"] = nobels.apply(partial(ID, catID, "category"), axis= 1) # replaces Category name with Category id
print(nobelID)
print(nobels.head())
res = cur.executemany("INSERT INTO nobel VALUES (?,?,?,?,?,?,?,?)" , nobels.itertuples(name=None))

#Continent
continents = complete.loc[:, ["birth_continent"]].drop_duplicates(ignore_index=True)
continents.index += 1
continentID = {}
for i,continent in continents.iterrows():
    continentID[continent['birth_continent']] = i

# Countries    
countries = complete.loc[:, ["birth_continent","birth_country"]].drop_duplicates(ignore_index=True)
countries["birth_continent"] = countries.apply(partial(ID, continentID, "birth_continent"), axis=1)
countries.index += 1
countryID = {}
for i,country in countries.iterrows():
    countryID[country["birth_country"]] = i

# Cities
cities = complete.loc[:, ["birth_country","birth_city"]].drop_duplicates(ignore_index=True)
cities.index += 1
cities["birth_country"] = cities.apply(partial(ID, countryID, "birth_country"),axis=1)
cityID = {}
for i,city in cities.iterrows():
    cityID[city["birth_city"]] = i

# SQL commands for City, Country and Continent
res = cur.executemany("INSERT INTO continent VALUES (?,?)", continents.itertuples(name=None))
res = cur.executemany("INSERT INTO country VALUES (?,?,?)", countries.itertuples(name=None))
res = cur.executemany("INSERT INTO city VALUES (?,?,?)", cities.itertuples(name=None))

#People
laureatesFull = complete.loc[:, ["name","birth_date","gender","affiliation_1","death_date","orgName","nativeName","acronym","birth_city","ind_or_org","org_founded_date"]].drop_duplicates(ignore_index=True)
laureatesFull.index += 1
laureateID = {}
for i,laureate in laureatesFull.iterrows():
    laureateID[laureate["name"]] = i
laureates = laureatesFull.apply(partial(ID, cityID, "birth_city"),axis=1)
print(laureates)
res = cur.executemany("INSERT INTO laureate VALUES (?,?)", zip(laureates.index,laureates))

#Instiution
people = laureatesFull.loc[laureatesFull["ind_or_org"] == "Individual", ["name","birth_date","gender","affiliation_1","death_date"]]
res = cur.executemany("INSERT INTO person VALUES (?,?,?,?,?,?)", people.itertuples(name=None))
institutions = laureatesFull.loc[laureatesFull["ind_or_org"] == "Organization", ["orgName", "nativeName", "acronym","org_founded_date"]]
res = cur.executemany("INSERT INTO institution VALUES (?,?,?,?,?)", institutions.itertuples(name=None))

#Prize
prize = complete.loc[:, ["awardYear", "category", "portion", "name"]]
prize["nobelID"] = prize.apply(IDnobel, 1)
prize["laureateID"] = prize.apply(partial(ID, laureateID, "name"), axis=1)
prize["portion"] = prize.apply(portion2float, axis=1)
prize = prize.loc[:, ["nobelID", "laureateID", "portion"]]
res = cur.executemany("INSERT INTO prize VALUES (?,?,?)", prize.itertuples(name=None, index=False))
con.commit()
