# Import the csv module [CSV (Comma Separated Values) - A simple text file format used to store tabular data, like a spreadsheet. Example: Downloading your monthly bank statement as a file that opens perfectly in MS Excel]
import csv

# Import the re module [re (Regular Expression) - A sequence of characters that specifies a search pattern in text. Example: Finding all phone numbers in a large document by searching for a pattern of 10 digits]
import re

# Import sync_playwright from playwright.sync_api [API (Application Programming Interface) - A software intermediary that allows two applications to talk to each other. Example: Google Maps API allows food delivery apps like Zomato to show your delivery driver's location. Playwright Sync API allows Python to directly control a web browser step-by-step]
from playwright.sync_api import sync_playwright

# Define a helper function to carefully handle closing the popup if it appears on the screen
def close_popup_if_present(page):
    # Check if the popup dialog container is visible using the strictly verified locator
    dialog = page.locator('[role="dialog"]')
    
    # If the dialog exists in the DOM [DOM (Document Object Model) - The structure of a webpage. Example: The blueprint of a house showing where walls go] and is visually shown to the user
    if dialog.count() > 0 and dialog.first.is_visible():
        
        # Locate the specific close button using the verified data-testid HTML attribute
        close_btn = page.locator('[data-testid="rating-modal-close"]').first
        
        # Start a try-except block to attempt closing the popup gracefully
        try:
            # Try a standard Playwright click with a short 3000ms timeout
            close_btn.click(timeout=3000)
            
        # Catch any errors (like the button being covered by another invisible element)
        except Exception:
            
            # If standard click fails, use JavaScript evaluation to forcefully dispatch a click event directly inside the browser engine
            page.evaluate("""
                const btn = document.querySelector('[data-testid="rating-modal-close"]');
                if(btn) {
                    btn.dispatchEvent(
                        new MouseEvent('click', {
                            bubbles: true,
                            cancelable: true
                        })
                    );
                }
            """)
        
        # Start another try-except block to wait strictly for the popup overlay to vanish
        try:
            # Wait strictly until the popup overlay disappears completely before letting the script continue
            dialog.first.wait_for(state="hidden", timeout=5000)
            
        # Catch the timeout if the popup takes too long to close visually
        except Exception:
            
            # Pass (ignore) the error and move on, assuming the popup is closed enough to proceed
            pass

# Define a helper function to definitively ensure the sidebar menu is open before clicking lectures
def ensure_sidebar_available(page):
    
    # Locate the verified sidebar toggle arrow
    toggle = page.locator("#fermion-course-item-mobile-sidebar .cursor-pointer").first
    
    # If the toggle button is present and visible, it implies the sidebar is currently closed or collapsed
    if toggle.count() > 0 and toggle.is_visible():
        
        # Click the toggle button to trigger the sidebar to open
        toggle.click()
        
        # Wait 1000 milliseconds for the sidebar CSS expansion animation to complete
        page.wait_for_timeout(1000)

