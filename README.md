# whatsapp-scraper

Whatsapp Images and Videos Scraper

Code Documentation
Fabrizia Canfora (March 2021)

Code: Whatsapp_Image_Scraper.py
Python script to download images and video from a chat in an interval of time.

Functions in the class WhatsappScrapper():

__init__ = Opens the web page with the given browser.

load_driver = Loads the Selenium driver depending on the browser, at the moment only works for Chrome, but can be extended to Firefox.

open_conversation(name) =  Searches the specified user by the 'name' and opens the conversation. It first tries to find the contact name between the last chats in the home page, otherwise it searches using the search box.

read_last_in_message = it is not used for this application, it can be useful in case the code is extended to download text messages. It reads the last received messages.

send_message(message) = this is also not used in this application in particular. It might be a useful starting point for further development of the program. And it is useful for debugging.

scrapeImages(name, download, date_start, date_end, language) = this is the main function of this application and it is explained in detail in the next section. 

Other functions:

 load_settings = it uses tkInter to create a pop up window to insert the input parameters. 
Chat Name: default “POINTS FOCAUX COVID 19”;
Start Date: default ‘yesterday’;
End Date: default ‘today’;
Download Folder: initial directory “C:”, it can be changed in the function chooseDir ;
Language of the smartphone: for now English or French, in can be extended;

When one of the fields is left empty an error message appears and it is possible to try again.  

exitApp =  it uses tkInter to create a pop up window when all the images and video have been scraped. Closing this window also terminates the program. 

Function scrapeImages(name, download, date_start, date_end, language) 

It works for phone languages set to French or English, it can be extended.
It works for images and video. No gif…
It also checks whether a message has been sent with the image or video and it saves it in a text file. 
       
        Creates a folder GroupName_startdate_enddate (if it does not exist yet).
 Navigate towards the Media of the whatsapp group. Here it uses the language information, therefore including more languages means to expand this first part with more options.
I have included some checks to try to understand the format of the date in web whatsapp. The format of the date dd/mm/yyyy or mm/dd/yyyy changes with the language (also between english UK and english Netherlands). The basic assumption is english dd/mm/yyyy and french mm/dd/yyyy. However I could include a few check:
When the day or the month have only one digit, for instance 3/26/2021 the month is first. 
When the month > 12 then it is not a month…
Hardcoded creation date of the group. Ugly, but it works also when the date is 12/10/2021. By comparing the format that is written in the web whatsapp page and the input value, it sets the right date format.
When the time interval includes ‘yesterday’ or ‘today’ the string is converted in the date. This is done separately for the two languages. 
At first it tries to download the media file as an image. If it fails, it tries the video. 
Media not in the selected interval are skipped.
Close web whatsapp when the download is completed



How create the application with pyinstaller :

pyinstaller --onefile --hidden-import babel.numbers --name WhatsappScraper Whatsapp_Image_Scraper.py
pyinstaller WhatsappScraper.spec

--hidden-import babel.numbers is important for the calendar option. 
The executable will be in dist.


