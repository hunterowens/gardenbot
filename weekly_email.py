from postmarker.core import PostmarkClient
import os 
import requests 
import pandas as pd 
import datetime 

TOKEN = os.environ.get('POSTMARK_API_KEY')
BASE_URL = 'https://gardenbot-uxehlftuua-uw.a.run.app'
TODAY = datetime.date.today()

def get_seedlings():
  """
  Get's a list of seedlings from the API
  and returns it was a pandas dataframe
  """
  r = requests.get(f'{BASE_URL}/gardenbot.json?_shape=array&sql=select%0D%0A++*%0D%0Afrom%0D%0A++seedlings%0D%0A++inner+JOIN+seeds+on+seed_id+%3D+id%3B')
  df = pd.DataFrame.from_dict(r.json())
  df['date_planted'] = pd.to_datetime(df.date_planted)
  df = df.assign(today = pd.to_datetime(TODAY))
  df = df.assign(days_to_transplant = df.days_to_transplant.apply(lambda x: pd.Timedelta(x, unit='d')))
  df = df.assign(time_remaining = df.days_to_transplant - (df.today - df.date_planted))
  return df

def generate_seedlings_report(seedlings = get_seedlings()):
  df = seedlings[['seed_name', 'container', 'location', 'time_remaining']].sort_values(by='time_remaining')
  body =f"""
  <h2>Seedlings Active</h2> 
  {df.to_html()}
  """
  return body

def generate_current_plantings_report():
  pass

def generate_what_to_plant_report():
  pass

def generate_body():
  """
  Generates the HTML Body of the email
  """
  body = generate_seedlings_report()
  return body

def send_email(html, subject):
  postmark = PostmarkClient(server_token=TOKEN)
  postmark.emails.send(
      From='gardenbot@hunterowens.net',
      To='hunter@hunterowens.net',
      Subject=subject,
      HtmlBody=html
      )
  print(f"email sent: {subject})")
  return 

if __name__ == '__main__':
  subject=f'Garden Weekly Report for {TODAY.strftime("%B %d, %Y")}'
  html = generate_body()
  send_email(html, subject)
