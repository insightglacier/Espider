#encoding=utf-8
import sys  #菜单
from optparse import OptionParser  #命令行传参

######################
#第三方安装类

######################
#自定义类
#!/usr/bin/env python
#coding=utf-8
import Queue
import urllib    #爬虫
import urllib2  #爬虫
import urlparse
import threading  #多线程

import re   #正则表达式
from threading import Thread
######################
#第三方安装类
from bs4 import BeautifulSoup
######################
import MySQLdb
import time
import httplib
from urlparse import *

from termcolor import colored
#BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE, RESET





#爬虫类
class Crawler:
    def __init__(self,url,threadnum,depth):
##################################

##################################
        self.url = url
        self.threadnum = threadnum
        self.depth = depth

##################################


        self.lock = threading.Lock()
##################################


    #获取当前页面所有url
    def get_all_url(self,url):
        urls = []
        try:
            web = urllib.urlopen(url)
        except:
            pass
        soup =BeautifulSoup(web.read(), "html.parser")
        #通过正则过滤合理的url
        tags_a =soup.findAll(name='a',attrs={'href':re.compile("^https?://")})  #匹配a标签下面   href中的https或者http
        try:
            for tag_a in tags_a:
                if tag_a['href'] not in urls:
                    urls.append(tag_a['href'])
        except:
            pass
        return  urls


    #获取当前页面根url
    def get_root_url(self,url):
    #     reg = r'^https?:\/\/([a-z0-9\-\.]+)[\/\?]?'
    #     m = re.match(reg,url)
    #     uri = m.groups()[0] if m else ''
    #     return uri[uri.rfind('.', 0, uri.rfind('.')) + 1:]
    # #urlparse 模块更好
        r = urlparse(url)
        #ParseResult(scheme='http', netloc='badu.com', path='/1212/2313/3213/4/index.php', params='', query='id=1&i=1', fragment='')
        # print unicode('当前网站根域名:','utf-8')+r.scheme+'://'+r.netloc
        return r.scheme+'://'+r.netloc



    #得到所有本网站相关二级url
    def get_local_urls(self,url):
        rooturl = self.get_root_url(url)
        local_urls = []
        urls = self.get_all_url(url)
        urls = list(set(urls))  #域名去重
        for _url in urls:
           ret = _url
           if rooturl in ret.replace('//','').split('/')[0]:
               local_urls.append(_url)
        return  local_urls

    #得到所有的非本域名的url
    def get_remote_urls(self,url):
        rooturl = self.get_root_url(url)
        remote_urls = []
        urls = self.get_all_url(url)
        for _url in urls:
           ret = self.get_root_url(_url)
           if ret not in remote_urls:
               remote_urls.append(ret)
        return  remote_urls


    def sipder_start(self,url):
        db = MySQLdb.connect (host = "127.0.0.1", user = "root", passwd = "123456", db = "espider")
        cursor = db.cursor ()
        print url
        updatesql = "UPDATE url SET ispider=1 WHERE url like '%s'" % url
        cursor.execute(updatesql)
        db.commit()
        allurl = self.get_all_url(url)
        for url in allurl:
            try:
                r = urlparse(url)
                rooturl = r.scheme+'://'+r.netloc 
                sql = "INSERT INTO url (url,title,ip,webcontainers,ispider) VALUES ('%s','','','',0)" % (rooturl)
                cursor.execute(sql)
                db.commit()
            except:
                db.rollback()





    #多线程分配函数
    def run(self):
        db = MySQLdb.connect (host = "127.0.0.1", user = "root", passwd = "123456", db = "espider")
        cursor = db.cursor ()

        sql = "SELECT url FROM url WHERE ispider=0  limit %d" % int(self.threadnum)
        cursor.execute(sql)
        # 提交到数据库执行
        # print cursor.execute(sql)
        rows = cursor.fetchall()    #cursor.fetchall() 返回所有
        print rows

        while(rows):
            for i in range(10):
                if(rows[i][0]):
                    t = threading.Thread(target=self.sipder_start(rows[i][0]),name=str(i))
                    t.setDaemon(True)
                    t.start()
                    print colored(unicode("当前进程url：",'utf-8')+str(threading.activeCount()),'cyan')


            db = MySQLdb.connect (host = "127.0.0.1", user = "root", passwd = "123456", db = "espider")
            cursor = db.cursor ()

            sql = "SELECT url FROM url WHERE ispider=0  limit %d" % int(self.threadnum)
            cursor.execute(sql)
            # 提交到数据库执行
            # print cursor.execute(sql)
            rows = cursor.fetchall()    #cursor.fetchall() 返回所有

            print rows





if __name__ == '__main__':

    print '''
      _____       _     _
     / ____|     (_)   | |
    | (___  _ __  _  __| | ___ _ __
     \___ \| '_ \| |/ _` |/ _ \ '__|
     ____) | |_) | | (_| |  __/ |
    |_____/| .__/|_|\__,_|\___|_|
           | |
           |_|
    '''
    parser = OptionParser('usage: %prog [options] target')  #创建解析器
    #添加-f参数, 完整参数名是–filename, action的意思是, 得到该参数后, 怎么处理它, 一般使用store来存储起来, 存储的属性名称就是dest里写的filename, help里的内容将会在使用-h打印帮助信息的时候看到
    parser.add_option('-u', '--url',     dest='url',        default=None,          type='string', help='the begin url')
    parser.add_option('-d', '--depth',   dest='depth',      default=5,             type='int',    help='the depth of spider')
    parser.add_option('-t', '--threads', dest='threadnum',  default=10,            type='int',    help='Number of threads. default = 10')
    parser.add_option('-f', '--file',    dest='names_file', default='subnames.txt',type='string', help='Dict file used to brute sub names')
    parser.add_option('-o', '--output',  dest='output',     default=None,          type='string', help='Output file name. default is {target}.txt')

    (options, args) = parser.parse_args(sys.argv) #解析命令行的参数, 并将结果传给options


	# 当不输入参数时，提示帮助信息
    if len(args) < 1:
        parser.print_help()
    else:
        print options.url,options.depth,options.threadnum
        crawler = Crawler(options.url,options.threadnum,options.depth)
        crawler.run()

        # 判断线程如果全部结束就退出程序
        while True:

            if(threading.activeCount() <= 2 ):
                break
            else:

                pass


















#去重
# url_list_uniq = []
# for url in url_list:
#         if url not in url_list_uniq:
#                 url_list_uniq.append(url)
# print url_list_uniq
