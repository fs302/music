#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'fanshen.fs'


import urllib2
from bs4 import BeautifulSoup
import time
import re
import sqlite3
import random

class Music:

    def __init__(self, title, artist, play, album, image, songwriters, composer, arrangement, share):
        self.title = title
        self.artist = artist
        self.play = play
        self.album = album
        self.image = image
        self.songwriters = songwriters
        self.composer = composer
        self.arrangement = arrangement
        self.share = share

    def displayInfo(self):
        return self.title+"|"+self.artist+"|"+self.play+"|"+self.album+"|"+self.image+"|"+self.songwriters+"|"+self.composer+"|"+self.arrangement+"|"+str(self.share)

class Spider:

    count = 0

    def __init__(self):
        self.siteURL = 'http://www.xiami.com'
        self.fileName = 'xiami-5.csv'
        self.cookie = {}
        raw_cookies = 'gid=147416112934312; _unsign_token=096e2a331d57128baa6d5391167d7b0a; cna=RSQ8EIuGQGQCASp4SmcFoUUA; member_auth=2T%2BQHose7D1lgqDAH49hJ3AbsubRGGODxNhVjbYot1YlIdoMN9HwwauSSw9K3CiQrGFJV76c3wJP; user=39424834%22fs302%22%220%22726%22%3Ca+href%3D%27%2Fwebsitehelp%23help9_3%27+%3Efa%3C%2Fa%3E%220%220%22852%2222029598f7%221479108409; bdshare_firstime=1479117719482; __guestplay=MTc3MTYzODE5NywxOzE3NzI5MjEyOTQsMTsxNzcxMDU5MzA1LDE7MjA2NzIzNSwxOzc2MzIsMTs3NjM3LDE7NzU5NSwxOzM4NDUzOSwxOzIwNjcyNDEsMTszODQ1NDUsMTsyMDY3MjQ4LDE7MjExMzI0OCwxOzE3NjkxMTA4ODUsMTs3NTczLDE7MzU4OTUyMiwxOzE3NjkxMTA4ODEsMTsxNzcxMjA5MzI0LDE7MTc2OTM5OTc3MywxOzE3NzAwMjU4MjUsMTsxNzY5ODEzNDI2LDE7Mzg0NjE0LDE%3D; _m_h5_tk=29d54ec6d8d7f646fe819e7dbd395b2a_1479136498582; _m_h5_tk_enc=2338eeeca412163c032d70aaabbebdf1; _xiamitoken=b63f66b6e3c935a9f6c72af6addb6592; XMPLAYER_url=/song/playlist/id/1771331041/object_name/default/object_id/0; XMPLAYER_addSongsToggler=0; XMPLAYER_isOpen=0; CNZZDATA921634=cnzz_eid%3D546959707-1479103921-%26ntime%3D1479179523; CNZZDATA2629111=cnzz_eid%3D1295337304-1479104746-%26ntime%3D1479180347; t_sign_auth=1; l=Au/vsDq47E-zGXCTvxqjpN0H/wn5hUO2; isg=AgcHasmFE7Stl5c7qsn0TJzslr04ldvu8ikR1Nn0Mha9SCcK4dxrPkUCnL_s'
        for line in raw_cookies.split(';'):
            key, value = line.split("=",1)
            self.cookie[key] = value
        self.db = DB()

    def main_spider(self,start,end):
        urlPrefix = "http://www.xiami.com/artist/top-"
        for i in range(start,end+1):
            artistUrl = urlPrefix + str(i)
            songUrls = self.get_song_urls(artistUrl)
            print i,len(songUrls)
            for songUrl in songUrls:
                music = self.get_data(songUrl)
                if music:
                    self.db.insert_data(music)
                time.sleep(0.1)

    def transfer_data(self,fileName,splitor):
        f = open(fileName, "r+")
        for line in f.readlines():
            record = line.split(splitor)
            music = Music(record[1],record[2],record[3],record[4],record[5],record[6],record[7],record[8],int(record[9]))
            if music:
                self.db.insert_data(music)
        f.close()

    def deal_data(self,page):
        soup = BeautifulSoup(page)
        songNodes = soup.find_all("td", class_="song_name")
        songUrls = []
        for node in songNodes:
            songUrls.append(self.siteURL + node.a.attrs['href'])
        return songUrls

    def check_if_chinese(self, page):
        soup = BeautifulSoup(page)
        info = str(soup.select("#artist_profile > div.content.clearfix > table"))
        if ("China" in info or "Taiwan" in info or "Hongkong" in info or "Malaysia" in info):
            return True
        return False

    def get_song_urls(self,preUrl):
        headers = {'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.98 Safari/537.36'}
        headers['referer'] = 'http://www.xiami.com/radio/play/id/'+str(random.randint(1,10000))
        pageNo = 1
        songUrls = []
        while (pageNo<=5):
            request = urllib2.Request(url=preUrl + "?page=" + str(pageNo), headers=headers)
            response = urllib2.urlopen(request).read()
            if self.check_if_chinese(response) == False:
                print "[Not Chinese]",preUrl
                return songUrls
            nextPageUrls = self.deal_data(response)
            songUrls.extend(nextPageUrls)
            if len(nextPageUrls) < 20:
                break
            pageNo = pageNo + 1
            time.sleep(1)
        return songUrls

    def get_data(self,url):
        retry = 3
        while retry>0:
            try:
                headers = {'User-Agent':'Mozilla/5.0 (Windows NT 6.2; Win64; x64; rv:16.0.1) Gecko/20121011 Firefox/16.0.1'}
                request = urllib2.Request(url=url, headers=headers)
                response = urllib2.urlopen(request)
                soup = BeautifulSoup(response.read(),'lxml')

                metadata = soup.find_all("meta")
                metadataMap = {}
                for meta in metadata:
                    if 'property' in meta.attrs:
                        metadataMap[meta.attrs['property']] = meta.attrs['content']

                title = metadataMap['og:title']
                artist = metadataMap['og:music:artist']
                play = metadataMap['og:music:play']
                album = metadataMap['og:music:album']
                image = metadataMap['og:image']
                if (len(soup.find("table",id="albums_info").contents)>5):
                    songwriters = soup.find("table",id="albums_info").contents[5].contents[3].string
                else:
                    songwriters = "\N"
                if (len(soup.find("table",id="albums_info").contents)>7):
                    composer = soup.find("table",id="albums_info").contents[7].contents[3].string
                else:
                    composer = "\N"
                if (len(soup.find("table",id="albums_info").contents)>9):
                    arrangement = soup.find("table",id="albums_info").contents[9].contents[3].string
                else:
                    arrangement = "\N"
                share = 0
                if (soup.find("div", class_="music_counts")):
                    text = soup.find("div", class_="music_counts").find("li",class_="line")
                    nums = re.findall('\d+(?=<span>)', str(text),re.S)
                    if (len(nums)>0):
                        share = int(nums[0])

                music = Music(title.encode('utf-8').replace("\"","#"), artist.encode('utf-8'), play.encode('utf-8'), album.encode('utf-8').replace("\"","#"), image.encode('utf-8'),\
                              songwriters.encode('utf-8'), composer.encode('utf-8'), arrangement.encode('utf-8'), share)
                self.count += 1
                print self.count,music.displayInfo()
                return music
            except Exception,e:
                print Exception,":",e
                time.sleep(5)
            retry -=1

