# Import Splinter, BeautifulSoup, and Pandas
from splinter import Browser, browser
from bs4 import BeautifulSoup as soup
import pandas as pd
import datetime as dt
from webdriver_manager.chrome import ChromeDriverManager


# add function to initialize browser, create data dict, end webdriver, return scraped data
def scrape_all():
    # initiate headless driver for deployment
    executable_path = {'executable_path': ChromeDriverManager().install()}
    browser = Browser('chrome', **executable_path, headless=True)

    # set news title and paragraph variables
    news_title, news_paragraph=mars_news(browser)

    # run all scraping functions and store results in dictionary
    data={
        "news_title": news_title,
        "news_paragraph": news_paragraph,
        "featured_image": featured_image(browser),
        "facts": mars_facts(),
        "hemispheres": hemis(browser),
        "last_modified": dt.datetime.now()
    }

    # stop webdriver and return data
    browser.quit()
    return data


### News 

def mars_news(browser):

    # Visit the Mars news site
    url = 'https://redplanetscience.com/'
    browser.visit(url)

    # Optional delay for loading the page
    browser.is_element_present_by_css('div.list_text', wait_time=1)

    # Convert the browser html to a soup object and then quit the browser
    html = browser.html
    news_soup = soup(html, 'html.parser')

    # Add try/except for error handling
    try:
        slide_elem = news_soup.select_one('div.list_text')
        # use parent element to find the first 'a' tage and save it as news_title
        news_title=slide_elem.find('div', class_='content_title').get_text()
        # use the parent element to find the paragraph text
        news_p = slide_elem.find('div', class_='article_teaser_body').get_text()

    except AttributeError:
        return None, None

    return news_title, news_p


### JPL Space Images Featured Image

def featured_image(browser):

    # Visit URL
    url = 'https://spaceimages-mars.com'
    browser.visit(url)

    # Find and click the full image button
    full_image_elem = browser.find_by_tag('button')[1]
    full_image_elem.click()

    # Parse the resulting html with soup
    html = browser.html
    img_soup = soup(html, 'html.parser')

    # add try/except for error handling
    try:
        # find the relative image url
        img_url_rel = img_soup.find('img', class_='fancybox-image').get('src')
        
    except AttributeError:
        return None

    # Use the base url to create an absolute url
    img_url = f'https://spaceimages-mars.com/{img_url_rel}'

    return img_url

# ## Mars Facts


def mars_facts():

    # add try/except for error handling
    try:
        # use 'read_html' to scrape facts table into dataframe
        df = pd.read_html('https://galaxyfacts-mars.com')[0]
    
    except BaseException:
        return None

    # assign columns and set index of dataframe
    df.columns=['Description', 'Mars', 'Earth']
    df.set_index('Description', inplace=True)
    
    # convert dataframe into HTML format, add bootstrap
    return df.to_html(classes="table table-striped")





def hemis(browser):
    # 1. Use browser to visit the URL 
    url = 'https://marshemispheres.com/'
    browser.visit(url)

    # 2. Create a list to hold the images and titles.
    hemisphere_image_urls = []

    # 3. Write code to retrieve the image urls and titles for each hemisphere.
    html = browser.html
    hemi_soup = soup(html, 'html.parser')
    home='https://marshemispheres.com/'
    #find where hemi info is
    items=hemi_soup('div',class_='item')

    #loop through items to pull titles and hemi page links
    for item in items:
        #set empty dictionary
        hemispheres={}
        #find titles
        title=item.find('h3').get_text()
        #find relative links
        img_rel=item.find('a',class_='itemLink product-item')['href']
        #create full link
        hemi_link=home+img_rel
        browser.visit(home + img_rel)
        
        #parse data on hemi page
        img_html=browser.html
        img_soup=soup(img_html,'html.parser')
        dl=img_soup.find('div',class_='downloads')
        img_rel=dl.find('a')['href']
        img_url=home+img_rel
        
        #add data to hemisphere_image_urls list
        hemispheres['img_url']=img_url
        hemispheres['title']=title
        hemisphere_image_urls.append(hemispheres)
        browser.back()
   
    #return hemisphere data
    return hemisphere_image_urls

# tells flask script is complete and ready 
#prints results of scraping to terminal

if __name__ == "__main__":
    #if running as script, print scraped data
    print(scrape_all())
