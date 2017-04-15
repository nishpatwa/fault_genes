import requests
import urllib,json
import pandas as pd
import string
import sqlite3

final_dict={}
id_list=[]
url_list = []
summary_list=[]
title_list=[]
answer_list = []
def getPageCount():
    response = requests.get("https://ask.openstack.org/en/api/v1/users/")
    data = response.json()
    return int(data['pages'])

def fetchData(pages):
 conn = sqlite3.connect('fault_genes.db')
 conn.text_factory = str
 print "Opened database successfully";

 conn.execute('''CREATE TABLE IF NOT EXISTS askopenstack
               (url TEXT,
               summary TEXT,
               title TEXT,
               answer TEXT);''')

 for page in range(1, 10):
    parameters = {"scope": all, "page": page}
    response = requests.get("https://ask.openstack.org/en/api/v1/questions/", params = parameters)
    data = response.json()
    answer = 0
    for i in range(0,len(data['questions'])):
       tmp_answer = ""
       tmp_summary = ""
       tmp_url = ""
       tmp_title = ""
       for key,value in data['questions'][i].iteritems():
          url = data['questions'][i]['url'].encode('utf-8').strip()
          if 'url' in key:
             value = value.encode('utf-8').strip()
             tmp_url = value
             url_list.append(value)
          elif 'summary' in key:
             value = value.encode('utf-8').strip()
             tmp_summary = value
             summary_list.append(value)
          elif 'title' in key:
             value = value.encode('utf-8').strip()
             tmp_title = value
             title_list.append(value)
          elif 'accepted_answer_id' in key:
              if value is None:
                 answer = ""
              else: answer=getAnswer(value,url)
              tmp_answer = answer
              answer_list.append(answer)
       row = {
             'url':tmp_url,
             'title':tmp_title,
             'summary':tmp_summary,
             'answer':tmp_answer
       }
       columns = ', '.join(row.keys())
       placeholders = ', '.join('?' * len(row))
       sql = 'INSERT INTO askopenstack ({}) VALUES ({})'.format(columns, placeholders)
    #   import pdb;pdb.set_trace();
       conn.execute(sql, row.values())
       conn.commit()
    print "Completed Page#: "+str(page)
 final_dict['url'] = url_list
 final_dict['title'] = title_list
 final_dict['summary'] = summary_list
 final_dict['answer'] = answer_list
 buildCsv(final_dict)  

def getAnswer(answer_id,url):
   try:
      answer_id = str(answer_id)
      url_text = url+"?"+"answer="+answer_id+"#post-id-"+answer_id
      response = requests.get(url_text)
      import bs4
      soup = bs4.BeautifulSoup(response.text)
      id = "js-post-body-"+answer_id
      answer = soup.select('div#'+id+' p')
      return answer
   except:
      print url

   

def buildCsv(final_dict):
 data_frame = pd.DataFrame(final_dict)
 data_frame.to_csv("ask_os.csv",sep=",")

def main():
     pages = getPageCount()
     fetchData(pages)

if __name__ == "__main__": main()
