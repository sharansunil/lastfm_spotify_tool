import pandas as pd 
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from gspread_dataframe import get_as_dataframe,set_with_dataframe

class GoogleSheetLoader:

	def __init__(self, scope=['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive'],):
		self.scope=scope
		self.credentials=ServiceAccountCredentials.from_json_keyfile_name('spotfm_credentials.json',self.scope)
		self.gc=gspread.authorize(self.credentials)

	def top100_to_df(self):
		top100=self.gc.open('best albums').worksheet("top100")
		no_rows=int(top100.acell('S2').value)
		no_col=int(top100.acell('S1').value )
		retval=[]
		for row in range(1,no_rows):
				retval.append(top100.row_values(row))
		df=pd.DataFrame(retval[1:],columns=[x.lower() for x in retval[0]])
		df=df.iloc[:,range(0,no_col)].fillna(0)
		df.to_csv("exports/Top100.csv")
		print("top 100 albums file downloaded")