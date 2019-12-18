from selenium import webdriver
from bs4 import BeautifulSoup
from urllib import request
from os import path
from tqdm import tqdm
import time
import re


def scroll_infinite(driver, scrool_pause_time = 1):
    """
    Scroll till the end of page 
    """
    # Get scroll height
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        # Scroll down to bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # Wait to load page
        time.sleep(scrool_pause_time)

        # Calculate new scroll height and compare with last scroll height
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

def get_list_presentation(home_page_url):
    """
    Get list of presentations
    """

    driver = webdriver.Chrome()
    driver.get(home_page_url)
    scroll_infinite(driver)
    html = driver.page_source

    soup = BeautifulSoup(html)
    presentations_div = soup.find('div',attrs={'class':'presentationsGrid'})
    list_presentations_pages = []
    list_presentations = presentations_div.find_all('div', attrs={'data-item-type':'presentation'})
    for presentation in list_presentations:
        url = presentation.find('a')['href']
        list_presentations_pages.append(url)
        
    return list_presentations_pages

def get_video_data(list_presentations):
    """
    Get video link and name
    """

    extracted_links = []
    heading_list = []
    for presentation_link in list_presentations_pages:
        driver = webdriver.Chrome()
        driver.get(presentation_link)
        try:
            heading = driver.find_element_by_tag_name('h1').get_attribute('innerHTML')
            heading = heading.strip().replace("amp;", '_').replace(" ", "_")

            iframe_div = driver.find_element_by_class_name('slp__videoPlayer__content')
            iframe = iframe_div.find_element_by_tag_name('iframe')

            driver.switch_to.frame(iframe)

            html = driver.page_source
            soup = BeautifulSoup(html)
            script = soup.find_all('script')[4]
            res = re.search('"url":"(https://gcs-vimeo.akamaized.net.*?.mp4)"', script.string)
        

            extracted_links.append(res.group(1))
            heading_list.append(heading)
        
        except:
            pass

        driver.quit()
    
    return extracted_links, heading_list

def download_all_videos(extracted_links, heading_list):
    """
    Download all videos and save in data dir
    """
    for i in tqdm(range(len(extracted_links))):
        request.urlretrieve(extracted_links[i], path.join("../data", extracted_links[i]))

    return True

def main():
    list_presentations = get_list_presentation("https://slideslive.com/neurips")
    
    with open('../data/all_presentations.txt', 'w') as f:
        for item in list_presentations:
            f.write("%s\n" % item)

    extracted_links, heading_list = get_video_data(list_presentations)

    with open('../data/all_urls_headings.txt', 'w') as f:
        for i in range(len(extracted_links)): 
            f.write("%s %s\n" % (heading_list[i], extracted_links[i]))

    download_all_videos(extracted_links, heading_list)

if __name__ == "__main__":
    main()

