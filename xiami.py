#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'fanshen.fs'


import urllib2
from bs4 import BeautifulSoup
import time
import re
from fake_useragent import UserAgent

class Music:

    def __init__(self, title, artist, play, album, image, songwriters, composer, arrangement, shareNum):
        self.title = title
        self.artist = artist
        self.play = play
        self.album = album
        self.image = image
        self.songwriters = songwriters
        self.composer = composer
        self.arrangement = arrangement
        self.shareNum = shareNum

    def displayInfo(self):
        return self.title+","+self.artist+","+self.play+","+self.album+","+self.image+","+self.songwriters+","+self.composer+","+self.arrangement+","+self.shareNum

class Spider:

    count = 0

    def __init__(self):
        self.siteURL = 'http://www.xiami.com'
        self.fileName = 'xiami.csv'

    def main_spider(self,start,end):
        f = open(self.fileName, "w+")
        urlPrefix = "http://www.xiami.com/artist/top-"
        for i in range(start,end+1):
            artistUrl = urlPrefix + str(i)
            songUrls = self.get_song_urls(artistUrl)
            print i,len(songUrls)
            datas = []
            for songUrl in songUrls:
                info = self.get_data(songUrl)
                if (info and len(info)>0):
                    datas.append(str(self.count)+","+str(info.encode('utf-8')+"\n"))
                time.sleep(1)
            f.writelines(datas)
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
        pageNo = 1
        songUrls = []
        while (pageNo<10):
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
            time.sleep(3)
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
                shareNum = 0
                if (soup.find("div", class_="music_counts")):
                    text = soup.find("div", class_="music_counts").find("li",class_="line")
                    nums = re.findall('\d+(?=<span>)', str(text),re.S)
                    if (len(nums)>0):
                        shareNum = nums[0]
                music = Music(title, artist, play, album, image, songwriters, composer, arrangement, shareNum)
                self.count += 1
                print self.count,music.displayInfo()
                return music.displayInfo()
            except Exception,e:
                print Exception,":",e
                time.sleep(5)
            retry -=1

spider = Spider()

spider.main_spider(500,1000)