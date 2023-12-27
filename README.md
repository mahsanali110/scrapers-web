Web Scrapper:

1. **Subscribe to New Websites:**
   - Open the Config.json file.
   - Add the website links and all elements of respective websites you want to subscribe in config.json.

2. **Main Server:**
   - Run the web.py script, the main server.
   - This script uses the BeautifulSoap to fetch NEWS.
   - Saves the NEWS locally.
   - Sends the NEWS to a web server.

3. **Additional Scripts:**
   - If the Twitter server process is stuck for a prolonged time, run the `kill_web_process.py` script to auto restart the server. 

4. **Scripts To Depoly:**
   - `kill_web_process.py`
   - `web.py`
  
5. **Latest Code:**
   - V7-withmultipleLinks > V2 folder Contains the latest code of Web Scrapper.
   
5. **Flow Chart:**
![WhatsApp Image 2023-11-20 at 4 59 09 PM](https://github.com/si-fahad-nadeem/Scrapers/assets/81758709/44343b61-afa3-4aa4-a7c4-f74ede3168a0)
