import datetime
import dateutil.relativedelta
import instaloader
import time
import os
import random

# scrape_videos.py scrapes all the videos from pages we are following
def scrapeVideos(username="", password="", output_folder="", days=1):
    print("Starting Scraping")
    
    # Create output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Initialize with instaloader for profile scraping
    L = instaloader.Instaloader(
        download_videos=True,
        download_video_thumbnails=False,
        download_geotags=False,
        download_comments=False,
        save_metadata=False,
        compress_json=False,
        post_metadata_txt_pattern="",
        max_connection_attempts=3,
        request_timeout=30
    )

    try:
        # Try to login directly first
        print(f"Attempting to login as {username}")
        L.login(username, password)
        print("Login successful")
        
        # Wait a bit after login
        time.sleep(5)
        
        try:
            # Try to save session for future use
            L.save_session_to_file(f"{username}_instagram_session")
            print("Session saved successfully")
        except Exception as e:
            print(f"Could not save session: {e}")

        # Verify login was successful
        test_profile = instaloader.Profile.from_username(L.context, username)
        if not test_profile:
            raise Exception("Could not verify login success")

        # Get following with retry mechanism
        max_retries = 5
        retry_count = 0
        while retry_count < max_retries:
            try:
                following = list(test_profile.get_followees())
                print(f"Successfully retrieved {len(following)} following accounts")
                break
            except Exception as e:
                retry_count += 1
                wait_time = 2 ** retry_count + random.uniform(0, 1)  # Exponential backoff with jitter
                print(f"Retry {retry_count}/{max_retries} getting following list. Waiting for {wait_time:.2f} seconds.")
                time.sleep(wait_time)  # Wait between retries
                if retry_count == max_retries:
                    raise Exception(f"Failed to get following list after {max_retries} attempts")

        # Calculate date range
        until_date = datetime.datetime.now()
        since_date = until_date - dateutil.relativedelta.relativedelta(days=days)

        total_downloaded = 0
        
        # Download videos from each following
        for followed_profile in following:
            if total_downloaded >= 50:  # Limit total videos
                break
                
            print(f"\nScraping from account: {followed_profile.username}")
            try:
                posts = followed_profile.get_posts()
                account_downloads = 0

                for post in posts:
                    if post.date_local < since_date:
                        break
                    if post.date_local > until_date:
                        continue

                    if post.is_video and account_downloads < 5:  # Limit per account
                        try:
                            L.download_post(post, target=output_folder)
                            account_downloads += 1
                            total_downloaded += 1
                            print(f"Downloaded video {account_downloads} from {followed_profile.username}")
                            time.sleep(2)  # Delay between downloads
                        except Exception as e:
                            print(f"Failed to download video: {e}")
                            time.sleep(5)  # Longer delay after error
                            continue

                print(f"Downloaded {account_downloads} videos from {followed_profile.username}")
                time.sleep(3)  # Delay between accounts

            except Exception as e:
                print(f"Error scraping {followed_profile.username}: {e}")
                time.sleep(5)  # Delay after error
                continue

        if total_downloaded == 0:
            raise Exception("No videos were downloaded")

        print(f"\nScraping completed! Total videos downloaded: {total_downloaded}")
        return total_downloaded

    except instaloader.exceptions.InstaloaderException as e:
        print("\nInstagram Error! Please follow these steps:")
        print("1. Open Instagram in your browser")
        print("2. Log out of your account")
        print("3. Log back in and verify any security prompts")
        print("4. Delete the session file (if it exists)")
        print("5. Wait 10-15 minutes")
        print("6. Try running the script again")
        print(f"\nDetailed error: {str(e)}")
        raise
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        raise

def download_reel(reel_url):
    # Use instaloader to download the reel
    L = instaloader.Instaloader()
    try:
        L.download_post(reel_url, target="./")  # Download the reel to the current directory
        print("Reel downloaded successfully.")
    except Exception as e:
        print(f"Failed to download reel: {e}")

if __name__ == "__main__":
    scrapeVideos(username="your_username",
                 password="your_password",
                 output_folder="./Memes_Output")
    
    # Example usage of downloading a reel
    download_reel("https://www.instagram.com/reel/XYZ/")  # Replace XYZ with the actual reel ID
