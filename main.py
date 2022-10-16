from AuctionAlarmContainer import AuctionAlarmContainer as AAC

debug = False

interface_path = r"G:\My Drive\interface"

if debug:
    worksheet_name = "auctions_debug"
    interface_name = r'\interface_script_debug.json'
else:

    worksheet_name = "auctions"
    interface_name = r'\interface_script.json'

auction_alarm_container = AAC(worksheet_name, interface_path+interface_name)
auction_alarm_container.set_up_auctions()
auction_alarm_container.start_auction_alarm_session()
