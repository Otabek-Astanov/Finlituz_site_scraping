import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException


def get_urls(ws):
    """
    Extracts URLs of articles from the Finlit website based on the provided writing system.

    Args:
        ws (str): The writing system code ('lat', 'krl', or 'rus').

    Returns:
        list: A list of URLs of articles.
    """
    # Define writing systems and their corresponding URL paths
    writing_systems = {
        'lat': 'uz/',
        'krl': 'oz/',
        'rus': 'ru/'
    }

    # Set up Selenium WebDriver
    PATH = r"C:\Program Files (x86)\chromedriver.exe"
    service = Service(PATH)
    driver = webdriver.Chrome(service=service)

    # Generate URL for the articles page based on the writing system
    url = f"https://finlit.uz/{writing_systems[ws]}articles/"
    driver.get(url)
    print("\nSelenium_part Successfully Started\nPlease Wait few minutes\n")

    # Wait for the page to load
    time.sleep(5)

    # Scroll to the bottom of the page to load more content
    bottom_element = driver.find_element(By.TAG_NAME, 'footer')
    driver.execute_script("arguments[0].scrollIntoView();", bottom_element)
    time.sleep(5)

    # Click the "Load More" button multiple times to load additional content
    num_clicks = 50
    for _ in range(num_clicks):
        try:
            button = driver.find_element(By.CLASS_NAME, "btn-load-else")
            if button.is_displayed():
                button.click()
                time.sleep(5)
            else:
                print("the end")
                break
        except (NoSuchElementException, ElementClickInterceptedException) as e:
            print("something went wrong!")

    # Extract URLs of articles from the loaded content
    time.sleep(5)
    posts = driver.find_elements(By.CLASS_NAME, "post-container")
    print(f"\n\npost count: {len(posts)}")

    urls = []
    for post in posts:
        try:
            # Extract URL from the onclick attribute of the post element
            post_url = post.get_attribute("onclick").split("'")[1]
            if post_url.endswith('/'):
                urls.append(post_url)
            else:
                urls.append(post_url + '/')

        except Exception as e:
            print("error occurred:", str(e))

    # Clean up WebDriver
    driver.quit()

    return urls

# Call the function with the desired writing system to get the URLs of articles
# print(get_urls('lat'))
