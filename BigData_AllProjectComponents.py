# Imports :)
import pandas as pd
import requests
from urllib2 import urlopen
from bs4 import BeautifulSoup
import sqlite3
import csv as csv
from IPython.core.display import Image
from gensim.models import Word2Vec

# Base yelp website
BASE_YELP = "http://www.yelp.com/"

# Base website for type of food - sushi for example 
BASE_SUSHI = "http://www.yelp.com/search?find_desc=sushi&find_loc=Reno%2C+NV&ns=1"

# Given a yelp search - "sushi" for example - this function will return
# all of the additional search pages. These pages will be used later
# to obtain all of the restaurants for the yelp search. 

# For example, when you type "sushi" in yelp, you will initially see
# a page with ten restaurants on it. When you scroll down to the
# bottom of the page, there are additional pages that have additional 
# restaurants on them. This function acquires all those links so
# they can be iterated through later. 
def find_all_pages(section_url):
    # Initialize function/variables 
    count = 0
    links = [] # for the new page links 
    
    # Create beautiful soup objects 
    html = urlopen(section_url).read()
    soup = BeautifulSoup(html, "lxml")
    pages = soup.find("ul", "pagination-links")
    
    # Find all of the pages to search next 
    links.append(section_url)
    for li in pages.findAll("li"):
        # Skip the first "li" member because Yelp is weird 
        if count == 0:
            count += 1
            continue
        else:
            # Check to make sure the link doesn't already reside in list 
            if li.a != None and BASE_YELP + li.a["href"] not in links:
                links.append(BASE_YELP + li.a["href"])
                
    # Return the located links  
    return links

# This is an example of a yelp search with multiple pages.
# Again, this function will find all the links encompassed by
# the red oval. 
Image(filename='/home/wesley/Pictures/pagesToSearchExample.png')

# Given a yelp search - sushi, for example - this function will 
# obtain all of the yelp sub-restaurant links, the restaurant
# location, and the rating for each restaurant for a single
# page only. 

# This function was ultimately used to determine the aforementioned
# attributes for all restaurants on a single page of a yelp search. 
def get_category_links(section_url):
    # Initialize function/variables 
    biz_links = [] # for the restaurant links
    biz_addrs = [] # for the restaurant names 
    biz_stars = [] # for the restaurant rating 
    count = 0      # flag used to check for advertisements 
    
    # Create beautiful soup objects 
    html = urlopen(section_url).read()
    soup = BeautifulSoup(html, "lxml")
    content = soup.find("ul", "ylist ylist-bordered search-results")
    ad = soup.find("li", "add-search-result")
    
    # Acquire the physical addresses
    biz_addrs = [address for address in content.findAll("address")]
    if len(ad) != 0:
        biz_addrs.pop(0)

    # Acquire the business rating
    biz_stars = [rating.i["title"] for rating in content.findAll("div", "rating-large")]
    if len(ad) != 0:
        biz_stars.pop(0)
        
    # Acquire the sub-restaurant links 
    for li in content.findAll("li"):
        # Check to see if there is an advertisement 
        if len(ad) != 0 and count == 0:
            count += 1
            continue
        if li.a != None:
            biz_links.append(BASE_YELP + li.a["href"])
            
    # Return all the acquired information 
    return biz_links, biz_addrs, biz_stars

# This is an example of some of the data that we acquired
# for each restaurant 
Image(filename='/home/wesley/Pictures/restaurantAttributesExample.png')

# Now that we have a list of links for all the restaurants, we'll  
# want to acquire the data synonymous with each restaurant. 
def get_data(section_url):
    # Initialize function/variables
    allData = {}     # used to store "more business info" data 
    count = 0
    phone_data = []   # for the phone number of the restaurant 
    category = []     # for the "more business info" section 
    result = []       # also for the "more business info" section 
    
    # Create beautiful soup objects 
    html = urlopen(section_url).read()
    soup = BeautifulSoup(html, "lxml")
    name = soup.find("div", "biz-page-header-left")
    phone = soup.find("span", "i-wrap ig-wrap-biz_details i-phone-biz_details-wrap mapbox-icon") 
    biz_info = soup.find("div", "short-def-list")
    
    # Locate the phone number information  
    if phone != None:
        phone_data = [span.string for span in phone.findAll("span")]
        
    # Calculate the name of the restaurant    
    res_name = [h1.string for h1 in name.findAll("h1")]
    
    # If there is "more business info," we will acquire it 
    if biz_info != None:
        category = [dt.string for dt in biz_info.findAll("dt", "attribute-key")]
        result = [dd.string for dd in biz_info.findAll("dd")]
        
    # Otherwise, we chose not to consider the restaurant 
    else:
        return None
    
    # Add name of restaurant to dictionary 
    for name in res_name:
        allData["Name"] = name
    
    # Add phone number of restaurant to dictionary 
    for nums in phone_data:
        if count == 0:
            count += 1
            continue
        allData["Phone Number"] = nums

    # Add "more business info" to dictionary 
    for c,r in zip(category, result):
        allData[c] = r
        
    # Return the accumulated data for a single restaurant 
    return allData

