#imports
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
# to save the file with the right name
from datetime import datetime, timedelta
# import Action chains 
from selenium.webdriver.common.action_chains import ActionChains

## setting up the Web Driver
options = webdriver.ChromeOptions() 
options.add_argument("start-maximized")
# to suppress the error messages/logs, I found it in stack overflow
options.add_experimental_option('excludeSwitches', ['enable-logging'])
PATH = 'C:\Program Files (x86)\chromedriver.exe'
driver = webdriver.Chrome( PATH, options=options)

job_titles_search_keywords = [
    # Data Science related job titles
    "Data Scientist",
    "Data Analyst",
    "Data Engineer",
    "Machine Learning Engineer",
    "Statistician",
    "Data Architect",
    "Business Intelligence Analyst",
    "Data Science Manager",
    "Big Data Engineer",
    "Quantitative Analyst",

    # Software Development related job titles, commented out if we Only want Data related jobs
    '''"Software Developer",
    "Software Engineer",
    "Front-End Developer",
    "Back-End Developer",
    "Full Stack Developer",
    "Web Developer",
    "Mobile Application Developer",
    "Software Architect",
    "Software Development Manager"'''
]

locations = ['canada', 'vancouver', 'montreal' 'toronto','calgary' , 'edmonton', 'Ottawa', 'Mississauga', 'Winnipeg']
# class to store each Job listing 
class JobListing:
    """Class for job listings"""
    def __init__(self, title, company, description, jobType, location, job_ID, salary, platform, posting_date):
        self.title = title
        self.company = company
        self.description = description
        self.location =location
        self.jobID = job_ID
        self.jobType = jobType
        self.salary = salary
        self.platform = platform
        self.posting_date = posting_date

# function to get the right the right string to input as a search term
def get_google_url(position, location):
    """Function to get the right the right string in the url, it will handle the space and make sure search is in canada"""
    search_string = str.replace(position,' ','+')
    search_term = search_string.lower() + f'+{location}'
    url = f"https://www.google.com/search?q={search_term}&ie=UTF-8&ibp=htl;jobs#fpstate=tldetail"
    return url

def get_job_id (url):
    """Function to get the unique Id of a job, to identify when we get the same JOB from different searches"""
     # Find the start of the job ID
    start = url.find('htidocid=') + len('htidocid=')
    # Extract the rest of the string
    rest = url[start:]
    # Find the end of the job ID (if there are more parameters after it)
    end = rest.find('&') if '&' in rest else len(rest)
    # Extract the job ID
    job_id = rest[:end]
    return job_id

def scroll_page(driver, listing):
    """ Scroll view to load more listings, pass the selenium driver and the element to scroll to and have on the top"""
    driver.execute_script(
        "arguments[0].scrollIntoView(true);" , listing)



## Find all the  visible listings
def get_listings(driver):
    listings = driver.find_elements_by_xpath("//*[contains(@class, 'PwjeAc')]")
    return listings


def get_job_title(driver):
    """get the job title"""
    title_element =  driver.find_elements_by_xpath('//*[@class="KLsYvd"]')
    title = title_element[-1].text
    return (title)

def get_company_name(driver):
    company_element = driver.find_elements_by_xpath('//*[@class="nJlQNd sMzDkb"]')
    company = company_element[-1].text
    return company

def get_location(driver):
    location = driver.find_elements_by_xpath('//div[@class="sMzDkb"]')[-1].text
    return location

def get_job_type(driver):
    job_type = driver.find_elements_by_xpath('//span[@class="LL4CDc"]')[-1].text
    return job_type

