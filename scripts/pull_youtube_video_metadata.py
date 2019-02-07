from apiclient.discovery import build
from apiclient.errors import HttpError
from oauth2client.tools import argparser
from datetime import datetime, timedelta
from unidecode import unidecode
import csv, time, json, sys

today = datetime.utcnow()

#Search Parameters
MAX_RESULTS = 50
ORDER = 'viewCount'
PUBLISHED_AFTER = (today + timedelta(days=-1500)).isoformat() + "Z"
SAFE_SEARCH = 'none'

# Retrieve a CSV file of youtube video metadata with respect to
# a given search query
#	config_file: Full file path of the config file containing
#				 your youtube API developer key.
#				 The developer key should be assigned to the key
#				 "DEVELOPER_KEY" in your config file.
#	query: Search query. Videos matching this query will be retrieved
#
def get_youtube_video_metadata(config_file, query):

  # Set developer key and required api call parameters
  params = json.load(open(config_file))
  DEVELOPER_KEY = params["DEVELOPER_KEY"]
  YOUTUBE_API_SERVICE_NAME = "youtube"
  YOUTUBE_API_VERSION = "v3"
  
  # Retrieve desired output location for csv files
  out_loc = params["OUT_LOC"]
  
  youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
    developerKey=DEVELOPER_KEY)

  # Call the search.list method to retrieve results matching the specified
  # query term.
  search_response = youtube.search().list(
    q=query,
    part="id,snippet",
    maxResults=MAX_RESULTS,
	order=ORDER,
	publishedAfter=PUBLISHED_AFTER,
	safeSearch=SAFE_SEARCH,
	type=('video')
  ).execute()
  page_token = search_response['nextPageToken']
  max_records = min(search_response['pageInfo']['totalResults'],800000)

  
  with open("{4}/youtube_{3}_{0}_{1}_{2}.csv".format(str(today.month),str(today.day),str(today.year),query.replace(" ",""),out_loc), 'a+',newline='') as csvfile:

    yt_writer = csv.writer(csvfile, delimiter=',')
    total_results = 0
	
    # Add each result to the appropriate list, and then display the lists of
    # matching videos, channels, and playlists.
    while total_results < max_records:
      if total_results > 0:
        search_response = youtube.search().list(
          q=query,
          part="id,snippet",
          maxResults=MAX_RESULTS,
          order=ORDER,
          publishedAfter=PUBLISHED_AFTER,
          safeSearch=SAFE_SEARCH,
          type=('video'),
          pageToken=page_token
        ).execute()
       # print(search_response['pageInfo']['totalResults'])
        print(total_results)
        print(search_response)
        page_token = search_response['nextPageToken']
      for search_result in search_response.get("items", []):
        record_vals = []
        if search_result["id"]["kind"] == "youtube#video":
          snippet = search_result["snippet"]
          #Add field values to record
          record_vals.append(search_result["id"]["videoId"])
          record_vals.append(snippet["title"])
          record_vals.append(snippet["publishedAt"])
          record_vals.append(snippet["channelId"])
          record_vals.append(snippet["description"])
          record_vals.append(snippet["thumbnails"]["high"]["url"])
          record_vals.append(snippet["channelTitle"])
          yt_writer.writerow([unidecode(x) for x in record_vals])
      total_results = total_results + MAX_RESULTS

if __name__ == "__main__":
  try:
    get_youtube_video_metadata(sys.argv[1],sys.argv[2])
  except HttpError as e:
    print("An HTTP error %d occurred:\n%s" % (e.resp.status, e.content))
