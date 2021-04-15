"""
Prerequisites:
Chrome, Windows (or the same OS used to create the application), Whatsapp in French or English.

To create the application:

pyinstaller --onefile --hidden-import babel.numbers --name WhatsappScraper Whatsapp_Image_Scraper.py
pyinstaller WhatsappScraper.spec

the exe will be in dist (not in build!)

"""

"""
Importing the libraries that we are going to use
for loading the settings file and scraping the website
"""

from selenium import webdriver
from selenium.common.exceptions import (NoSuchElementException,
                                        StaleElementReferenceException)
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import TimeoutException
import chromedriver_autoinstaller

import base64
import dateutil.parser

import datetime
import configparser
import time
import os
import sys

from tkinter import *
from tkinter import filedialog
from tkinter import messagebox
import tkinter.font as tkFont
from tkinter import ttk
from tkcalendar import DateEntry


class WhatsappScrapper():
    def __init__(self):
        self.driver = self.load_driver()
        # Open the web page with the given browser
        self.driver.get('https://web.whatsapp.com')

    def load_driver(self):
        """
        Load the Selenium driver depending on the browser
        (Edge and Safari are not running yet)
        """
        chromedriver_autoinstaller.install(cwd=True)
        driver = webdriver.Chrome()
        return driver

    def open_conversation(self, name):
        """
        Function that searches the specified user by the 'name' and opens the conversation.
        """

        while True:
            for chatter in self.driver.find_elements_by_xpath("//div[@id='pane-side']/div/div/div/div"):
                chatter_path = ".//span[@title='{}']".format(name)
                try:
                    contact = self.driver.find_element_by_xpath("//span[@class=\"_35k-1 _1adfa _3-8er\"][@title=\""+name+"\"]")
                except:
                    print("Search Contact, Using Search Box")
                    search_box_xpath = '//div[@class="_2_1wd copyable-text selectable-text"][@contenteditable="true"][@data-tab="3"][@dir="ltr"]'
                    search_box = WebDriverWait(self.driver,50).until(lambda driver: self.driver.find_element_by_xpath(search_box_xpath))
                    search_box.click()
                    search_box.send_keys(name)
                    time.sleep(1)
                    contact = self.driver.find_element_by_xpath("//span[@class=\"_35k-1 _1adfa _3-8er\"][@title=\""+name+"\"]")
                contact.click()
                print("Contact Found")
                return True


    def read_last_in_message(self):
        """
        Reading the last message that you got in from the chatter
        """
        for messages in self.driver.find_elements_by_xpath(
                "//div[contains(@class,'message-in')]"):
            try:
                message = ""
                emojis = []

                message_container = messages.find_element_by_xpath(
                    ".//div[@class='copyable-text']")

                message = message_container.find_element_by_xpath(
                    ".//span[contains(@class,'selectable-text invisible-space copyable-text')]"
                ).text

                for emoji in message_container.find_elements_by_xpath(
                        ".//img[contains(@class,'selectable-text invisible-space copyable-text')]"
                ):
                    emojis.append(emoji.get_attribute("data-plain-text"))

            except NoSuchElementException:  # In case there are only emojis in the message
                try:
                    message = ""
                    emojis = []
                    message_container = messages.find_element_by_xpath(
                        ".//div[contains(@class,'copyable-text')]")

                    for emoji in message_container.find_elements_by_xpath(
                            ".//img[contains(@class,'selectable-text invisible-space copyable-text')]"
                    ):
                        emojis.append(emoji.get_attribute("data-plain-text"))
                except NoSuchElementException:
                    pass

        return message, emojis

    def send_message(self, text):
        """
        Send a message to the chatter.
        You need to open a conversation with open_conversation()
        before you can use this function.
        """

        input_text = self.driver.find_element_by_xpath(
            "//div[@id='main']/footer/div/div[2]/div/div[@contenteditable='true']")

        input_text.click()
        input_text.send_keys(text)

        send_button = self.driver.find_element_by_xpath(
            "//div[@id='main']/footer/div/div[3]/button")
        send_button.click()

        return True


    def scrapeImages(self, name, download, date_start, date_end, language):
        """
        For now it works for phone languages set to French or English, it can be extended.
        For now it works for images and video. No gif...
        Function:
        1) Creates a folder GroupName_startdate_enddate (if it does not exist yet)
        2) Navigate towards the Media of the whatsapp group and download images and video.
           File name is img_day_month_yearathours_minutes
        3) If a message is sent with the media it is also saved in a txt file.
        4) If more media are sent at the same time the file name an index is included in the file name.
        5) Media not in the selected interval are skipped.
        6) Close web whatsapp when the download is completed
        """

        if (download.endswith('/')): #test if string endswith a d)
            path = download+str(name.replace(" ",""))+"_"+str(date_start.strftime("%d-%m-%Y"))+"_"+str(date_end.strftime("%d-%m-%Y"))
        else:
            path = download+"/"+str(name.replace(" ",""))+"_"+str(date_start.strftime("%d-%m-%Y"))+"_"+str(date_end.strftime("%d-%m-%Y"))
        if not os.path.exists(path):
            os.makedirs(path)
        index_img = 0
        index_video = 0

        menu = self.driver.find_element_by_xpath("(//div[@title=\"Menu\"])[2]")
        menu.click()
        time.sleep(1)
        if language ==1:
            media_xpath = '//span[text()="Media, Links and Docs"]'
            try:
                info = self.driver.find_element_by_xpath("//div[@aria-label=\"Group info\"]")
            except:
                info = self.driver.find_element_by_xpath("//div[@aria-label=\"Contact info\"]")
        elif language ==2:
            media_xpath = '//span[text()="Médias, liens et documents"]'
            try:
                info = self.driver.find_element_by_xpath("//div[@aria-label=\"Infos du groupe\"]")
            except:
                info = self.driver.find_element_by_xpath("//div[@aria-label=\"Infos du contact\"]")

        info.click()
        time.sleep(5)
        """ A check for the time format using the date in which the group has been created. The name of the group and date is hard coded. In this case it only work for POINTS FOCAUX COVID 19, which has been created on March 13 2020.  """
        date_created_str = self.driver.find_element_by_xpath('//span[@class="_37Hn4 _1AJnI _29Iga"]').text
        dayfirst = False
        monthfirst = False
        if name == 'POINTS FOCAUX COVID 19':
            if language == 1:
                xx, yy, zzzz = date_created_str.replace("Created ", "").replace(" ","").split("at")[0].split('/')
            if language ==2:
                xx, yy, zzzz = date_created_str.replace("Créé le ", "").replace(" ","").split("à")[0].split('/')
            group_created = datetime.date(2020, 3, 13) # year, month, day
            if (int(xx) == int(group_created.day) and int(yy) == int(group_created.month)):
                dayfirst = True
            if (int(yy) == int(group_created.day) and int(xx) == int(group_created.month)):
                monthfirst = True
        media = self.driver.find_element_by_xpath(media_xpath)
        media.click()
        time.sleep(5)
        check_boxes = self.driver.find_elements_by_class_name("VxCaw") #("w3gMB")
        check_boxes[0].click()
        time.sleep(2)
        print("==================Getting Images====================")
        while True:
            today = datetime.date.today()
            yesterday = datetime.date.today() - datetime.timedelta(days =1)
            if language == 1:
                today = today.strftime('%d_%m_%Y')
                yesterday = yesterday.strftime('%d_%m_%Y')
            if language == 2:
                today = today.strftime('%m_%d_%Y')
                yesterday = yesterday.strftime('%m_%d_%Y')

            if (date_start>date_end):
                d_temp = date_start
                date_start = date_end
                date_end = d_temp
            try:
                image_xpath ='//img[@class="_3WrZo _1SkhZ _3-8er"]'
                gif_xpath ='//video[@class="_2oX7m"]'
                video_xpath = '//video[@class="_29ubQ"]'
                next_button_path = '//div[@class="_3LLJf _2Op2j SncVf"]'
                caption_xpath = '//span[@class="_1ZtrG _3-8er"]'
                sender_path = '//span[@class="_35k-1 _3-8er"]'

                date = (self.driver.find_elements_by_class_name("_2vfYK")[0]).text.replace(" ","")
                dateOutputfile = (self.driver.find_elements_by_class_name("_2vfYK")[0]).text
                date = date.replace("/","_")
                if "yesterday" in date:
                    date = date.replace("yesterday", yesterday)
                    dateOutputfile = dateOutputfile.replace("yesterday", yesterday)
                if "today" in date:
                    date = date.replace("today", today)
                    dateOutputfile = dateOutputfile.replace("today", today)
                if "hier" in date:
                    date = date.replace("hier", yesterday)
                    dateOutputfile = dateOutputfile.replace("hier", yesterday)
                if "aujourd'hui" in date:
                    date = date.replace("aujourd'hui", today)
                    dateOutputfile = dateOutputfile.replace("aujourd'hui", today)
                date = date.replace(":","_")
                #Date format check. If the month is larger than 12 or if has only 1 digit* than the format is mm/dd/yyyy.
                #* When the format is dd/mm/yyyy the day and the month are express with two digits 1 of February 2021 is "01/02/2021", while when the date format is mm/dd/yyyy this is (often) written as 2/1/2021. Therefore by checking the number of digits I have tried to distinguish the date format.
                if language == 1 or dayfirst==True:
                    if language == 1:
                        dp, mp, yp = date.split("at")[0].split('_')
                    if language == 2:
                        dp, mp, yp = date.split("à")[0].split('_')
                    if len(dp)==1 or len(mp)== 1 or int(mp)>12:
                        mp, dp, yp =date.split("at")[0].split('_')
                elif language ==2 or monthfirst:
                    mp, dp, yp =date.split("à")[0].split('_')
                    if int(mp)>12:
                        dp, mp, yp = date.split("à")[0].split('_')

                date_pic = datetime.date(int(yp), int(mp), int(dp))

                if (date_pic<date_start):
                    close_image_button = self.driver.find_element_by_xpath('//div[@title="Close"]') if language == 1 else self.driver.find_element_by_xpath('//div[@title="Fermer"]')
                    close_image_button.click()
                    self.driver.close()
                    break
                if (date_pic<date_start or date_pic>date_end):
                    raise Exception("Not in the request interval: %s" % str(date_pic))

                try:
                    image = WebDriverWait(self.driver,20).until(lambda driver: self.driver.find_element_by_xpath(image_xpath))
                    image_src = image.get_attribute("src");
                    result = self.driver.execute_async_script("""
                        var uri = arguments[0];
                        var callback = arguments[1];
                        var toBase64 = function(buffer){for(var r,n=new Uint8Array(buffer),t=n.length,a=new Uint8Array(4*Math.ceil(t/3)),i=new Uint8Array(64),o=0,c=0;64>c;++c)i[c]="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/".charCodeAt(c);for(c=0;t-t%3>c;c+=3,o+=4)r=n[c]<<16|n[c+1]<<8|n[c+2],a[o]=i[r>>18],a[o+1]=i[r>>12&63],a[o+2]=i[r>>6&63],a[o+3]=i[63&r];return t%3===1?(r=n[t-1],a[o]=i[r>>2],a[o+1]=i[r<<4&63],a[o+2]=61,a[o+3]=61):t%3===2&&(r=(n[t-2]<<8)+n[t-1],a[o]=i[r>>10],a[o+1]=i[r>>4&63],a[o+2]=i[r<<2&63],a[o+3]=61),new TextDecoder("ascii").decode(a)};
                        var xhr = new XMLHttpRequest();
                        xhr.responseType = 'arraybuffer';
                        xhr.onload = function(){ callback(toBase64(xhr.response)) };
                        xhr.onerror = function(){ callback(xhr.status) };
                        xhr.open('GET', uri);
                        xhr.send();
                        """, image_src)
                    if type(result) == int :
                        raise Exception("Request failed with status %s" % result)
                    final_image = base64.b64decode(result)
                    filename = path+"/"+'img_'+date+'.jpg'  # I assume you have a way of picking unique filenames
                except:
                    video = WebDriverWait(self.driver,20).until(lambda driver: self.driver.find_element_by_xpath(video_xpath))
                    video_src = video.get_attribute("src");
                    result = self.driver.execute_async_script("""
                        var uri = arguments[0];
                        var callback = arguments[1];
                        var toBase64 = function(buffer){for(var r,n=new Uint8Array(buffer),t=n.length,a=new Uint8Array(4*Math.ceil(t/3)),i=new Uint8Array(64),o=0,c=0;64>c;++c)i[c]="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/".charCodeAt(c);for(c=0;t-t%3>c;c+=3,o+=4)r=n[c]<<16|n[c+1]<<8|n[c+2],a[o]=i[r>>18],a[o+1]=i[r>>12&63],a[o+2]=i[r>>6&63],a[o+3]=i[63&r];return t%3===1?(r=n[t-1],a[o]=i[r>>2],a[o+1]=i[r<<4&63],a[o+2]=61,a[o+3]=61):t%3===2&&(r=(n[t-2]<<8)+n[t-1],a[o]=i[r>>10],a[o+1]=i[r>>4&63],a[o+2]=i[r<<2&63],a[o+3]=61),new TextDecoder("ascii").decode(a)};
                        var xhr = new XMLHttpRequest();
                        xhr.responseType = 'arraybuffer';
                        xhr.onload = function(){ callback(toBase64(xhr.response)) };
                        xhr.onerror = function(){ callback(xhr.status) };
                        xhr.open('GET', uri);
                        xhr.send();
                        """, video_src)
                    if type(result) == int :
                        raise Exception("Request failed with status %s" % result)
                    final_video = base64.b64decode(result)
                    videoname = path+"\\"+'video_'+date+'.mp4'  # I assume you have a way of picking unique filenames
                    if os.path.exists(videoname):
                        index_video+=1
                        videoname = path+"\\"+'video_'+date+'_'+str(index_video)+'.mp4'
                    else:
                        index_video=0
                    with open(videoname, 'wb') as f:
                        f.write(final_video)
                        print("Saving "+videoname+", Go To The Next Image")
                    try:
                        mess =  WebDriverWait(self.driver,20).until(lambda driver: self.driver.find_element_by_xpath(caption_xpath)) and self.driver.find_element_by_xpath(caption_xpath).text
                        messagevideoname = videoname.replace("mp4","txt").replace("video", "message_video")
                        file = open(messagevideoname,'w')
                        file.write(dateOutputfile+'\n')
                        file.write(self.driver.find_element_by_xpath(caption_xpath).text+'\n')
                        file.close()
                    except:
                        pass
                    time.sleep(1)
                    next_button = self.driver.find_element_by_xpath(next_button_path) #_2eUNe _3Z6h5 _2Yacq _1XCgf
                    next_button.click()
                    time.sleep(1)

                else:
                    if os.path.exists(filename):
                        index_img+=1
                        filename = path+"/"+'img_'+date+'_'+str(index_img)+'.jpg'
                    else:
                        index_img=0
                    with open(filename, 'wb') as f:
                        f.write(final_image)
                        print("Saving "+filename+", Go To The Next Image")
                    try:
                        mess =  WebDriverWait(self.driver,20).until(lambda driver: self.driver.find_element_by_xpath(caption_xpath)) and self.driver.find_element_by_xpath(caption_xpath).text
                        messageimgname = filename.replace("jpg","txt").replace("img", "message_img")
                        file = open(messageimgname,'w')
                        file.write(dateOutputfile+'\n')
                        file.write(self.driver.find_element_by_xpath(caption_xpath).text+'\n')
                        file.close()
                    except:
                        pass
                    next_button = self.driver.find_element_by_xpath(next_button_path) #_2eUNe _3Z6h5 _2Yacq _1XCgf
                    next_button.click()
                    time.sleep(1)

            except Exception as e:
                try:
                    next_button = self.driver.find_element_by_xpath(next_button_path)
                    next_button.click()
                    time.sleep(1)
                except Exception as err:
                    close_image_button = self.driver.find_element_by_xpath('//div[@title="Close"]') if language == 1 else self.driver.find_element_by_xpath('//div[@title="Fermer"]')
                    close_image_button.click()
                    self.driver.close()
                    break




