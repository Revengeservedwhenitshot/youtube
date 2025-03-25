from scrape_videos import scrapeVideos
from make_compilation import makeCompilation
from upload_ytvid import uploadYtvid
import schedule
import time
import datetime
import os
import shutil
import googleapiclient.errors
from googleapiclient.discovery import build #pip install google-api-python-client
from google_auth_oauthlib.flow import InstalledAppFlow #pip install google-auth-oauthlib
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import config
from seo_optimizer import SEOOptimizer

num_to_month = {
    1: "Jan",
    2: "Feb",
    3: "Mar",
    4: "Apr",
    5: "May",
    6: "June",
    7: "July",
    8: "Aug",
    9: "Sept",
    10: "Oct",
    11: "Nov",
    12: "Dec"
} 

# USER VARIABLES FILL THESE OUT (fill out username and password in config.py)
IG_USERNAME = config.IG_USERNAME
IG_PASSWORD = config.IG_PASSWORD
print(IG_USERNAME)
print(IG_PASSWORD)
title = "TRY NOT TO LAUGH (BEST Dank video memes) V1"
now = datetime.datetime.now()
videoDirectory = "./DankMemes_" + num_to_month[now.month].upper() + "_" + str(now.year) + "_V" + str(now.day) + "/"
outputFile = "./" + num_to_month[now.month].upper() + "_" + str(now.year) + "_v" + str(now.day) + ".mp4"

INTRO_VID = '' # SET AS '' IF YOU DONT HAVE ONE
OUTRO_VID = ''
TOTAL_VID_LENGTH = 13*60
MAX_CLIP_LENGTH = 19
MIN_CLIP_LENGTH = 5
DAILY_SCHEDULED_TIME = "20:00"
TOKEN_NAME = "token.json" # Don't change

# Setup Google 
SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
client_secrets_file = "googleAPI.json"

def makeShort(videoDirectory, shortNumber):
    shortOutputFile = f"./SHORT_{num_to_month[now.month].upper()}_{str(now.year)}_v{str(now.day)}_{shortNumber}.mp4"
    shortDescription = "Enjoy this short! :) \n\n" \
    "like and subscribe for more \n\n" \
    "#shorts #memes #viral #funny #trending"
    
    # Make a shorter compilation for YouTube Shorts
    print(f"Making Short #{shortNumber}...")
    makeCompilation(path = videoDirectory,
                    introName = '',  # No intro for shorts
                    outroName = '',  # No outro for shorts
                    totalVidLength = 60,  # Shorts must be 60 seconds or less
                    maxClipLength = 15,
                    minClipLength = 3,
                    outputFile = shortOutputFile)
    print(f"Made Short #{shortNumber}!")
    
    return shortOutputFile, shortDescription

def routine():

    # Handle GoogleAPI oauthStuff
    print("Handling GoogleAPI")
    creds = None
    # The file token1.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists(TOKEN_NAME):
        creds = Credentials.from_authorized_user_file(TOKEN_NAME, SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                client_secrets_file, SCOPES)
            creds = flow.run_console()
        # Save the credentials for the next run
        with open(TOKEN_NAME, 'w') as token:
            token.write(creds.to_json())

    googleAPI = build('youtube', 'v3', credentials=creds)

    now = datetime.datetime.now()
    print(now.year, now.month, now.day, now.hour, now.minute, now.second)
    
    #metadataFile = "./metadata-" + num_to_month[now.month].upper() + "_" + str(now.year) + "_v" + str(now.day) + ".txt"
    description = ""
    print(outputFile)

    if not os.path.exists(videoDirectory):
        os.makedirs(videoDirectory)
    
    # Step 1: Scrape Videos
    print("Scraping Videos...")
    scrapeVideos(username = IG_USERNAME,
                 password = IG_PASSWORD,
                 output_folder = videoDirectory,
                  days=1)
    print("Scraped Videos!")
    
    description = "Enjoy the memes! :) \n\n" \
    "like and subscribe to @Chewy for more \n\n" \

    seo = SEOOptimizer()
    
    # Generate SEO optimized title and tags for main video
    main_title = seo.generate_title(is_short=False)
    main_tags = seo.generate_tags(is_short=False)
    
    # Step 2: Make Compilation
    print("Making Main Compilation...")
    makeCompilation(path = videoDirectory,
                    introName = INTRO_VID,
                    outroName = OUTRO_VID,
                    totalVidLength = TOTAL_VID_LENGTH,
                    maxClipLength = MAX_CLIP_LENGTH,
                    minClipLength = MIN_CLIP_LENGTH,
                    outputFile = outputFile)
    print("Made Main Compilation!")
    
    description += "\n\nCopyright Disclaimer, Under Section 107 of the Copyright Act 1976, allowance is made for 'fair use' for purposes such as criticism, comment, news reporting, teaching, scholarship, and research. Fair use is a use permitted by copyright statute that might otherwise be infringing. Non-profit, educational or personal use tips the balance in favor of fair use.\n\n"
    description += "#memes #dankmemes #compilation #funny #funnyvideos \n\n"

    # Make and upload two shorts
    for i in range(1, 3):
        shortFile, shortDescription = makeShort(videoDirectory, i)
        
        # Generate SEO optimized title and tags for shorts
        short_title = seo.generate_title(is_short=True)
        short_tags = seo.generate_tags(is_short=True)
        
        print(f"Uploading Short #{i} to Youtube...")
        uploadYtvid(VIDEO_FILE_NAME=shortFile,
                    title=short_title,
                    description=shortDescription,
                    tags=short_tags,
                    googleAPI=googleAPI)
        print(f"Uploaded Short #{i} To Youtube!")
        
        # Clean up short file
        try:
            os.remove(shortFile)
        except OSError as e:
            print(f"Error removing short {i}: %s - %s." % (e.filename, e.strerror))

    # Step 3: Upload main video to Youtube
    print("Uploading to Youtube...")
    uploadYtvid(VIDEO_FILE_NAME=outputFile,
                title=main_title,
                description=description,
                tags=main_tags,
                googleAPI=googleAPI)
    print("Uploaded To Youtube!")
    
    # Step 4: Cleanup
    print("Removing temp files!")
    # Delete all files made:
    #   Folder videoDirectory
    shutil.rmtree(videoDirectory, ignore_errors=True)
    #   File outputFile
    try:
        os.remove(outputFile)
    except OSError as e:  ## if failed, report it back to the user ##
        print ("Error: %s - %s." % (e.filename, e.strerror))
    print("Removed temp files!")

def attemptRoutine():
    while(1):
        try:
            routine()
            break
        except OSError as err:
            print("Routine Failed on " + "OS error: {0}".format(err))
            time.sleep(60*60)

#attemptRoutine()
# schedule.every().day.at(DAILY_SCHEDULED_TIME).do(attemptRoutine)

# Directly call the attemptRoutine function
attemptRoutine()

# Remove or comment out the infinite loop for scheduling
# while True:
#     schedule.run_pending()  
#     time.sleep(60) # wait one min

