from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import WebDriverException
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
import time
import os

MAX_WAIT = 10

class NewVisitorTest(StaticLiveServerTestCase):
    
    def setUp(self):
        self.browser = webdriver.Chrome()
        staging_server = os.environ.get('STAGING_SERVER')
        if staging_server:
            self.live_server_url = 'http://' + staging_server

    def tearDown(self):
        self.browser.refresh()
        self.browser.quit()

    def wait_for_row_in_list_table(self, row_text):
        start_time = time.time()
        while True:
            try:
                table = self.browser.find_element_by_id('id_list_table')
                rows = table.find_elements_by_tag_name('tr')
                self.assertIn(row_text, [row.text for row in rows])
                return
            except(AssertionError, WebDriverException) as e:
                if time.time() -start_time >MAX_WAIT:
                    raise e
                time.sleep(0.5)
    
    def test_can_start_a_list_for_one_user(self):

        # Edith has heard about a cool new online to-do app.
        # She goes to check out its homepage
        self.browser.get(self.live_server_url)

        # She notices the page title and header mention to-do lists
        self.assertIn('To-Do', self.browser.title)
        header_text = self.browser.find_element_by_tag_name('h1').text
        self.assertIn('To-Do', header_text)
        
        # She is invited to enter a to-do item straight away
        inputBox = self.browser.find_element_by_id('id_new_item')
        self.assertEqual(
            inputBox.get_attribute('placeholder'),
            'Enter a to-do item'
            )
        
        # She types "Buy peacock feathers" into a text box (Edith's hobby
        # is tying fly-fishing lures)
        inputBox.send_keys('Buy peacock feathers')
       
    
        # when she hits enter, the page updates, and now the page lists
        # "1： Buy peacock feathers" as an item in a to-do list
        inputBox.send_keys(Keys.ENTER)
        self.wait_for_row_in_list_table('1:Buy peacock feathers')


        # There is still a text box inviting her to add another item. She
        # enters "Use peacock feathers to make a fly"(Edith is very methodical)
        time.sleep(1)
        inputBox = self.browser.find_element_by_id('id_new_item')
        inputBox.send_keys('Use peacock feathers to make a fly')
        inputBox.send_keys(Keys.ENTER)
        
        # The page updates again, and now shows both items on her list
        self.wait_for_row_in_list_table('1:Buy peacock feathers')
        self.wait_for_row_in_list_table('2:Use peacock feathers to make a fly')
        
        #satisfied, she goes back to sleep
        
    


    def test_multiple_users_can_start_lists_at_different_url(self):
        #Edith starts a new to-do list
        self.browser.get(self.live_server_url)
        inputBox = self.browser.find_element_by_id('id_new_item')
        inputBox.send_keys('Buy peacock feathers')
        inputBox.send_keys(Keys.ENTER)
        self.wait_for_row_in_list_table('1:Buy peacock feathers')

        # She notices that her list has a unique URL
        edith_list_url = self.browser.current_url
        self.assertRegex(edith_list_url, '/lists/.+')

        # Now a new user, Francis, comes along to the site

        ## We use a new browser session to make sure that no information 
        ## of Edith's is coming through from cookies etc
        self.browser.quit()
        self.browser = webdriver.Chrome()

        # Francis visits the home page. There is no sign of Edith's list
        self.browser.get(self.live_server_url)
        page_text = self.browser.find_element_by_tag_name('body').text
        self.assertNotIn('Buy peacock feathers', page_text)
        self.assertNotIn('make a fly', page_text)

        # Francis starts a new list by entering a new item, He is less
        # interesting than Edith...
        inputBox = self.browser.find_element_by_id('id_new_item')
        inputBox.send_keys('Buy milk')
        inputBox.send_keys(Keys.ENTER)
        self.wait_for_row_in_list_table('1:Buy milk')

        # Francis get his own unique URL
        francis_list_url = self.browser.current_url
        self.assertRegex(francis_list_url,'/lists/.+')
        self.assertNotEqual(francis_list_url, edith_list_url)

        # Again, there is no trace of Edith's list
        page_text = self.browser.find_element_by_tag_name('body').text
        self.assertNotIn('Buy peacock_feathers', page_text)
        self.assertIn('Buy milk', page_text)
        
    def test_layout_and_styling(self):
        # Edith goes to the home page
        self.browser.get(self.live_server_url)
        self.browser.set_window_size(1024, 768)

        # She notice the input box is nicely centered
        inputBox = self.browser.find_element_by_id('id_new_item')
        self.assertAlmostEqual(
            inputBox.location['x'] + inputBox.size['width']/2, 512, delta=10
        )

        # She starts a new list and sees the input is nicely center there too
        inputBox.send_keys('testing')
        inputBox.send_keys(Keys.ENTER)
        self.wait_for_row_in_list_table('1:testing')
        inputBox = self.browser.find_element_by_id('id_new_item')
        self.assertAlmostEqual(
            inputBox.location['x'] + inputBox.size['width']/2, 512, delta=10
        )
    
        
    

       
