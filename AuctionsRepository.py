import gspread
from oauth2client.service_account import ServiceAccountCredentials
from AuctionsDataFrame import AuctionsDataFrame
import time


class AuctionsRepository:
    def __init__(self):
        """
            The Auction Repository is responsible for connecting to Google Drive AOI and login with:
              - the File Name in .fileName
              - the File Id in .spreadsheetId
              - the Sheet Name in .sheetName
              - the Sheet Id in .sheetId (although not used here)
              - the Sheet itself (the data) in .sheet
              - the URLs and the credential to interact with the API in .scope and .creds

        """
        self.fileName = 'File Name'
        self.spreadsheetId = 'a_very_long_spreadsheet_id
        self.sheetname = 'a_sheet_of_the_spreadsheet'
        self.scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/spreadsheets',
                 "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]
        self.creds = ServiceAccountCredentials.from_json_keyfile_name('ml-model-fu.json', self.scope)
        self.client = gspread.authorize(self.creds)
        self.spreadsheet, self.sheet_all = self.login()

    def login(self):
        spreadsheet = self.client.open_by_key(self.spreadsheetId)
        sheet_all = spreadsheet.worksheet(self.sheetname_all)
        return spreadsheet, sheet_all

    def find_all_auctions(self) -> AuctionsDataFrame:
        adf = AuctionsDataFrame(self.sheet_all.get_all_values())
        adf.cleaning_currency_format()
        return adf

    def update_probability_award(self, auctionsdataframe: AuctionsDataFrame):
        auctionsdataframe.check_probability_column()
        probability_column = self.sheet_all.find('Probabilità Aggiudicazione').col
        ids_column = self.sheet_all.col_values(self.sheet_all.find('Id Immobile').col)

        ids_list = auctionsdataframe.get_ids_list()
        print("Number of auctions to be updated: ", len(ids_list))
        for Id in ids_list:
            while True:
                try:
                    self.sheet_all.update_cell(row=ids_column.index(Id) + 1,
                                               col=probability_column,
                                               value=auctionsdataframe.get_probability_by_id(Id))
                    time.sleep(3)
                    break
                except gspread.exceptions.APIError:
                    print(f"Errore durante l'update dell'id: {Id}")
                    t = 100
                    print(f"Aspetto per {t} secondi...\n")
                    time.sleep(t)
                    print("Re-Login agli API")
                    self.spreadsheet, self.sheet_all = self.login()