#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pandas import Series

def toUpperNoSpaces(row,column):
    return str(row[column]).replace(" ","").upper().strip()
def BoxOfficeNumber(row,column):
    return float(str(row[column]).replace("$","").replace(",","").strip())

# sources dfAll: principal dataset, dfOM: dataset of netflix movies, dfOs: dataset of netflix series
data_folder = "D:/COMPUTER SCIENCE/2 SEMESTER/information visualization/project/"
dfAll = pd.read_csv('netflixList.csv')
dfOM = pd.read_csv('netflixOM.csv')
dfOS = pd.read_csv('netflixOS.csv')

# Adding new columns to compare between datasets
dfOM['TitleToCompare'] = dfOM.apply(lambda row: toUpperNoSpaces(row,'Title'), axis = 1)
dfOS['TitleToCompare'] = dfOS.apply(lambda row: toUpperNoSpaces(row,'Title'), axis = 1)
dfAll['TitleToCompare'] = dfAll.apply(lambda row: toUpperNoSpaces(row,'Title'), axis = 1)

dfAll['GenreToCompare'] = dfAll.apply(lambda row: toUpperNoSpaces(row,'Genre'), axis = 1)
dfAll['BoxOfficeProfits'] = dfAll.apply(lambda row: BoxOfficeNumber(row,'Boxoffice'), axis = 1)

# ----------------------------------------- SECTION 1 ----------------------------------------------------
# add new column: Original, 1: is produced by netflix, 0: is not produced by netflix
# df: is the result dataset after matching
df = dfAll.assign(Original = dfAll.TitleToCompare.isin(pd.concat([dfOM.TitleToCompare,dfOS.TitleToCompare])).astype(int))

df['Year'] = pd.to_numeric(df['Release Date'].str[-4:])
# ----------------------------------------- SECTION 2 ----------------------------------------------------

# a) **** GRAPH 1: Netflix content rating trend by year ****

dfTrend = pd.DataFrame()
# get unique values from Genre
dfTemp = df['GenreToCompare'].drop_duplicates().str.split(',', expand=True)
dfGenre = dfTemp[0].drop_duplicates()
for col in dfTemp.columns:
    dfGenre = dfGenre.append(dfTemp[col].drop_duplicates(), ignore_index=True)
# drop duplicates and "Nan" value from Genre unique values 
dfGenre = dfGenre.drop_duplicates().dropna().drop(dfGenre.index[10])

filterYear = df['Year'] >= 2010
for genre in dfGenre:
    filterGenre = df['GenreToCompare'].str.contains(pat = genre)
    dfTrend = dfTrend.append(df[['Original','Title','Series or Movie','Year','GenreToCompare','IMDb Score']].where(filterYear & filterGenre, inplace = False).dropna().drop_duplicates().groupby(['Year','Original','Series or Movie']).agg(Films = ('Title', 'count'), Rating = ('IMDb Score', 'mean')).assign(Genre = genre))

dfTrend = dfTrend.reset_index()
#export to csv file
dfTrend.sort_values(['Genre','Year','Original','Series or Movie'], ascending=[True,True,True,True], inplace=True)
dfTrend.to_csv(data_folder + 'trend_genre.csv', index = False, header=True)

# b) **** GRAPH 2: Box office contribution ****

dfBoxOffice = pd.DataFrame()

for genre in dfGenre:
    filterGenre = df['GenreToCompare'].str.contains(pat = genre)
    dfBoxOffice = dfBoxOffice.append(df[['Original','Genre','Title','GenreToCompare','Series or Movie','IMDb Score','Year','BoxOfficeProfits']].where(filterYear & filterGenre, inplace = False).dropna(how='all').drop_duplicates().assign(MainGenre = genre))
dfBoxOffice.sort_values(['MainGenre','Year','Original','Series or Movie'], ascending=[True,True,True,True], inplace=True)
# changing 'Nan' values to '0'
dfBoxOffice['BoxOfficeProfits'] = dfBoxOffice['BoxOfficeProfits'].fillna(0)
dfBoxOffice['IMDb Score'] = dfBoxOffice['IMDb Score'].fillna(0)
#export to csv file
dfBoxOffice[['MainGenre','Year','Original','Series or Movie','IMDb Score','BoxOfficeProfits','color','Title','Genre']].to_csv(data_folder + 'boxOffice.csv', index = False, header=True)

# c) **** GRAPH 3: Popular Directors of the year based on the rating **** 

df3 = df[['Director','Year','IMDb Score','Genre','Original','Series or Movie']]
df3 = df3.dropna()
# Split the Genre column into multiple rows
s = df3['Genre'].str.split(',').apply(Series, 1).stack()
s.name = 'Genre'
s.index = s.index.droplevel(-1)
del df3['Genre']
df3 = df3.join(s)
# Calculate the mean rating for specific year, genre and director
dfg = df3.groupby(['Year','Genre','Original','Series or Movie','Director'])['IMDb Score'].mean().to_frame('Avg Rating').reset_index()
df5 = dfg.groupby(['Genre','Year']).apply(lambda x: x.sort_values(['Avg Rating'],ascending=False))
df5 = df5.drop(['Genre','Year'],1)
df5 = df5.reset_index()
df5 = df5.drop(['level_2'],1)
# retrieve the name of first director and make a separate column
res =[]
for row in df5['Director']:
    res.append(row.split(',')[0])
df5['dir1'] = res
# rename for further visualization
df5.columns = ['Genre','Year','Original','Series or Movie','Director','Y','X']
# consider only years from 1990
df5 = df5[df5['Year']>1990]
df5.to_csv(data_folder + 'directors3new.csv',index= False)

# d) **** GRAPH 4: Popular Writers of the year based on the rating **** 

dfWriter = pd.DataFrame()

#filtering first writer
df['First_Writer'] = df.Writer.str.split(', ').str[0]
for genre in dfGenre:
    filterGenre = df['GenreToCompare'].str.contains(pat = genre)
    dfWriter = dfWriter.append(df[['Original','Writer','Series or Movie','Year','GenreToCompare','IMDb Score','Title','First_Writer']].where(filterYear & filterGenre, inplace = False).dropna().drop_duplicates().groupby(['Year','Original','Series or Movie','Writer','Title','First_Writer']).agg(Films = ('Title', 'count'),Writers = ('Writer','count'),Rating = ('IMDb Score', 'mean')).assign(Genre = genre)).sort_values(by=['Rating'],ascending=False)
dfWriter = dfWriter.reset_index()
#export to csv file
dfWriter.to_csv(data_folder + 'writer_fulldata.csv', index = False, header=True)