def load_settings():
    """
    Creates input window
    """

    top = Tk()
    style = ttk.Style(top)
    style.theme_use('clam')
    top.geometry("500x450")
    name_entry = StringVar(top, value='POINTS FOCAUX COVID 19')
    v = IntVar()
    top.sourceFolder = ''

    def chooseDir():
        top.sourceFolder =  filedialog.askdirectory(parent=top, initialdir= "C:", title='Please select a directory')
    # the label for user_name
    Label(top, text = "WHATSAPP DOWNLOAD IMAGES AND VIDEOS", font=tkFont.Font(size='13', weight='bold')).place(x = 40, y = 10)
    Label(top, text = "WHATSAPP TELECHARGER IMAGES ET VIDEOS", font=tkFont.Font(size='13', weight='bold',slant='italic')).place(x = 40, y = 35)

    Label(top, text = "Please fill out ALL fields and choose your download folder", font=tkFont.Font(size='10', weight='bold')).place(x = 65, y = 70)
    Label(top, text = "Veuillez remplir TOUS les champs et choisir votre fichier", font=tkFont.Font(size='10', weight='bold',slant='italic')).place(x = 65, y = 90)
    Chat_name = Label(top, text = "Chat Name:").place(x = 40, y = 130)
    Chat_name = Label(top, text = "Nom du groupe:", font=tkFont.Font(size='9', slant='italic')).place(x = 40, y = 150)
    # the label for user_password
    start = Label(top, text = "From (dd/mm/yyyy):").place(x = 40,  y = 180)
    Label(top, text = "À partir du (jj/mm/aaaa):", font=tkFont.Font(size='9', slant='italic')).place(x = 40,  y = 200)
    stop = Label(top, text = "To (dd/mm/yyyy):").place(x = 40,  y = 230)
    Label(top, text = "Jusqu’au (jj/mm/aaaa):", font=tkFont.Font(size='9', slant='italic')).place(x = 40,  y = 250)
    download_folder = Label(top, text = "Download in:").place(x = 40,  y = 280)
    Label(top, text = "Sauvegarder:", font=tkFont.Font(size='9', slant='italic')).place(x = 40,  y = 300)
    #
    b_chooseDir = Button(top, text = "Choose Folder/Choisir Fichier", width = 25, command = chooseDir)
    b_chooseDir.place(x = 180,  y = 290)
    #
    lang = Label(top, text = "Smartphone language:").place(x = 40,  y = 330)
    Label(top, text = "Langue du smartphone:", font=tkFont.Font(size='9', slant='italic')).place(x = 40,  y = 350)
    eng = Radiobutton(top, text='English', variable=v, value=1)
    eng.pack(anchor=W)
    eng.place(x = 180, y = 330)
    french = Radiobutton(top, text='Français', variable=v, value=2)
    french.pack(anchor=W)
    french.place(x = 180, y = 350)
    #
    submit_button = Button(top, text = "Submit/Continuer", command = top.quit)
    submit_button.place(x = 200,  y = 400)
    #
    user_name_input_area = Entry(top, textvariable=name_entry, width = 30)
    user_name_input_area.place(x = 180, y = 140)
    date_start_entry = DateEntry(top, width=12, background='darkblue',
                    foreground='white', borderwidth=2, year=2021, date_pattern='dd/mm/yyyy')
    date_start_entry.set_date(datetime.date.today() - datetime.timedelta(days =1))
    date_start_entry.place(x = 180, y = 190)
    date_stop_entry = DateEntry(top, width=12, background='darkblue',
                    foreground='white', borderwidth=2, year=2021, date_pattern='dd/mm/yyyy')
    date_stop_entry.place(x = 180, y = 240)

    def on_closing():
        top.destroy()
        sys.exit()
    top.protocol("WM_DELETE_WINDOW", on_closing)
    top.mainloop()

    if not name_entry.get() or not date_start_entry.get_date() or not date_stop_entry.get_date() or not v.get():
        if messagebox.askretrycancel("error", "Please fill out all the required fields\nVeuillez remplir tous les champs")== False:
            sys.exit()
        else:
            top.mainloop()

    name = name_entry.get()
    date_start = date_start_entry.get_date()
    date_end = date_stop_entry.get_date()
    download = top.sourceFolder

    settings = {
        'name': name,
        'download': download,
        'date_start' : date_start,
        'date_end' : date_end,
        'language' : v.get()
    }
    return settings

def exitApp():
    """
    Creates pup-up when the download is completed
    """
    MsgBox = messagebox.showinfo("Info", "All images and videos scraped!\nToutes les images et vidéos ont été téléchargées!")
    if MsgBox == 'Ok':
        root.destroy()

def main():
    """
    Loading all the configuration and opening the website
    (Browser profile where whatsapp web is already scanned)
    """
    settings = load_settings()
    scrapper = WhatsappScrapper()

    if scrapper.open_conversation(settings['name']):
        scrapper.scrapeImages(settings['name'], settings['download'], settings['date_start'], settings['date_end'], settings['language'])
        exitApp()

if __name__ == '__main__':
    main()
