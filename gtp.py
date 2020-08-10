import sys
import requests
from bs4 import BeautifulSoup
from collections import OrderedDict
import time

def usage():
    print("==============================")
    print("Usage:python gtp.py https://en.wikipedia.org/wiki/<Article_Name>")
    print("==============================")
    sys.exit(1)


#Checks if the link is follows the "Getting to Philosophy" law
def is_valid_link(url, para):
    #Sometimes the url is NoneType
    if str(type(url)) == "<class 'NoneType'>":
        return False
    #To make sure that the link isn't from an image
    if ':' in url:
        return False

    # Only links to wikipedia articles
    if '/wiki/' not in url:
        return False

    if '.wiktionary.org' in url:
        return False

    #to make sure that the URL isn't inside parenthesis
    search_text = para.split(url)[0]
    if search_text.count('(') != search_text.count(')'):
        return False
    
    return True


# Return only p tags.
def valid_tag_selector(tag):
    return tag.name == 'p'


# Use the requests library to perform a get request for the page.
def retrieve_page(article_url):
    # use requests to perform a http get
    response = requests.get(article_url)
    # Parse the http response
    if response.status_code != 200:
        print("==============================")
        print("Cannot fetch article {} from wikipedia. Status code: {}, Reason: {}".format(article_url, response.status_code, response.reason))
        print("==============================")
    return response


# Parse the HTML text with BeautifulSoup and remove the unwanted links
# Unwanted links are italicized or are enclosed in parantheses
def get_first_linked_article(html_text):
    # parse the html text
    soup = BeautifulSoup(html_text,'html.parser')
    content_div = soup.find(id ='mw-content-text')
    
    # Find all valid tags using the valid_tag_selector method.
    # We need to find either the 'p' tags.
    # Also, we need only the direct children of the mw-content-text div
    # element
    for p in content_div.find_all(valid_tag_selector):
        #to remove italized links
        for i in p.find_all('i'):
            i.replace_with("")

        #find all links in paragraph
        links = p.find_all('a')

        #Stringfy the element
        unicode_para = str(p)
        for link in links:
            #Links with class "mw-redirect" automatically redirects to another pages. 
            #We dont want that
            if link.get('class') != 'mw-redirect':
                linked_article = link.get('href')
                # Check if link is valid and not in parantheses
                if is_valid_link(linked_article, unicode_para):
                    return "https://en.wikipedia.org" + linked_article
    
    


def run():
    # We need to check if we have an argument to parse
    if len(sys.argv) != 2:
        usage()

    # Print the arguments
    article = sys.argv[1]
    visited_articles = []
    
    while article.lower() != "https://en.wikipedia.org/wiki/philosophy":
        time.sleep(1)
        print(article)
        # check if we've already visited this article
        if article.lower() in visited_articles:
            print("==============================")
            print("Fell in a loop")
            print("==============================")
            sys.exit(1)

        response = retrieve_page(article)
        if article == 'Special:Random':
            # Replace the random string with the URL of the page
            article = response.url
        # add the page to our visited section
        visited_articles.append(article.lower())
        article = get_first_linked_article(response.text)
        time.sleep(1)
        
        
    # Finished finding all the pages till Philosophy.

    print("++++++++++++++++++++++++++++++++++++++++++++++++")
    
    print("Found " + str(len(visited_articles)) + " pages from "+ str(visited_articles[0]) +" to Philosophy\n")

    print("Articles: ")
    for a in visited_articles:
        print("- {}".format(a))
    
    print("++++++++++++++++++++++++++++++++++++++++++++++++")

if __name__ == '__main__':
    run()