# Define the main execution function to contain all our core logic
def main():
    
    # Start the Playwright context manager [Context Manager - Automatically manages resources, starting them up and shutting them down. Example: Renting a hotel room where cleaning and key return are handled automatically]
    with sync_playwright() as p:
        
        # Launch the Chromium browser [Chromium - The open-source engine behind Google Chrome. Example: The engine inside your car that makes it run]
        browser = p.chromium.launch(
            
            # Set headless mode to False so we can physically see the browser actions on screen [Headless - Running a browser in the background without a visual window to save resources]
            headless=False,
            
            # Add a slow_mo delay of 500 milliseconds between actions to mimic human interaction and prevent anti-bot detection algorithms
            slow_mo=500
        )
        
        # Create a new browser context using the saved login state [Browser Context - An isolated session that holds cookies and login data. Example: Using a VIP pass to skip the login screen]
        context = browser.new_context(
            
            # Pass the JSON file containing the authentication tokens [JSON (JavaScript Object Notation) - A lightweight format for storing data. Example: A restaurant menu sent from the server to your app]
            storage_state="login.json"
        )
        
        # Open a new tab or page within the securely authenticated context
        page = context.new_page()
        
        # --- API INTERCEPTION SETUP ---
        # Create a shared dictionary to store extracted data from intercepted API responses [Dictionary - A data structure that stores data in key-value pairs. Example: A real dictionary where the word is the key and definition is the value]
        current_extracted_data = {}

        # Define a function that will execute every time the browser receives a network response
        def handle_response(response):
            
            # Only process XHR or Fetch requests to avoid parsing heavy images or CSS files [XHR (XMLHttpRequest) - Technology used by browsers to communicate with servers in the background]
            if response.request.resource_type in ["xhr", "fetch"]:
                
                # Start a try-except block to parse the response as JSON data safely
                try:
                    
                    # Convert the raw network response into a native Python dictionary
                    data = response.json()
                    
                    # Define a recursive function to search deeply inside nested JSON structures [Recursive Function - A function that calls itself to dig deeper into layers. Example: Opening Russian nesting dolls one by one]
                    def extract_info(obj):
                        
                        # Check if the current object being inspected is a dictionary
                        if isinstance(obj, dict):
                            
                            # If the dictionary contains the 'title' key, save its value to our shared dictionary
                            if "title" in obj:
                                current_extracted_data["title"] = obj["title"]
                                
                            # If it contains the ISO date key, save it [ISO (International Organization for Standardization) Date - A globally accepted date format like 2026-07-23T09:24:42Z]
                            if "startAtIsoString" in obj:
                                current_extracted_data["startAtIsoString"] = obj["startAtIsoString"]
                                
                            # If it contains the duration key, save its exact value in seconds
                            if "durationInSecs" in obj:
                                current_extracted_data["durationInSecs"] = obj["durationInSecs"]
                                
                            # Loop through all values in the dictionary and call this function again to check nested inner layers
                            for val in obj.values():
                                extract_info(val)
                                
                        # Check if the object is a list of items rather than a dictionary
                        elif isinstance(obj, list):
                            
                            # Loop through every single item in the list and call this function again
                            for item in obj:
                                extract_info(item)
                                
                    # Trigger the recursive search starting on the main JSON data object
                    extract_info(data)
                    
                # Catch any parsing errors (like if the response wasn't actually valid JSON format)
                except Exception:
                    
                    # Silently ignore the error and move on, as not every API call holds the data we need
                    pass
                    
        # Attach our custom listener function to the Playwright page's internal 'response' event
        page.on("response", handle_response)
        # ------------------------------

        # Print a startup progress message to the console terminal
        print("Navigating to dashboard...")
        
        # Navigate to the ThinkNEXT dashboard URL [URL (Uniform Resource Locator) - The unique web address used to locate a specific webpage. Example: Typing www.youtube.com]
        page.goto("https://elearn.thinknext.co.in/user/dashboard")
        
        # Wait for 3000 milliseconds to allow all initial framework elements to load fully
        page.wait_for_timeout(3000)
        
        # Print progress to the console
        print("Opening Networking course...")
        
        # Find the element containing the exact text "Networking" and simulate a mouse click on it
        page.get_by_text("Networking").click()
        
        # Wait for 3000 milliseconds to allow the course page to transition, fetch data, and render completely
        page.wait_for_timeout(3000)
        
        # Print progress to the console
        print("Starting first lecture to load the video player interface...")
        
        # Dynamically locate the first button containing the text "Start lecture:" and click it to trigger the player interface
        page.locator("button:has-text('Start lecture:')").first.click()
        
        # Wait for 3000 milliseconds for the lecture player page and experience popup to manifest on screen
        page.wait_for_timeout(3000)
        
        # Simulate pressing the Escape key on the keyboard as a fast first attempt to dismiss the popup
        page.keyboard.press("Escape")
        
        # Wait for 1000 milliseconds to ensure the popup closing CSS transition finishes smoothly
        page.wait_for_timeout(1000)
        
        # Call our robust helper function to forcefully close the popup if Escape was ignored by the website
        close_popup_if_present(page)
        
        # Print progress to the console
        print("Scanning for authentic lecture links...")
        
        # Locate all anchor (<a>) elements where the 'href' attribute contains the specific lecture URL pattern [Anchor Tag (<a>) - The HTML element used to create clickable hyperlinks. Example: A 'Click Here' text pointing to a new page]
        lecture_links = page.locator("a[href*='/course-item?item-id=']")
        
        # Print the total mathematical count of lecture links found to verify our CSS selector is working flawlessly
        print("Lecture links found:", lecture_links.count())
        
        # Loop through a maximum of 10 items to print a quick sanity-check preview to the console
        for i in range(min(10, lecture_links.count())):
            
            # Extract and print the index number alongside the visible inner text of the link
            print(i, lecture_links.nth(i).inner_text())
        
        # Save the total integer count of verified lecture links found into a master variable
        link_count = lecture_links.count()
        
        # Initialize an empty list to store structured dictionaries of valid, cleaned lectures
        valid_lectures = []
        
        # Initialize an empty set to keep track of lecture hrefs we have already seen to avoid duplicate array entries [Set - A mathematical collection of unique items only. Example: A contact list where you cannot save the same phone number twice]
        seen_hrefs = set()
        
        # Iterate through every single lecture link found on the page using a standard numerical index loop
        for i in range(link_count):
            
            # Create a localized Playwright locator variable pointing to the specific link at the current loop index
            link_locator = lecture_links.nth(i)
            
            # Extract the raw visible inner text of the link and strip away any extra leading or trailing whitespace spaces
            raw_text = link_locator.inner_text().strip()
            
            # Extract the crucial href attribute containing the unique item-id [Attribute - Extra information hidden inside an HTML tag. Example: The 'src' attribute inside an image tag tells the browser where to find the picture file]
            href = link_locator.get_attribute("href")
            
            # Since the inner text might contain multiple garbage lines, split it by newlines and take only the first line which holds the true title
            title = raw_text.split('\n')[0].strip()
            
            # Check if the extracted title string or href string is completely empty
            if not title or not href:
                
                # If empty, skip to the next iteration of the loop without saving garbage data
                continue
                
            # Check if this exact unique href link has already been processed and added to our tracking set
            if href in seen_hrefs:
                
                # If it is a duplicate, skip this link immediately to maintain purely clean data
                continue
                
            # Add the unique href string to our set to guarantee we don't process it again in the future
            seen_hrefs.add(href)
            
            # Append a clean dictionary containing the filtered lecture title and its unique href link to our list of valid lectures
            valid_lectures.append({
                "title": title,
                "href": href
            })
            
        # Print the total number of valid, unique lectures successfully discovered and fully prepped for extraction
        print(f"Successfully discovered {len(valid_lectures)} lectures based on URL patterns. Beginning extraction...")
        
        # Open a new file named 'lectures.csv' in write ('w') mode with UTF-8 encoding to securely support all international special characters
        with open("lectures.csv", "w", encoding="utf-8", newline="") as csvfile:
            
            # Create a CSV writer object specifically responsible for formatting our raw string data into proper comma-separated rows
            writer = csv.writer(csvfile)
            
            # Write the initial header row defining our exact column names to the top of the CSV file
            writer.writerow(["Lecture Title", "Start Date (ISO)", "Duration (Secs)"])
            
            # Initialize a set specifically designed to track hrefs written to the CSV file to strictly deduplicate final file outputs
            written_csv_hrefs = set()
            
            # Start the main heavy loop to iterate through every single valid lecture dictionary in our prepped list
            for lecture in valid_lectures:
                
                # Retrieve the saved title string belonging to the current lecture being processed
                saved_title = lecture["title"]
                
                # Retrieve the exact saved unique href string belonging to the current lecture
                saved_href = lecture["href"]
                
                # Double check absolute deduplication: completely skip processing if we have already written this exact href to the CSV
                if saved_href in written_csv_hrefs:
                    
                    # Continue straight to the next loop iteration
                    continue
                
                # Begin a robust, outer try-except block to prevent a single broken lecture link from crashing the entire automation execution
                try:
                    
                    # Print which specific lecture title is currently being actively processed
                    print(f"Processing: {saved_title}")
                    
                    # Clear any previously intercepted API data from the shared dictionary to ensure entirely fresh data for this lecture
                    current_extracted_data.clear()
                    
                    # Ensure the sidebar is actually open and available BEFORE attempting any locator logic
                    ensure_sidebar_available(page)
                    
                    # Locate the specific anchor link deep in the DOM using its exact unique href attribute
                    lecture_link = page.locator(f'a[href="{saved_href}"]').first
                    
                    # Start the CRITICAL inner try-except block specifically designed to capture timeout crashes safely
                    try:
                        
                        # Command Playwright to click the link. We removed the unprotected scroll logic. The `force=True` parameter tells Playwright to automatically scroll and smash through invisible barriers with a strict 5000ms timeout limit.
                        lecture_link.click(force=True, timeout=5000)
                        
                    # Catch the timeout if React detaches the element or virtualization hides it, which previously crashed the entire script
                    except Exception:
                        
                        # If the native click times out, refresh the sidebar state by clicking the Networking course tab again to force a hard DOM reset
                        page.get_by_text("Networking").click()
                        
                        # Wait 2000 milliseconds for the sidebar component to completely reload from the server
                        page.wait_for_timeout(2000)
                        
                        # Ensure the newly reloaded sidebar is explicitly opened again after the reset
                        ensure_sidebar_available(page)
                        
                        # Execute raw JavaScript injection to click the link directly, entirely bypassing all visual UI rendering bugs, race conditions, and Playwright scroll restrictions
                        page.evaluate(f"""
                            const link = document.querySelector('a[href="{saved_href}"]');
                            if (link) {{
                                link.scrollIntoView();
                                link.click();
                            }}
                        """)
                    
                    # Wait 3000 milliseconds for the new lecture page to visually render completely and for the background API network calls to process
                    page.wait_for_timeout(3000)
                    
                    # Simulate pressing the Escape key to instantly handle any popups that appear after the lecture click resolves
                    page.keyboard.press("Escape")
                    
                    # Wait 1000 milliseconds for the popup closing CSS visual transition to finish
                    page.wait_for_timeout(1000)
                    
                    # Call our extremely robust helper function to definitively kill the popup if it is still blocking the browser screen
                    close_popup_if_present(page)
                    
                    # Wait a final 1500 milliseconds to absolutely guarantee all trailing API JSON responses have fully populated our dictionary
                    page.wait_for_timeout(1500)
                    
                    # Extract the values from our intercepted dictionary, using the `.get()` method to provide a default fallback string ("N/A") if the exact data wasn't found
                    api_title = current_extracted_data.get("title", saved_title)
                    iso_date = current_extracted_data.get("startAtIsoString", "N/A")
                    duration = current_extracted_data.get("durationInSecs", "N/A")
                    
                    # Write the fully extracted and cleaned API data as a brand new permanent row in the CSV file
                    writer.writerow([api_title, iso_date, duration])
                    
                    # Add the successfully processed unique href string to our tracking set to permanently prevent duplicate processing later in the run
                    written_csv_hrefs.add(saved_href)
                    
                    # Print a final success log message confirming the exact data row that was written to the storage file
                    print(f"Saved: {api_title} | {iso_date} | {duration}")
                        
                # Catch any critical, unexpected errors that somehow bypassed the inner loop during the processing cycle for this specific lecture
                except Exception as e:
                    
                    # Print an error message detailing exactly what went wrong, ensuring it does not stop the overall script execution
                    print(f"Failed to process lecture '{saved_title}': {e}. Skipping to next lecture.")
                    
                    # Use the 'continue' keyword to immediately jump back up to the next iteration of the loop to process the next lecture seamlessly
                    continue
                    
        # Print a triumphant final success message indicating the automation script has finished its monumental task completely
        print("Data extraction complete! Saved successfully to lectures.csv")

# Ensure this script runs execution ONLY when it is triggered directly from the terminal, preventing it from running if imported as a background module in another script
if __name__ == "__main__":
    
    # Call the main execution function to actively trigger the entire automation workflow
    main()