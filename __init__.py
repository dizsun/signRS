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


def signRS():
    # 对密码进行md5加密
    pwd = '你的密码'
    md5 = hashlib.md5()
    md5.update(pwd)
    pwdmd5 = md5.hexdigest()

    filename = 'cookie.txt'
    # 声明一个MozillaCookieJar对象实例来保存cookie，之后写入文件
    cookie = cookielib.MozillaCookieJar(filename)
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookie))
    postdata = urllib.urlencode({
        'username': '你的账号',
        'password': pwdmd5,
        'quickforward': 'yes',
        'handlekey': 'ls'
    })
    # 登录睿思的URL
    loginUrl = 'http://rs.xidian.edu.cn/member.php?mod=logging&action=login&loginsubmit=yes&infloat=yes&lssubmit=yes&inajax=1'
    # 模拟登录，并把cookie保存到变量
    result = opener.open(loginUrl, postdata)
    # 保存cookie到cookie.txt中
    cookie.save(ignore_discard=True, ignore_expires=True)

    signurl = 'http://rs.xidian.edu.cn/plugin.php?id=dsu_paulsign:sign'
    # signurl = 'http://rs.xidian.edu.cn/portal.php'
    result = opener.open(signurl)
    page = result.read()
    formhash = ''
    m = re.findall(
        r'<span class="pipe">\|</span><a href="member\.php\?mod=logging&amp;action=logout&amp;formhash=(.*?)">', page,
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
    result = opener.open(signmodeurl, data1)
    # 请求访问签到后的网址
    signurl = 'http://rs.xidian.edu.cn/plugin.php?id=dsu_paulsign:sign'
    result = opener.open(signurl)
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


def writelog(mode):
    fp = open("rslog.txt", 'a')
    if mode == 1:
        fp.write(time.strftime("%H:%M", time.localtime()) + "\n")
    else:
        fp.write("success!\n")
    fp.close()


hassign = False

while True:
    if "07:00" == time.strftime("%H:%M", time.localtime()) and not hassign:
        if signRS():
            print "success"
            writelog(2)
            hassign = True
        else:
            send_email(u"睿思签到失败!")
    else:
        hassign = False
        writelog(1)
        print time.strftime("%H:%M", time.localtime())
        time.sleep(0.01)
