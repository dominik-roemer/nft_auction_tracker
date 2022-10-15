from selenium import webdriver
import time
from datetime import datetime


class AuctionAlarm:

    def __init__(self, auction_name, url, thresh_time=60, thresh_percentage=50):
        self.name = auction_name
        self.url = url
        self.asset_info_list = []
        self.webdriver_path = r'C:\Users\Administrator\Desktop\chromedriver.exe'
        self.driver = None
        self.auction_info = self.initialize_auction_info_dict(url)
        self.auction_info = self.update_auction_info(name=auction_name)
        self.alarm_info = self.initialize_alarm_trigger_info_dict()
        self.alarm_info = self.update_alarm_settings(thresh_time=thresh_time, thresh_percentage=thresh_percentage)

        self.log_string = ''
        self.add_log_line(f'auction alarm for {self.name} created')
    """############"""
    """Web-Scraping"""
    """############"""

    def prepare_website(self):
        """calls all the functions which are necessary to get the desired website"""
        self.add_log_line(f'prepare website')
        self.click_on_auction()
        self.add_log_line(f'website prepared')

    def click_on_auction(self):
        """click the -On Action- button"""
        button_element = self.driver.find_element_by_xpath('//button[text()="On Auction"]')
        button_element.click()

    def close_webdriver(self):
        """closes the webdriver"""
        self.driver.close()
        self.add_log_line(f'webdriver closed')

    def scrape_floor_price(self):
        """gets the floor price of the current auction"""

        self.add_log_line(f'start scraping floorprice')
        """get the auction overview box element"""
        try:
            auction_overview_box_element = self.driver.find_elements_by_class_name("Blockreact__Block-sc-1xf18x6-0.iYAsis")
            floor_price = None
            for overview_box_element in auction_overview_box_element:
                sub_element_text = overview_box_element.text
                if "floor price" in sub_element_text:
                    floor_price_box_element_child = overview_box_element
                    floor_price_box_element = floor_price_box_element_child.find_element_by_xpath("./..")
                    floor_price_div_element = floor_price_box_element.find_element_by_class_name(
                        "Overflowreact__OverflowContainer-sc-7qr9y8-0.jPSCbX")
                    floor_price = float(floor_price_div_element.text)
                    break
            self.add_log_line(f'floorprice={floor_price} scraped.')
            return floor_price
        except Exception as e:
            self.add_log_line(f'failed to scrape floorprice.')
            self.add_log_line(f'error occurred: '+str(e))
            return None

    def scrape_auction_website(self):
        """executes all scraping functions to get all necessary infos from the url"""
        self.add_log_line(f'start scraping the website')
        floor_price = self.scrape_floor_price()
        self.auction_info = self.update_auction_info(floor_price=floor_price)

        asset_info = self.scrape_info_of_assets()
        self.update_auction_info(asset_list=asset_info)

    def init_webdriver(self):
        """initialize webdriver"""
        self.add_log_line(f'initialize webdriver')
        options = webdriver.ChromeOptions()
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument("--disable-blink-features=AutomationControlled")
        driver = webdriver.Chrome(executable_path=self.webdriver_path)
        self.add_log_line(f'webdriver initialized')
        return driver

    def open_url(self):
        """opens the given URL in the Chrome Webdriver and maximizes the window"""
        self.driver = self.init_webdriver()
        self.add_log_line(f'open website')
        self.driver.get(self.url)
        self.driver.maximize_window()
        self.add_log_line(f'website opened')
        time.sleep(10)
        self.prepare_website()
        time.sleep(10)  # wait for 20 seconds to load the website

    def scrape_info_of_assets(self) -> list:
        """Finds the first assets shown on the side and gets the prices of each one"""
        asset_list = self.find_asset_elements()
        info_list = []
        self.add_log_line(f'start scraping assets info')
        for asset in asset_list:
            if self.check_if_auction(asset):
                curr_dict = {
                    'name_tag': self.find_name(asset),
                    'price':  self.find_price(asset),
                    'time_left': self.find_left_time(asset),
                    'url': self.find_url(asset)
                }
                # check if any of the values (scraped info) is None. If yes, skip this asset
                if None not in curr_dict.values() or '' not in curr_dict.values():
                    info_list.append(curr_dict)
                else:
                    pass
            else:
                pass
        self.asset_info_list = info_list
        return info_list

    def find_asset_elements(self):
        """gets all assets which are required"""
        """search by x-path: https://www.softwaretestingmaterial.com/dynamic-xpath-in-selenium/.
        The assets are found by the x-path: //*[@role="gridcell"], because all assets are collected 
        in a grid and each one is in a gridcell"""
        self.add_log_line(f'searching for assets')
        try:

            x_path_asset = '//*[@role="gridcell"]'
            asset = self.driver.find_elements_by_xpath(x_path_asset)
            self.add_log_line(f'{len(asset)} assets where found')
            return asset

        except Exception as e:
            self.add_log_line(f'failed to find assets')
            self.add_log_line(f'error occurred: ' + str(e))
            self.driver.close()
            return None

    def find_left_time(self, asset_element):
        """find time left"""
        self.add_log_line('start searching for asset left time')
        try:
            time_left_block_element_class_name = "AssetCardFooter--trading-annotations"
            time_expiration_element_class_name = "AssetCardFooter--expiration"
            time_left_element_class_name = "Overflowreact__OverflowContainer-sc-7qr9y8-0"

            time_left_block_element = asset_element.find_element_by_class_name(time_left_block_element_class_name)
            trading_expiration_element = time_left_block_element.find_element_by_class_name(
                time_expiration_element_class_name)
            time_left_element = trading_expiration_element.find_element_by_class_name(time_left_element_class_name)
            time_left_str = time_left_element.text
            time_left_str_processed = self.convert_time_str_to_int(time_left_str)
            self.add_log_line(f'found left time: {time_left_str_processed}')
            return time_left_str_processed
        except Exception as e:
            self.add_log_line('failed to find asset left time')
            self.add_log_line(f'error occurred: ' + str(e))
            return None

    def find_price(self, asset_element):
        """finds the price of the given asset. The asset is a Selenium WebElement"""
        """find the price"""
        self.add_log_line('start searching for asset price')
        try:
            class_name = "Price--raw-symbol"
            price_symbol_element = asset_element.find_element_by_css_selector('span.' + class_name)
            price_div_element = price_symbol_element.find_element_by_xpath("./..")
            if price_div_element.text == '':
                return None
            price = float()
            self.add_log_line(f'found price: {price}')
            return price

        except Exception as e:
            self.add_log_line('failed to find asset price')
            self.add_log_line(f'error occurred: ' + str(e))
            return None

    def find_name(self, asset_element):
        """find the name"""
        self.add_log_line(f'start searching for asset name')
        try:
            name_tag_class_name = "AssetCardFooter--name"
            name_tag_element = asset_element.find_element_by_class_name(name_tag_class_name)
            self.add_log_line(f'found name_tag: {name_tag_element.text}')
            return name_tag_element.text

        except Exception as e:
            self.add_log_line('failed to find asset name')
            self.add_log_line(f'error occurred: ' + str(e))
            return None

    def find_url(self, asset_element):
        """find the url"""
        self.add_log_line(f'start searching for asset url')
        try:
            href_css_selector = "a.Asset--anchor"
            href_tag_element = asset_element.find_element_by_css_selector(href_css_selector)
            href = href_tag_element.get_attribute('href')
            self.add_log_line(f'found url')
            return href
        except Exception as e:
            self.add_log_line('failed to find asset url')
            self.add_log_line(f'error occurred: ' + str(e))
            return None


    """#############"""
    """Alarm Trigger"""
    """#############"""

    def execute_auction_alarm_check(self):
        """starts the process to check the asset infos for alarm triggers"""
        self.add_log_line('start alarm check execution')
        assets_triggered_alarm = [] # stores the assets which are triggering the alarm
        for asset_info in self.asset_info_list:
            if self.alarm_triggered(asset_info):
                self.add_log_line('alarm triggered')
                assets_triggered_alarm.append(asset_info)
        return assets_triggered_alarm

    def alarm_triggered(self, asset_info):
        """takes the given asset and checks if the given information fits the alarm settings"""
        # the price of an asset needs to be lower than the price_alarm_thresh
        curr_asset_price = asset_info['price']
        curr_left_time = asset_info['time_left']
        # if both alarm conditions are true, return True
        if self.lower_than_price_threshold(curr_asset_price) and self.lower_than_time_threshold(curr_left_time):
            return True
        return False

    def lower_than_price_threshold(self, asset_price) -> bool:
        """checks if the asset price is lower than the price threshold"""
        curr_alarm_thresh = self.compute_price_alarm_threshold(self.alarm_info['thresh_percentage'],
                                                               self.auction_info['floor_price'])

        if asset_price < curr_alarm_thresh:
            return True
        return False

    def lower_than_time_threshold(self, asset_left_time) -> bool:
        """checks if the left time is lower than the set left time threshold"""
        if asset_left_time < self.alarm_info['thresh_time']:
            return True
        return False

    """#############"""
    """Other methods"""
    """#############"""

    def update_alarm_settings(self, **kwargs):
        """updates the threshold time and percentage of the auction"""
        updated_alarm_info = self.alarm_info
        for key, value in kwargs.items():
            if key not in updated_alarm_info.keys():
                return None
            updated_alarm_info[key] = value
        return updated_alarm_info

    def update_auction_info(self, **kwargs):
        """update the auction info dict with the given key and value"""
        updated_auction_info = self.auction_info
        for key, value in kwargs.items():
            if key not in updated_auction_info.keys():
                return None
            updated_auction_info[key] = value
        return updated_auction_info

    def convert_time_str_to_int(self, time_str) -> int:
        """converts the timestring into a int representing minutes"""
        time_int = 0
        if "days" in time_str:
            time_str = self.preprocess_time_string(time_str)
            time_int = int(time_str)*24*60
        elif "a day" in time_str:
            time_int = 24 * 60
        elif "hours" in time_str:
            time_str = self.preprocess_time_string(time_str)
            time_int = int(time_str) * 60
        elif "an hour" in time_str:
            time_int = 60
        elif "minutes" in time_str:
            time_str = self.preprocess_time_string(time_str)
            time_int = int(time_str)
        elif "a minute" in time_str:
            time_int = 1
        return time_int

    """debug and develop methods"""
    def set_asset_info(self, asset_info_list):
        """sets the asset info list with the given info list. Used for debugging"""
        self.asset_info_list = asset_info_list

    def add_log_line(self, string):
        """adds the string to the log_string"""
        end_of_line_str = '::..'
        time_stamp = self.get_time_stamp()
        self.log_string = self.log_string+'\n'+time_stamp+': '+string+end_of_line_str


    """static methods"""

    @staticmethod
    def get_time_stamp():
        curr_time = datetime.now()
        time_stamp = f'{curr_time.day}-{curr_time.month} {curr_time.hour}:{curr_time.minute}:{curr_time.second}'
        return time_stamp

    @staticmethod
    def preprocess_time_string(time_string) -> str:
        """deletes all the unnecessary chars out of the string"""
        time_string = time_string.replace("days", "")
        time_string = time_string.replace("day", "")
        time_string = time_string.replace("left", "")
        time_string = time_string.replace("hours", "")
        time_string = time_string.replace("hour", "")
        time_string = time_string.replace("minutes", "")
        time_string = time_string.replace("minute", "")
        time_string = time_string.replace(" ", "")
        return time_string

    @staticmethod
    def check_if_auction(asset) -> bool:
        """function to check if the asset is an auction. True if yes"""
        if 'AssetCardFooter--expiration' in asset.get_attribute('innerHTML'):
            return True
        return False

    @staticmethod
    def compute_price_alarm_threshold(thresh_percentage, floor_price) -> float:
        """computes the price alarm threshold with the given thresh_percentage and the floor_price"""
        price_alarm_thresh = (100-thresh_percentage)/100*floor_price
        return price_alarm_thresh

    @staticmethod
    def initialize_auction_info_dict(url):
        """initialize the info dict for the infos related to the auction from the website"""
        info_dict = {
            'url': url,
            'floor_price': 0,
            'asset_list': [],
            'name': ''
        }
        return info_dict

    @staticmethod
    def initialize_alarm_trigger_info_dict():
        """returns the dict which keeps all the necessary infos related to the alarm trigger"""
        alarm_info = {
            'thresh_time': 0,  # in minutes
            'thresh_percentage': 0  # in percentage [0 to 100]
        }
        return alarm_info
