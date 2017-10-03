# - coding:utf-8 -
__author__ = 'deadfish'  
__version__ = 'V2.0 all Ranking and bookmarks'

import urllib, urllib2, cookielib, re, os
from bs4 import BeautifulSoup
from threading import *

class Pixiv_reptile:
    def __init__(self):
        self.cookieFile = "pxCookie.txt"
        self.userAgent = ['Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36',\
        'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:47.0) Gecko/20100101 Firefox/47.0']
        self.pxDUrl = {# url列表
        'bookmark': 'http://www.pixiv.net/bookmark.php?type=user',
        'painter':'painter',
        'international': 'http://www.pixiv.net/ranking_area.php?type=detail&no=6',
        'china': 'http://www.pixiv.net/ranking_area.php?type=detail&no=4',
        'hokkaido': 'http://www.pixiv.net/ranking_area.php?type=detail&no=0',
        'male': 'http://www.pixiv.net/ranking.php?mode=male',
        'daily': 'http://www.pixiv.net/ranking.php?mode=daily',
        'weekly': 'http://www.pixiv.net/ranking.php?mode=weekly',
        'monthly': 'http://www.pixiv.net/ranking.php?mode=monthly',
        'daily_r18': 'http://www.pixiv.net/ranking.php?mode=daily_r18',
        'weekly_r18': 'http://www.pixiv.net/ranking.php?mode=weekly_r18',
        'male_r18': 'http://www.pixiv.net/ranking.php?mode=male_r18'
        }
        self.BookMark = {
        'followpage': 'http://www.pixiv.net/bookmark.php?type=user&rest=show&p=',
        'painterurl': 'http://www.pixiv.net/member_illust.php?id='
        }
        self.agentSelect = 0    #访问的客户机
        self.opener = None      #用于打开网页
        self.BOOKMARK_N = 48    #关注用户一页的数目
        self.PAINTER_WORKS_N = 20#用户一页作品的数目
        self.Fails = 0          #线程失败次数
        self.MAX_SEMAPH = 8     #线程最大数目
        self.downloadImg_lock = BoundedSemaphore(value=self.MAX_SEMAPH)#线程控制
    def login(self, username, password):
        loginUrl = "https://www.pixiv.net/login.php"
        # 登陆页面信息
        data = {'mode': 'login','pixiv_id': username,'pass': password,'skip': 1}
        loginData = urllib.urlencode(data)
        # 登陆请求头
        header = {
        'Accept-Language': 'zh-CN,zh;q=0.8',
        'Referer': 'http://www.pixiv.net/',
        'User-Agent': self.userAgent[self.agentSelect]}
        request = urllib2.Request(url=loginUrl, data=loginData, headers=header) 
        try:
            cookie = cookielib.MozillaCookieJar(self.cookieFile) # cookie存储
            self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookie))
            response = self.opener.open(request) #利用请求头与cookie登陆
            ifLogin = response.read().split('\n')[0]
            if ifLogin != "<!DOCTYPE html>":
                print u"\033[1;35;40m你是我大FFF的成员么 赶快注册一个吧\033[0m"
                exit(0)
            else:
                print u"登陆成功鸟(￣▽￣) "
            cookie.save(ignore_discard=True, ignore_expires=True)   #保存 cookie
        except urllib2.URLError,e:
            if hasattr(e,"reason"):
                print u"服务器抽风了",e.reason
    # 采用cookie方式登陆
    def cookie_Login(self):
        cookie_login = cookielib.MozillaCookieJar()
        cookie_login.load(self.cookieFile, ignore_discard=True, ignore_expires=True)
        self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookie_login))
    # 要获得原图信息 还需要refer请求
    def download_Request(self, makeUrl, realUrl):
        header = {'Accept-Language':'zh-CN,zh;q=0.8',
        'User-Agent': self.userAgent[self.agentSelect]}
        header['Referer'] = makeUrl
        request = urllib2.Request(url=realUrl.group(1), headers=header)
        decodeUrl = self.opener.open(request)
        return decodeUrl.read()
    # 调整链接到正确状态
    def tool_StripStrange(self, url):
        urlSet = url.split('amp;')   #真正的地址是没有amp;这样的
        makeUrl = urlSet[0] + urlSet[1]
        #保证makeUrl最后一位为数字
        re_digital = re.compile("\d+")
        while(re_digital.findall(makeUrl[-1]) == []):
            makeUrl = makeUrl[:-1]    #这里有点奇葩//正则表达式不熟 就这样写了
        return makeUrl
    # 给予选择的入口函数
    def choice_Select(self, pxChoice):
        try:
            pxDirOrign = os.getcwd()   #获取当前路径
            destDir = pxDirOrign + '\\' + pxChoice + '\\'
            if os.path.exists(destDir) == False:
                os.mkdir(destDir)#生成图片存储目录
            if pxChoice == 'painter':
                print u"输入ID"
                uID = raw_input()
                self.painter_Download(destDir, uID, None)
                return
            page = self.opener.open(self.pxDUrl[pxChoice])
            pageOrign = page.read()
            if pxChoice == 'bookmark':
                self.down_Follow(pageOrign, destDir)
                return
            self.pixiv_Ranking(pageOrign, destDir)
        except urllib2.URLError, e:
            if hasattr(e, "reason"):
                print u"服务器抽了.", str(e)
    def pixiv_Ranking(self, pageOrign, destDir):
        soup = BeautifulSoup(pageOrign, 'lxml')
        os.system("cls")    #清空目前输出
        for i in range(1, 51):    #查找排名前50
            info = str(soup.find(id=i))
            urlDict = {}
            urlDict['Single'] = urlDict['Multiple'] = urlDict['Video'] = urlDict['Manga_multiple'] = None
            reSingle = re.search(re.compile('<a\sclass="work\s_work\s"\shref="(.*?)">', re.S),info)
            if reSingle != None:
                urlDict['Single'] = reSingle.group(1)
            reMultiple = re.search(re.compile('<a\sclass="work\s_work\smultiple\s"\shref="(.*?)">', re.S),info)
            if reMultiple != None:
                urlDict['Multiple'] = reMultiple.group(1)
            reVideo = re.search(re.compile('<a\sclass="work\s_work\sugoku-illust\s"\shref="(.*?)">',re.S),info)
            if reVideo != None:
                urlDict['Video'] = reVideo.group(1)
            reManga_multiple = re.search(re.compile('<a\sclass="work\s_work\smanga\smultiple\s"\shref="(.*?)">',re.S),info)
            if reManga_multiple != None:
                urlDict['Manga_multiple'] = reManga_multiple.group(1)
            self.download_Pic(destDir, urlDict)
        print u"\033[1;33;40m捕获队伍派遣完毕\033[0m"
    # 把数据写入文件
    def write_Pic(self, makeUrl, realUrl, destDir):
        try:
            pName = realUrl.group(1).split('/')[-1]
            fileName = os.path.join(destDir, 'p_' + pName)
            file_pic = open(fileName, 'wb')
            file_pic.write(self.download_Request(makeUrl, realUrl))
        except:
            self.Fails += 1
        finally:    #释放进程
            self.downloadImg_lock.release()
            file_pic.close()
            print u"捕获 (*ˉ﹃ˉ)"
    # 单个图片
    def down_Single(self, Url, destDir):
        makeUrl = Url
        soup = BeautifulSoup(self.opener.open(makeUrl), 'lxml')
        # orignal-image 标签的img就是存储的原图地址
        realUrl = re.search(re.compile('.*?data-src="(.*?)"',re.S),str(soup.find_all("img",class_="original-image")))
        if realUrl != None:
            print u'全舰数据准备中(\'=\')'
            self.downloadImg_lock.acquire()
            t = Thread(target=self.write_Pic, args=(makeUrl, realUrl, destDir))
            child = t.start()
        else:
            print u"出错了 话说你是组织的人么"
            exit(0)
    # work _wok maga multi 类型的图片
    def down_Multiple(self, Url, destDir):
        soup = BeautifulSoup(self.opener.open(Url), 'lxml')
        num = re.search(re.compile('</li><li>.*?\s(.*?)P</li>', re.S), str(soup.find_all("ul", class_="meta")))
        if num == None:
            return
        print u"总数: " + num.group(1)
        for i in range(int(num.group(1))):
            # <a href="/member_illust.php?mode=manga_big&amp;illust_id=57879081&amp;page=0" target="_blank" class="full-size-container _ui-tooltip" data-tooltip="显示原图">
            mPicUrl = (re.sub(re.compile('mode=medium'),"mode=manga_big", Url)).strip()
            makeUrl = mPicUrl + '&page=' + str(i)
            mSoup = BeautifulSoup(self.opener.open(makeUrl), 'lxml')
            # <img src="http://i2.pixiv.net/img-original/img/2016/07/13/01/10/49/57879081_p6.png" onclick="(window.open('', '_self')).close()">
            realUrl = re.search(re.compile('<img.*?src="(.*?)"/>',re.S),str(mSoup.find_all("img")))
            self.downloadImg_lock.acquire()
            t = Thread(target=self.write_Pic, args=(makeUrl, realUrl, destDir))
            child = t.start()
            print str(i+1)
    # 解析到跳转的链接
    def download_Pic(self, destDir, urlDict):
        if self.Fails > self.MAX_SEMAPH:
            print u"补给不足 正在撤退"
            exit(0)
        urlSingle = urlDict['Single']
        urlMultiple = urlDict['Multiple']
        urlVideo = urlDict['Video']
        urlManga_multiple = urlDict['Manga_multiple']
        makeUrl = ''
        if (urlSingle != None):
            makeUrl = 'http://www.pixiv.net/' + self.tool_StripStrange(urlSingle)
            print u"\033[1;36;40m[*] 遭遇一只图君 (●′ω`●)" + "\033[0m"  #打印要添加u否则会乱码
            self.down_Single(makeUrl, destDir)
        if (urlMultiple != None):
            print u"\033[1;33;40m[!] 高能预警，大波图君(￣^￣) \033[0m"
            makeUrl = 'http://www.pixiv.net/' + self.tool_StripStrange(urlMultiple)
            self.down_Multiple(makeUrl, destDir)
        if (urlVideo != None):
            print u"这是啥, 我也不知道啊\n"
        if (urlManga_multiple != None):
            makeUrl = 'http://www.pixiv.net/' + self.tool_StripStrange(urlManga_multiple)
            print u"\033[1;34;40m[!] 高能预警，大波图君(￣^￣) \033[0m"
            self.down_Multiple(makeUrl, destDir)

    def down_Follow(self, pageOrign, destDir):
        os.system("cls")
        soup = BeautifulSoup(pageOrign, 'lxml')
        unitCount = soup.find_all(class_="unit-count")
        nFollow = re.findall(re.compile('(\d+)', re.S), str(unitCount))
        nFollow = int(nFollow[0])
        print u"你关注了 " + str(nFollow) + u" 位大触"
        nFollowPage = (nFollow/self.BOOKMARK_N)
        if (nFollow % self.BOOKMARK_N) != 0:
            nFollowPage += 1
        print 'page:' + str(nFollowPage)
        for i in range(1, nFollowPage + 1):
            followPage = self.BookMark['followpage'] + str(i) #获得关注人第i页url
            self.painter_PageData(followPage, destDir)
    # 获得一页画师信息
    def painter_PageData(self, followpage, destDir):
        soup = BeautifulSoup(self.opener.open(followpage), 'lxml')
        userData = soup.find_all(class_="userdata")
        nameList = re.findall(re.compile('data-user_name="(.*?)"', re.S), str(userData))
        idList = re.findall(re.compile('data-user_id="(.*?)"', re.S), str(userData))
        for i in range(len(idList)):
            painterName = nameList[i]
            painterID = idList[i]
            self.painter_Download(destDir, painterID, painterName)

    def painter_Download(self, destDir, painterID, painterName):
        if painterID == None:
            return False
        painterUrl = self.BookMark['painterurl'] + str(painterID)
        soupPage = BeautifulSoup(self.opener.open(painterUrl), 'lxml')
        if painterName == None:
            uNameTag = soupPage.find_all(class_="_unit profile-unit")
            uName = re.findall(re.compile('<h1 class="user">(.*?)</h1>', re.S), str(uNameTag))
            painterName = str(uName[0])
        painterDir = destDir + 'id=' + str(painterID) + '\\'  
        if os.path.exists(painterDir) == False:
            os.mkdir(painterDir)#生成画师存储目录 由于可能乱码 所以直接用id来存目录
        print u"正在跪求大大 " + painterName.encode('utf-8') + u" 的作品"
        moreWorks = soupPage.find_all(class_="count-badge")
        nWorks = re.findall(re.compile('>(\d+).*?<', re.S), str(moreWorks))
        nWorks = int(nWorks[0])
        print u"画师有" + str(nWorks) +u"个作品"
        painterWorksPage = (nWorks/self.PAINTER_WORKS_N)
        if (nWorks % self.PAINTER_WORKS_N) != 0:  #判断一共有多少页
            painterWorksPage += 1
        print u"有" + str(painterWorksPage) + u"页"
        for p in range(1, painterWorksPage+1):
            print u"正在下载第" + str(p) + u"页作品"
            soupPage = BeautifulSoup(self.opener.open(painterUrl + "&type=all&p=" + str(p)), 'lxml')
            SingleList = re.findall(re.compile('<a\sclass="work\s_work\s"\shref="(.*?)">',re.S),str(soupPage))
            MultipleList = re.findall(re.compile('<a\sclass="work\s_work\smultiple\s"\shref="(.*?)">', re.S),str(soupPage))
            VideoList = re.findall(re.compile('<a\sclass="work\s_work\sugoku-illust\s"\shref="(.*?)">',re.S),str(soupPage))
            Manga_multipleList = re.findall(re.compile('<a\sclass="work\s_work\smanga\smultiple\s"\shref="(.*?)">',re.S),str(soupPage))
            urlDict = {}
            urlDict['Single'] = urlDict['Multiple'] = urlDict['Video'] = urlDict['Manga_multiple'] = None
            for worksUrl in SingleList:
                urlDict['Single'] = worksUrl
                self.download_Pic(painterDir, urlDict)
            urlDict['Single'] = urlDict['Multiple'] = urlDict['Video'] = urlDict['Manga_multiple'] = None
            for worksUrl in MultipleList:
                urlDict['Multiple'] = worksUrl
                self.download_Pic(painterDir, urlDict)
            urlDict['Single'] = urlDict['Multiple'] = urlDict['Video'] = urlDict['Manga_multiple'] = None
            for worksUrl in VideoList:
                urlDict['Video'] = worksUrl
                self.download_Pic(painterDir, urlDict)
            urlDict['Single'] = urlDict['Multiple'] = urlDict['Video'] = urlDict['Manga_multiple'] = None
            for worksUrl in Manga_multipleList:
                urlDict['Manga_multiple'] = worksUrl
                self.download_Pic(painterDir, urlDict)

def main():
    px = Pixiv_reptile()
    print u"要输入一个排行类别 具体名字你自己找吧(￣^￣)"
    choice = raw_input()
    while px.pxDUrl.has_key(choice) == False:
        print u"你傻么 再输入一次 _(:з」∠)"
        choice = raw_input()
    print u"输入你的代号"
    username = raw_input()
    print u"输入你的暗号"
    password = raw_input()
    print u"登陆中_(:з」∠)"
    px.login(username, password)
    print u"\033[1;35;40m(*ˉ﹃ˉ)\n提醒：如果中途崩溃了 说明你电脑抽了\033[0m"
    px.cookie_Login()
    if px.opener == None:
        print u"好像你电脑抽了(´_ゝ`)"
    else:
        print u"正在抽风（⊙.⊙）"
        px.choice_Select(choice)

if __name__ == '__main__':
    main()
