import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import time

headers = { "Accept-Language": "en-US, en;q=0.5" }

#base url which is the first page *not necessarily used in this code
url = "https://www.imdb.com/search/title/?count=100&groups=top_1000&sort=user_rating"

listurl = ["1","2","3","4","5","6","7","8","9"] #list of numbering for the base url with pattern

urllength = len(listurl) # the length of the list  *to use for iteration

i = 0

#baseurl that have pattern for next page iteration
nextpageurl = "https://www.imdb.com/search/title/?groups=top_1000&sort=user_rating,desc&count=100&start={}01&ref_=adv_prv"

#list of data that will be stored
#initialization is put outside the while loop to avoid multiple initialization and replace the previous data.
title = []
year_publish = []
duration = []
genre = []
imdb_ratings = []
metascores = []
votes = []
usdollar_gross = []
ranking = []

start_time = time.time()

while i < urllength: #iterate the code based on the length of the url list

    results = requests.get(nextpageurl.format(listurl[i]),headers=headers) #concatenation of nextpageurl and the number patter in the url

    soup = BeautifulSoup(results.text,"html.parser")

    #print(soup.prettify())

    movie_divcontainer = soup.find_all('div', class_ = "lister-item mode-advanced")

    #initiate the for loop 

    #variable container is for every div container that will be stored in movie_divcontainer

    for container in movie_divcontainer: #loop through all div container in the current page

        title_name = container.h3.a.text
        title.append(title_name) #append the title name into the title list initialized earlier


        year_publishscrape = container.h3.find('span' , class_ = "lister-item-year").text
        year_publish.append(year_publishscrape)

        duration_scrape = container.find('span', class_ = 'runtime').text if container.p.find('span', class_ = 'runtime') else '-'
        duration.append(duration_scrape)

        genre_scrape = container.find('span', class_ = 'genre').text 
        genre.append(genre_scrape)

        imdb_ratings_scrape = float(container.strong.text)
        imdb_ratings.append(imdb_ratings_scrape)

        metascores_scrape = container.find('span',class_ = "metascore favorable").text if container.find('span', class_ = "metascore favorable") else '0'
        metascores.append(metascores_scrape)

        #create new variable to hold two tags with the same name

        nv = container.find_all('span', attrs = {'name':'nv'})

        votes_scrape = nv[0].text
        votes.append(votes_scrape)


        gross_scrape = nv[1].text if len(nv) > 1 else '-'
        usdollar_gross.append(gross_scrape)

        #time taken for 1 page to be done by calculating the (end time - start time).
        end_time = time.time()

        #ranking is based on ratings
        #still not found how to do this
    
    i += 1

    print("Page done scraped : " , i)
    print("Time taken for {} page ... %s seconds".format(i) % round((end_time - start_time),2))

print('Time taken to complete scraping ... %s seconds' % round(time.time()-start_time,2))

'''
print(title)
print(year_publish)
print(duration)
print(genre)
print(imdb_ratings)
print(metascores)
print(votes)
print(usdollar_gross)
'''



#creating the DataFrame
imdbMoviesList = pd.DataFrame({
    'Movie Title' : title,
    'Year' : year_publish,
    'Genre' : genre,
    'Movie Duration' : duration,
    'Ratings' : imdb_ratings,
    'Metascore' : metascores,
    'Votes' : votes,
    'grossMillions($)' : usdollar_gross,
})

#Data Cleaning

imdbMoviesList['Year'] = imdbMoviesList['Year'].str.extract('(\d+)').astype(int) #extract only the digit and convert the data type to integer

imdbMoviesList['Genre'] = imdbMoviesList['Genre'].str.replace(',','').map(lambda x: x.lstrip('\n')) #lstrip is used to strip \n from the left side

imdbMoviesList['Movie Duration'] = imdbMoviesList['Movie Duration'].str.extract('(\d+)').astype(int) #extract only the digit and convert the data type to integer

imdbMoviesList['Metascore'] = imdbMoviesList['Metascore'].astype(int) #convert the data type to integer

imdbMoviesList['Votes'] = imdbMoviesList['Votes'].str.replace(',','').astype(int) #replace the ',' to nothing and change the data into integer

imdbMoviesList['grossMillions($)'] = imdbMoviesList['grossMillions($)'].map(lambda x: x.lstrip('$').rstrip('M')) #lstrip the $ sign from the left side and rstrip the 'M' from the right side

imdbMoviesList['grossMillions($)'] = pd.to_numeric(imdbMoviesList['grossMillions($)'],errors='coerce') #change the data to numeric value. Instead of using astype(float), this method help to change the whole column including the '-' data to NaN (not a value).

print(imdbMoviesList.dtypes)

print(imdbMoviesList)

file_path = r'insert_your_path_here\ '
 
imdbMoviesList.to_csv(file_path + 'imdbMoviesList.csv')