# coding=UTF-8
# 爬取睿思
#
import urllib
import urllib2
import re
import sys
import cookielib
import hashlib
import send_email
import time

reload(sys)
sys.setdefaultencoding('utf8')


class RSManager(object):
    # 用户名
    _username = ''
    # 明文密码
    _password = ''
    # MD5加密密码
    _md5pwd = ''
    # 是否已登录成功
    _isLogin = False
    # cookie文件名称
    _cookieFile = 'cookie2.txt'
    _opener = None

    def __init__(self, username, password):
        if username and password:
            self._username = username
            self._password = password
            md5 = hashlib.md5()
            md5.update(self._password)
            self._md5pwd = md5.hexdigest()

    def loginRS(self):
        # 声明一个MozillaCookieJar对象实例来保存cookie，之后写入文件
        cookie = cookielib.MozillaCookieJar(self._cookieFile)
        self._opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookie))
        postdata = urllib.urlencode({
            'username': self._username,
            'password': self._md5pwd,
            'quickforward': 'yes',
            'handlekey': 'ls'
        })
        # 登录睿思的URL
        loginUrl = 'http://rs.xidian.edu.cn/member.php?mod=logging&action=login&loginsubmit=yes&infloat=yes&lssubmit=yes&inajax=1'
        # 模拟登录，并把cookie保存到变量
        result = self._opener.open(loginUrl, postdata)
        # 保存cookie到cookie.txt中
        cookie.save(ignore_discard=True, ignore_expires=True)
        if result:
            self._isLogin = True
        return False

    def signRS(self):
        if not self._isLogin:
            return False
        signurl = 'http://rs.xidian.edu.cn/plugin.php?id=dsu_paulsign:sign'
        result = self._opener.open(signurl)
        page = result.read()
        formhash = ''
        m = re.findall(
            r'<span class="pipe">\|</span><a href="member\.php\?mod=logging&amp;action=logout&amp;formhash=(.*?)">',
            page,
            re.S)
        if m:
            formhash = m[0]
        else:
            print "formhash getting error!"
            return False
        # 利用cookie请求访问另一个网址，此网址是签到网址
        signmodeurl = 'http://rs.xidian.edu.cn/plugin.php?id=dsu_paulsign:sign&operation=qiandao&infloat=1&inajax=1'
        data1 = urllib.urlencode({
            'formhash': formhash,
            'qdxq': 'kx',
            'qdmode': '3',
            'todaysay': '',
            'fastreplay': '0'
        })
        # 请求访问签到网址
        result = self._opener.open(signmodeurl, data1)
        # 请求访问签到后的网址
        signurl = 'http://rs.xidian.edu.cn/plugin.php?id=dsu_paulsign:sign'
        result = self._opener.open(signurl)
        page = result.read()
        m = re.findall(r'您今天已经签到过了或者签到时间还未开始', page, re.S)
        if m:
            if m[0] == u'您今天已经签到过了或者签到时间还未开始':
                print u"签到成功!"
                return True
            else:
                print u"签到失败!"
                return False
        else:
            print u"签到失败!"
            return False

    def search(self):
        if not self._isLogin:
            return False
        keyWord = u'爱宠大机密'
        searchUrl = 'http://rs.xidian.edu.cn/bt.php?w=%s&c=&t=all' % (keyWord.encode())
        result = self._opener.open(searchUrl)
        page = result.read()
        m = re.findall(r'试种资源，正在审核中\.\.\.', page, re.S)
        ans = m[0]
        if ans.decode() == u'试种资源，正在审核中...':
            return False
        else:
            return True

    def get_isLogin(self):
        return self._isLogin


if __name__ == '__main__':
    manager = RSManager('***', '***')
    manager.loginRS()
    while True:
        if not manager.get_isLogin():
            manager.loginRS()
        if manager.search():
            send_email.send_qq_email(u'爱宠大机密可以下载!')
            break
        time.sleep(60 * 10)