# Business information for resturant - this is an example of the 
# data we acquired for a single restaurant 
Image(filename='/home/wesley/Pictures/yelpInfoExample.png')

# For all of the pages (for a given search) that we need to iterate 
# through. 
for page in pagesToIterate:
    # For each of the pages, get the link, location, and rating 
    # for each restaurant 
    placesToEat, addrs, ratings = get_category_links( page )
    
    # For all of that data, acquire the "more business info" data
    for link, loc, stars in zip(placesToEat, addrs, ratings):
        
        # Store the data into a dictionary 
        res_data = get_data( link )
        
        # Assuming there is data, add the additional attributes
        # (Name, location, and rating). 
        if res_data != None:
            res_data["Restaurant Link"] = link
            res_data["Location"] = loc
            res_data["Rating"] = stars
            
            # Write the data to a .csv file 
            for key, value in res_data.iteritems():
                writer.writerow( [key.encode('utf-8'), value.encode('utf-8')] )
            writer.writerow( ["XXXXX", "XXXXX"] )

# Now we can use our database!
conn = sqlite3.connect('restaurant.db')
conn.text_factory = str
c = conn.cursor()

# Display adjectives - for user
print "Please choose an adjective and enter it in the prompt below: \n"
print "Casual"
print "Bar"
print "Cozy"
print "Exciting"
print "Family"
print "Friends"
print "To-Go"
print "Upscale"
print "Romantic"
print "Outdoor"
print "Late-Night"
print "Richardy\n"

# Acquire input
user_input = raw_input( "Adjective selection: " )

# Display food types - for user 
print "Please choose a type of food and enter it in the prompt below: \n"
print "American"
print "Asian"
print "Breakfast"
print "European"
print "Italian"
print "Mexican"
print "Pizza"
print "Sandwich"
print "Seafood"
print "Steakhouse"
print "Sushi"
print "Vegan\n"

# Acquire input
type_input = raw_input( "Food Selection: " )

# We used word2vec to create our queries. 
words = Word2Vec.load_word2vec_format('/home/wesley/Desktop/theano/GoogleNews-vectors-negative300.bin', binary=True)

# Here is an example.

# Compare the following: 
a = words.similarity('romantic', 'reservations')
a_not = words.similarity('unromantic', 'reservations')

# Determine relationship
if a > a_not:
    print "Romantic and Reservations - so reservations. \n"
else:
    print "Unromantic and Reservations - so no reservations. \n"
    
# Now compare the following:
b = words.similarity('romantic', 'childish')
b_not = words.similarity('unromantic', 'childish')

# Determine relationship 
if b > b_not:
    print "Romantic and Childish - so kids are okay. \n"
else:
    print "Unromantic and Childish - so no kids. \n"

# Now compare the following:
c = words.similarity('romantic', 'groups')
c_not = words.similarity('unromantic', 'groups')

# Determine relationship 
if c > c_not:
    print "Romantic and Groups - so groups are okay. \n"
else:
    print "Unromantic and Groups - so no groups. \n"
    
# Now compare the following:
d = words.similarity('romantic', 'noise')
d_not = words.similarity('unromantic', 'noise')

# Determine relationship 
if d > d_not:
    print "Romantic and Noise - so noise is okay. \n"
else:
    print "Unromantic and Noise - so the less noise, the better. \n"
    
# This was done for all 12 of our adjectives.

# Display the final query
print "You have created the following query: "
print query

# Display the final result 
for res in c.execute( query ):
    print res