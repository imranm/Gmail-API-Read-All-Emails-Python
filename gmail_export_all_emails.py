'''
Reading GMAIL using Python
    - Imran Momin
'''

'''
This script does the following:
- Go to Gmal inbox
- Find and read all messages (you can specify labels to read specific emails)
- Extract details (Date, Subject, Body) and export them to a .csv file
'''

'''
Before running this script, the user should get the authentication by following
the link: https://developers.google.com/gmail/api/quickstart/python
Also, client_secret.json should be saved in the same directory as this file
'''
from apiclient import discovery
from apiclient import errors
from httplib2 import Http
from oauth2client import file, client, tools
import base64
from bs4 import BeautifulSoup
# import dateutil.parser as parser
import csv
from time import strftime, gmtime
import sys

def ReadEmailDetails(service, user_id, msg_id):

  temp_dict = { }

  try:

      message = service.users().messages().get(userId=user_id, id=msg_id).execute() # fetch the message using API
      payld = message['payload'] # get payload of the message
      headr = payld['headers'] # get header of the payload


      for one in headr: # getting the Subject
          if one['name'] == 'Subject':
              msg_subject = one['value']
              temp_dict['Subject'] = msg_subject
          else:
              pass


      for two in headr: # getting the date
          if two['name'] == 'Date':
              msg_date = two['value']
              # date_parse = (parser.parse(msg_date))
              # m_date = (date_parse.datetime())
              temp_dict['DateTime'] = msg_date
          else:
              pass


      # Fetching message body
      email_parts = payld['parts'] # fetching the message parts
      part_one  = email_parts[0] # fetching first element of the part
      part_body = part_one['body'] # fetching body of the message
      part_data = part_body['data'] # fetching data from the body
      clean_one = part_data.replace("-","+") # decoding from Base64 to UTF-8
      clean_one = clean_one.replace("_","/") # decoding from Base64 to UTF-8
      clean_two = base64.b64decode (bytes(clean_one, 'UTF-8')) # decoding from Base64 to UTF-8
      soup = BeautifulSoup(clean_two , "lxml" )
      message_body = soup.body()
      # message_body is a readible form of message body
      # depending on the end user's requirements, it can be further cleaned
      # using regex, beautiful soup, or any other method
      temp_dict['Message_body'] = message_body

  except Exception as e:
      print(e)
      temp_dict = None
      pass

  finally:
      return temp_dict


def ListMessagesWithLabels(service, user_id, label_ids=[]):
  """List all Messages of the user's mailbox with label_ids applied.

  Args:
    service: Authorized Gmail API service instance.
    user_id: User's email address. The special value "me"
    can be used to indicate the authenticated user.
    label_ids: Only return Messages with these labelIds applied.

  Returns:
    List of Messages that have all required Labels applied. Note that the
    returned list contains Message IDs, you must use get with the
    appropriate id to get the details of a Message.
  """
  try:
    response = service.users().messages().list(userId=user_id,
                                               labelIds=label_ids,
                                               maxResults=500).execute()

    messages = []
    if 'messages' in response:
      messages.extend(response['messages'])

    while 'nextPageToken' in response:
      page_token = response['nextPageToken']

      response = service.users().messages().list(userId=user_id,
                                                 labelIds=label_ids,
                                                 pageToken=page_token,
                                                 maxResults=500).execute()

      messages.extend(response['messages'])

      print('... total %d emails on next page [page token: %s], %d listed so far' % (len(response['messages']), page_token, len(messages)))
      sys.stdout.flush()

    return messages

  except errors.HttpError as error:
    print('An error occurred: %s' % error)


if __name__ == "__main__":
  print('\n... start')

  # Creating a storage.JSON file with authentication details
  SCOPES = 'https://www.googleapis.com/auth/gmail.modify' # we are using modify and not readonly, as we will be marking the messages Read
  store = file.Storage('storage.json')
  creds = store.get()

  if not creds or creds.invalid:
      flow = client.flow_from_clientsecrets('client_secret.json', SCOPES)
      creds = tools.run_flow(flow, store)

  GMAIL = discovery.build('gmail', 'v1', http=creds.authorize(Http()))

  user_id =  'me'
  label_id_one = 'INBOX'
  label_id_two = 'UNREAD'

  print('\n... list all emails')

  # email_list = ListMessagesWithLabels(GMAIL, user_id, [label_id_one,label_id_two])  # to read unread emails from inbox
  email_list = ListMessagesWithLabels(GMAIL, user_id, [])

  final_list = [ ]

  print('\n... fetching all emails data, this will take some time')
  sys.stdout.flush()


  #exporting the values as .csv
  rows = 0
  file = 'emails_%s.csv' % (strftime("%Y_%m_%d_%H%M%S", gmtime()))
  with open(file, 'w', encoding='utf-8', newline = '') as csvfile:
      fieldnames = ['Subject','DateTime','Message_body']
      writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter = ',')
      writer.writeheader()

      for email in email_list:
        msg_id = email['id'] # get id of individual message
        email_dict = ReadEmailDetails(GMAIL,user_id,msg_id)

        if email_dict is not None:
          writer.writerow(email_dict)
          rows += 1

        if rows > 0 and (rows%50) == 0:
          print('... total %d read so far' % (rows))
          sys.stdout.flush()

  print('... emails exported into %s' % (file))
  print("\n... total %d message retrived" % (rows))
  sys.stdout.flush()


  print('... all Done!')
