from AuctionAlarm import AuctionAlarm
import json
from datetime import datetime
import smtplib
import time
import gspread


GOOGLE_SHEETS_API_USER = "...." # put your google sheets api username here
API_KEY = "google_drive_api_key.json"
REPEAT_TIMER = 10  # amount of minutes which the program waits before starting a new scraping


class AuctionAlarmContainer:

    def __init__(self, auction_spreed_sheet_name, interface_script):
        self.auction_info = []  # stores all the info about the auctions from the google sheet
        self.auctions = []  # stores all the auction objects which are created from the ones listed in the sheet
        self.interface_script = interface_script
        self.interface_data = self.read_interface_script(self.interface_script)
        self.email_server_info = {
            'domain_name': '....', # email domain like gmail
            'port': 465,  # 587 für TSL Verschlüsselung
            'provider': '...', # your email address
            'password': '...' # password for your email account
        }
        self.timer_start = self.set_timer()
        self.email_sent_assets = []  # keeps all the assets for which an email was already sent
        self.error_status = 0
        self.wks = self.initialize_worksheet(auction_spreed_sheet_name)
        self.read_auction_worksheet()

    def start_auction_alarm_session(self):
        """starts the whole auction alarm process. It iterates over all the
        auctions stored in self.auctions. The while loop keeps on running until the
        continue parameter in the interface script is changed to 0."""
        while True:

            if self.continue_session():
                for auction in self.auctions:
                    try:
                        if not self.error_status:  # checks if an error message was already sent
                            if self.error_occurred(auction):  # checks if an error occurred
                                self.send_error_email_to_admin(auction)

                        asset_list = self.execute_auction_observation(auction)
                        self.send_email(auction.auction_info, asset_list)
                        print(auction.log_string)
                        if not self.continue_session():
                            break
                    except Exception as e:
                        auction.close_webdriver()
                        self.send_error_email_to_admin(auction, str(e))
            time.sleep(self.interface_data['repeat_timer']*60)
            self.update_auction_alarm_session()

    def error_occurred(self, auction):
        """check if an error occurred in the process"""
        if "error" in auction.log_string:
            self.error_status = 1
            return True
        return False

    def reset_auction_alarm_check(self):
        """checks if the auction should be reset"""
        if self.interface_data['reset_status']:
            curr_time = time.time()
            time_passed_threshold = self.interface_data['hrs_to_reset']*60*60
            if curr_time - self.timer_start > time_passed_threshold:
                return True
            else:
                return False
        else:
            return False

    def update_auction_alarm_session(self):
        """change the settings of the auction alarm session"""
        self.interface_data = self.read_interface_script(self.interface_script)
        self.read_auction_worksheet()
        if self.new_auction_added():
            self.update_auctions()

    def read_auction_worksheet(self):
        """reads the auction information from the auction google sheet"""
        auction_info = self.wks.get_all_records()
        self.auction_info = auction_info

    def email_already_sent(self, asset):
        """check if an email was already sent for given asset was """
        already_sent_asset_names = [asset['name_tag'] for asset in self.email_sent_assets]
        if asset['name_tag'] in already_sent_asset_names:
            return True
        return False

    def reset_parameters(self):
        """resets the auction alarm"""
        self.email_sent_assets = []

    def continue_session(self):
        """checks if the session is continued or stopped"""
        if self.interface_data['continue'] == 1:
            return True
        return False

    def set_up_auctions(self):
        """takes all the auctions and their info to create the AuctionAlarm instances"""
        for info_dict in self.auction_info:
            self.add_auction_alarm(info_dict)

    @staticmethod
    def initialize_worksheet(auction_spreed_sheet_name):
        # google sheets login
        sa = gspread.service_account(filename=API_KEY)
        sh = sa.open(auction_spreed_sheet_name)
        return sh.worksheet(auction_spreed_sheet_name)

    def add_auction_alarm(self, auction_dict):
        """"""
        new_auction = self.create_auction_alarm(auction_dict)
        self.auctions.append(new_auction)

    def get_auction_info(self):
        print(self.auction_info)

    def send_error_email_to_admin(self, auction, message=''):
        """sends an email if an error occurred"""
        email_subject = f"Error occurred in {auction.name}!"
        if message == "":
            email_body = auction.log_string
        else:
            email_body = message+'\n'+auction.log_string
        server = smtplib.SMTP_SSL(self.email_server_info['domain_name'],
                                  self.email_server_info['port'])
        server.ehlo()
        server.login('nft.auction.alarm5000@gmail.com', self.email_server_info['password'])
        receiver = self.interface_data['administrator']
        server.sendmail(self.email_server_info['provider'],
                        receiver,
                        f"Subject: {email_subject}\n{email_body}")

    def send_email(self, auction_info, asset_list):
        """sends an email for all the assets which are given in the list"""
        # self.add_log_line(f'setup email server')
        for asset_info in asset_list:
            if not self.email_already_sent(asset_info):
                self.email_sent_assets.append(asset_info)
                email_subject, email_body = self.generate_email_text(auction_info, asset_info)
                try:
                    server = smtplib.SMTP_SSL(self.email_server_info['domain_name'],
                                              self.email_server_info['port'])
                    server.ehlo()
                    server.login('nft.auction.alarm5000@gmail.com', self.email_server_info['password'])
                    receiver = self.interface_data['receiver']
                    server.sendmail(self.email_server_info['provider'],
                                    receiver,
                                    f"Subject: {email_subject}\n{email_body}")
                    server.close()
                    self.email_sent_assets.append(asset_info)
                    #   self.add_log_line(f'email sent')
                except Exception as e:
                    print(e)

    def new_auction_added(self):
        """check if a new auction was added to auction_info"""
        # get the names of the already existing auction objects
        curr_auction_names = [auction.name for auction in self.auctions]

        # get the names of the auction_info
        auction_info_names = [info_dict["name"] for info_dict in self.auction_info]

        if not all(elem in curr_auction_names for elem in auction_info_names):
            return True
        return False

    def get_not_added_auctions(self):
        """get the info_dicts of the auctions for which no AuctionAlarm object was created yet"""
        curr_auction_names = [auction.name for auction in self.auctions]

        new_auction_info_dict = []
        for dict_info in self.auction_info:
            if not dict_info["name"] in curr_auction_names:
                new_auction_info_dict.append(dict_info)
        # get the auctions which have not been added
        return new_auction_info_dict

    def update_auctions(self):
        """checks first if a new auction was added to dict_info and if so, it adds it to the self.auctions"""
        not_added_auction = self.get_not_added_auctions()
        for auction_info in not_added_auction:
            self.add_auction_alarm(auction_info)

    def load_auction_info(self, auction_json_file):
        """loads the auction infi from json_file"""
        auction_info = open(auction_json_file)
        data = json.load(auction_info)
        self.auction_info = data

    @staticmethod
    def generate_email_text(auction_info, asset_info):
        """generates an e-mail which keeps all the necessary information"""
        diff_asset_floor_price = auction_info["floor_price"] - asset_info["price"]
        perc_under_floor_price = int(diff_asset_floor_price/auction_info["floor_price"]*100)
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        email_subject_str = f"Auction Alarm for {auction_info['name']}!!!!"
        email_body_str = f"{asset_info['name_tag']} is {perc_under_floor_price}% under the current floor price and " \
            f"the auction lasts for another {asset_info['time_left']} minutes.\n" \
            f"Link: {asset_info['url']}\n"\
            f"floor price: {auction_info['floor_price']}\n" \
            f"asset price: {asset_info['price']}\n" \
            f"time: {current_time}"

        return email_subject_str, email_body_str

    @staticmethod
    def execute_auction_observation(auction_alarm):
        """starts the routine to trigger an auction alarm. Which includes:
         opening and preprocessing the website, scrape it, eventually trigger the alarm
         and sends an email to the self.receiver"""
        auction_alarm.open_url()
        auction_alarm.scrape_auction_website()
        assets_triggered = auction_alarm.execute_auction_alarm_check()
        auction_alarm.close_webdriver()

        return assets_triggered

    @staticmethod
    def create_auction_alarm(auction_dict):
        """creates a new instance of AuctionAlarm object"""
        new_auction = AuctionAlarm(auction_dict["name"], auction_dict["url"],
                                   thresh_time=auction_dict["thresh_time"],
                                   thresh_percentage=auction_dict["thresh_percentage"])
        return new_auction

    @staticmethod
    def read_interface_script(interface_script):
        """reads the interface and returns the dict"""
        interface_info = open(interface_script)
        return json.load(interface_info)

    @staticmethod
    def set_timer():
        return time.time()