def get_description(driver, job_container):
    try:        
        # if there is a show more button
        if(driver.find_elements_by_xpath('//div[@class="atHusc"]')[-1].text!=''):
            # get the show more div
            show_more = job_container.find_elements_by_xpath('//div[@class="atHusc"]')[-1]
            ### scroll to 'show more' button
            scroll_page(driver,show_more)
            show_more.click()
            # wait to load
            time.sleep(0.2)
            description = driver.find_elements_by_xpath('//span[@class="HBvzbc"]')[-1].text
            return description
        else:
            description = driver.find_elements_by_xpath('//span[@class="HBvzbc"]')[-1].text
            return description
        
    except :
        print("Element not found or page took too long to load")
        return 'null'
    
def get_salary(job_item):
    try:
        salary_element = job_item.find_elements_by_xpath('.//div[@class="I2Cbhb bSuYSc"]/span[@class="LL4CDc"]')[-1]
        salary = salary_element.text
        #salary = driver.find_elements_by_xpath('//*[@id="gws-plugins-horizon-jobs__job_details_page"]/div/div[3]/div[2]/span[2]/span]') 
        return salary
    except:
        return 'null'
    
def get_platform(job_item):
    try:
        # Find the 'via ..' element using XPath
        #recruitment_platform = driver.find_element_by_xpath("//div[contains(text(), 'via ')][@class='Qk80Jf']")
        recruitment_platform = job_item.find_elements_by_xpath(".//div[@class='oNwCmf']/div[contains(text(),'via ')][@class='Qk80Jf']")[-1]
        # Extract the text
        text = recruitment_platform.text.replace('via ', '')
        #recruitment_platform = driver.find_elements_by_xpath('//div[@class="Qk80Jf"]')[-1].text.replace('via ', '')
        
        return text
    except:
        return 'null'

def get_posting_date(job_item):
    try:
        # Find the element using relative XPath
        element = job_item.find_elements_by_xpath('.//span[contains(text()," ago")]')[-1]

        # Extract the text
        text = element.text  # e.g., '4 days ago', '3 hours ago', or '30 minutes ago'

        # Check if the text is not empty
        if text:
            # Parse the number and the unit (days, hours, or minutes) from the text
            num, unit = text.split()[:2]

            # Calculate the exact date
            if unit.startswith('day'):
                date = datetime.now() - timedelta(days=int(num))
            elif unit.startswith('hour'):
                date = datetime.now() - timedelta(hours=int(num))
            elif unit.startswith('minute'):
                date = datetime.now() - timedelta(minutes=int(num))

            return date.strftime("%Y-%m-%d")
        else:
            return 'null'
    except:
        return 'null'
    

def get_job_data(positions, locations):
    Jobs = []
    for location in locations:
        for position in positions:
            #Define the url to search for the jobs
            url = get_google_url(position, location)
            driver.get(url)
            # wait for it to load the new search
            time.sleep(0.3)
            # counter of jobs
            i = 0
            while True:
                listings = get_listings(driver)
                # stop condition to exit the loop
                if i >= len(listings):
                    break
                element = listings[i]
                posting_date = get_posting_date(element)
                platform = get_platform(element)
                scroll_page(driver, element)
                time.sleep(0.1)
                element.click()
                # Wait for the element to load
                time.sleep(0.2)
                ## Get Job information 
                complete_job = driver.find_element_by_xpath('//div[@class="pE8vnd avtvi"]')
                company = get_company_name(driver)
                title = get_job_title(driver)
                job_type = get_job_type(driver)
                location = get_location(driver)
                description = get_description(driver,complete_job)
                job_id =  get_job_id(driver.current_url)
                salary = get_salary(element)
                #print(salary)
                #print(platform)
                #print(posting_date)
                
                new_job =JobListing(title,company,description,job_type,location, job_id,salary, platform, posting_date)
                Jobs.append(new_job)
            
                # Increase job Count 
                i += 1

    print(len(Jobs))
    df = pd.DataFrame([vars(f) for f in Jobs])
    return df
    


# Actual Call of everything
df = get_job_data(job_titles_search_keywords, locations)
df.to_csv(f"jobs_{datetime.now().strftime('%Y-%m-%d_%H-%M')}.csv", encoding='UTF-8')

#Close the Browser
driver.quit()

