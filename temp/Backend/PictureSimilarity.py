from io import BytesIO
from difflib import SequenceMatcher
import Levenshtein
import pandas as pd
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from PIL import Image
import imagehash
import tldextract
import requests

class PictureSimilarity:
    def __init__(self,URL):
     self.URL = URL
     self.df = pd.read_csv("./screenshots.csv")
     self.key_words = []
     self.domain = ""
     self.cnt = 0
     self.websites_to_check = []
     self.domain = URL.split("/")[2]
     self.key_words = re.split('[.;-]',self.domain)
     print("key words present in url : ",self.key_words)
     self.Domain_names = self.df[["Domain","hash"]]
     self.key_words_length = len(self.key_words)
     
    def domain_similarity(self,str1, str2):
        # Create a SequenceMatcher object with the input strings
        seq_matcher = SequenceMatcher(None, str1, str2)

        # Get the matching blocks, where a block is represented as a tuple (i, j, n)
        # i: start index in str1, j: start index in str2, n: length of the match
        matching_blocks = seq_matcher.get_matching_blocks()

        # Extract the longest common subsequence from the matching blocks
        lcs = ''.join(str1[i:i+n] for i, j, n in matching_blocks)
        
        distance = Levenshtein.distance(str1, str2)

        # Calculate similarity ratio
        max_length = max(len(str1), len(str2))
        similarity_percentage = ((max_length-distance) / max_length)*100
        return (len(lcs)/min(len(str1),len(str2)))*100 + similarity_percentage
    
    def getSimilarity(self):
        potential_domains = []
        for index,row in self.Domain_names.iterrows():
            domain_parts = row['Domain'].split(".")
            avg_scr = 0
            highest_scr = 0
            for i in range(len(self.key_words)-1):
                highest_scr = 0
                for j in range(len(domain_parts)-1):
                    similarity_percentage = self.domain_similarity(self.key_words[i], domain_parts[j])
                    highest_scr = max(highest_scr,similarity_percentage)
                avg_scr = max(avg_scr,highest_scr)
            potential_domains.append((avg_scr,row['Domain'],row['hash']))


        sorted_potential_domains = sorted(potential_domains, key=lambda x: x[0],reverse=True)
        
        websites_to_check = []
        found = False
        
        
        def check_key(k):
            if k == "hdfcbank" or k=="icici" or k=="sbi" or k=="irctc":
                return True
            return False
        
        for domain in sorted_potential_domains:
            domain_keys = re.split('[.;-]',domain[1])
            url = "https://"+domain[1]
            url = tldextract.extract(url)
            url = url.domain + "." + url.suffix
            url_to_check = tldextract.extract(self.URL)
            url_to_check = url_to_check.domain + "." + url_to_check.suffix
            present = False
            for k in domain_keys:
                if(check_key(k)):
                    present = True
            if url != url_to_check and present:
                websites_to_check.append(["https://" + domain[1],domain[2]])
            elif url == url_to_check:
                found = True
                break
        
        if found == True:
            return 0,[]
        
        hamming_distance = 64
        website_with_minDistance = "no website"
        print(websites_to_check)
        
        try:
            response = requests.get(self.URL, timeout=20)
            if response.status_code == 200:
                    Image2 = self.take_screenshot(self.URL)
                    H2 = self.calculate_image_hash(Image2)
                    for row in websites_to_check:
                        hdist = self.compare_image_hashes(H2,imagehash.hex_to_hash(row[1]))
                        if(hdist<hamming_distance):
                            hamming_distance = hdist
                            website_with_minDistance = row[0]
            else:
                print("no hash")
        except Exception as e:
            print("no hash")

        print(website_with_minDistance, hamming_distance)
        # H2 
        # response = requests.get(self.URL, timeout=20)
        # if response.status_code == 200:
        #         Image2 = self.take_screenshot(self.URL)
        #         H2 = self.calculate_image_hash(Image2)

        # if(len(websites_to_check)==0):
        #     for index,row in self.Domain_names.iterrows():
        #         H = self.compare_image_hashes(row[1],H2)
        #         if(H<=10):
        #             hamming_distance = min(hamming_distance,imagehash.hex_to_hash(H))
        #             websites_to_check.append("https://"+row[1])

        return hamming_distance,websites_to_check
        # try:
        #     if found == False:
        #         Len = len(websites_to_check)
        #         Image1 = self.take_screenshot(self.URL)
        #         H1 = self.calculate_image_hash(Image1)
        #         if Len == 1:
        #             print("Websites with 90 percent or more domain name similarity:",[websites_to_check[0]])
        #             Image2 = self.take_screenshot(websites_to_check[0])
        #             H2 = self.calculate_image_hash(Image2)
        #             return self.compare_image_hashes(H1,H2),websites_to_check[:1]
        #         elif Len == 2:
        #             print("Websites with 90 percent or more domain name similarity:",[websites_to_check[0],websites_to_check[1]])
        #             Image2 = self.take_screenshot(websites_to_check[0])
        #             Image3 = self.take_screenshot(websites_to_check[1])
        #             H2 = self.calculate_image_hash(Image2)
        #             H3 = self.calculate_image_hash(Image3)
        #             return min(self.compare_image_hashes(H1,H2),self.compare_image_hashes(H1,H3)),websites_to_check[:2]
        #         elif Len >=3:
        #             print("Websites with 90 percent or more domain name similarity:",[websites_to_check[0],websites_to_check[1],websites_to_check[2]])
        #             websites = []
        #             result = 64
        #             response = requests.get(websites_to_check[0])
        #             print(response)
        #             if response.status_code == 200:
        #                 Image2 = self.take_screenshot(websites_to_check[0])
        #                 H2 = self.calculate_image_hash(Image2)
        #                 websites.append(websites_to_check[0])
        #                 result = min(result,self.compare_image_hashes(H1,H2))
        #             response = requests.get(websites_to_check[1])
        #             if response.status_code == 200:
        #                 Image3 = self.take_screenshot(websites_to_check[1])
        #                 H3 = self.calculate_image_hash(Image3)
        #                 websites.append(websites_to_check[1])
        #                 result = min(result,self.compare_image_hashes(H1,H3))
        #             response = requests.get(websites_to_check[2])
        #             if response.status_code == 200:
        #                 Image4 = self.take_screenshot(websites_to_check[2])
        #                 H4 = self.calculate_image_hash(Image4)
        #                 websites.append(websites_to_check[2])
        #                 result = min(result,self.compare_image_hashes(H1,H4))
                    
        #             return result,websites
        #     else :
        #         print("Original websites")
        #         return 0,[] # It is original website
        # except BaseException as e:
        #     print(e)
        #     return 16,[]
    def take_screenshot(self,url):
        chrome_options = Options()

        # chrome_options.add_argument("--headless")  # Run Chrome in headless mode (no GUI)
        # chrome_options.add_argument("--disable-gpu")  # Disable GPU acceleration for headless mode

        driver = webdriver.Chrome(options=chrome_options)

        try:
            # Open the URL
                driver.get(url)
                WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
                # Take a screenshot
                screenshot_bytes = driver.get_screenshot_as_png()
                image = Image.open(BytesIO(screenshot_bytes))
                jpg_bytes_io = BytesIO()
                image.convert("RGB").save(jpg_bytes_io, format="JPEG")
                # Now you can work with the 'jpg_bytes_io' variable, for example, display it or process it further
                # Example: Display the JPG image
                # driver.save_screenshot("./screenshot"+str(i+1)+".jpg")
                # print("Screenshot saved to screenshot"+str(i+1)+".jpg")
                return image
        finally:
            # Close the browser
            driver.quit()

    def calculate_image_hash(self,image):
        hash_value = imagehash.phash(image)
        return hash_value

    def compare_image_hashes(self,hash1, hash2):
        return hash1 - hash2