class DB:

    def __init__(self):
        self.database = "./xiami.db"
        self.conn = sqlite3.connect(self.database)

    def drop_table(self):
        self.conn.execute("DROP TABLE IF EXISTS XIAMI_MUSIC;")
        self.conn.commit()
        return

    def create_table(self):

        self.conn.execute('''
        CREATE TABLE IF NOT EXISTS XIAMI_MUSIC (
            id INTEGER PRIMARY KEY	autoincrement,
            key     CHAR(100),
            title 	CHAR(50),
            artist 	CHAR(20),
            play	CHAR(100),
            album	CHAR(50),
            image	CHAR(100),
            songwriters CHAR(20),
            composer	CHAR(20),
            arrangement	CHAR(20),
            share	INT
        );
        ''')

        print "create table XIAMI_MUSIC successfully."

        return

    def insert_data(self, music):

        try:

            sql = '''
                INSERT INTO XIAMI_MUSIC (key,title,artist,play,album,image,songwriters,composer,arrangement,share)
                VALUES ('''
            sql = sql + '\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",%d' % (music.title+'-'+music.artist,music.title,music.artist,\
                                                                          music.play, music.album, music.image, music.songwriters,\
                                                                          music.composer,music.arrangement,music.share)
            sql = sql + ")"

            # print "[execute]",sql
            self.conn.execute(sql)
            self.conn.commit()
        except Exception,e:
            print Exception,":",e

        return

    def __del__(self):
        self.conn.close()

spider = Spider()

spider.main_spider(105,500)
