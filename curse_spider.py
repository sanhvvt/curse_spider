#!/usr/bin/env python
#encoding=utf8
from __future__ import print_function
from __future__ import division
import sys
import os
import re
import zipfile
import shutil
import json

_ver = sys.version_info
is_py2 = (_ver[0] == 2)
is_py3 = (_ver[0] == 3)
is_request = False
is_urllib2 = False

try:
    import requests
    is_request = True
except:
    import urllib2
    is_urllib2 = True

_nTimeOut = 30
_sMozilla = 'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6'

class MyResponse:
    headers = None
    content = None
    def __init__(self, headers, content):
        self.headers = headers
        self.content = content

def getOSName():
    sName = ''
    if os.name == 'nt':
        sName = 'Windows'
    else:
        sName = 'Mac'
    print('[Check OS]: {}'.format(sName))
    print('[Check PY]: {}'.format(sys.version))
    return sName

def checkDir(sPath):
    return os.path.isdir(sPath)

def chunk_report(bytes_so_far, chunk_size, total_size):
    percent = float(bytes_so_far) / total_size
    percent = round(percent*100, 2)
    done = int(50 * bytes_so_far / total_size)
    sys.stdout.write("\r[%s%s] (%0.2f%%)" % ('*' * done, ' ' * (50 - done), percent))
    sys.stdout.flush()
    if bytes_so_far >= total_size:
        sys.stdout.write('\n')  

def downloadFileByRequest(sUrl, sDownlaodPath, chunk_size=8192):
    response = requests.get(sUrl, timeout=_nTimeOut, stream=True)
    total_size = response.headers['Content-Length']
    total_size = int(total_size)
    bytes_so_far = 0
    with open(sDownlaodPath, 'wb') as code:
        for chunk in response.iter_content(chunk_size=chunk_size):
            if not chunk:
                break
            code.write(chunk)
            bytes_so_far += len(chunk)
            chunk_report(bytes_so_far, chunk_size, total_size)
    return bytes_so_far

def getUnRedirectUrlByRequest(sUrl):
    response = requests.get(sUrl, timeout=_nTimeOut, stream=True, allow_redirects=False)
    response.raise_for_status()
    return response

def downloadFileByUrllib(sUrl, sDownlaodPath, chunk_size=8192):
    response = urllib2.urlopen(sUrl, timeout=_nTimeOut)
    total_size = response.headers['Content-Length']
    total_size = int(total_size)
    bytes_so_far = 0
    with open(sDownlaodPath, 'wb') as code:
        while 1:
            chunk = response.read(chunk_size)
            if not chunk:
                break
            code.write(chunk)
            bytes_so_far += len(chunk)
            chunk_report(bytes_so_far, chunk_size, total_size)
    return bytes_so_far

def getUnRedirectUrlByUrllib(sUrl):
    class MyRedirectHandler(urllib2.HTTPRedirectHandler):
        def http_error_302(self, req, fp, code, msg, headers):
            return 
        http_error_301 = http_error_303 = http_error_307 = http_error_302

    print(sUrl)
    req = urllib2.Request(sUrl)
    debug_handler = urllib2.HTTPHandler(debuglevel = 1)
    opener = urllib2.build_opener(debug_handler, MyRedirectHandler)
    opener.addheaders = [('User-agent', _sMozilla)]

    response = None
    page = None
    headers = None
 
    try:
        response = opener.open(sUrl, timeout=_nTimeOut)
        page = response.read()
        headers = response.headers
    except urllib2.URLError as e:
        if e.code in (300, 301, 302, 303, 307):
            headers = e.headers
        else:
            raise Exception('[URL Error]', e.code, e.reason)
    finally:
        if response:
            response.close()
 
    data = MyResponse(headers, page)
    return data

def extractZip(sZip, sExtPath, filterDir=[]):
    def isFileter(key, filters):
        for e in filters:
            if e == key:
                return True
        return False

    objZip = zipfile.ZipFile(sZip, 'r')
    objInfos = objZip.infolist()
    nLen = len(objInfos)
    nIndex = 0
    for member in objInfos:
        if isFileter(member.filename, filterDir):
            continue
        nIndex += 1
        objZip.extract(member, sExtPath)
        chunk_report(nIndex, 0, nLen)
        # print("Extracting file", member.filename)

#============================================================================
#API已过期

# def checkCurseAPI(sUrl):
#     if sUrl.startswith('https://www.curseforge.com/wow/addons/'):
#         resp = None
#         if is_request:
#             resp = getUnRedirectUrlByRequest(sUrl)
#         elif is_urllib2:
#             resp = getUnRedirectUrlByUrllib(sUrl)
#         sContent = str(resp.content)

#         # API示例: click <a href="/wow/addons/details/download/2743849/file">here
#         pattern = re.compile('click\s?<a href="(\S+)">\s?here') 
#         match = pattern.search(sContent)
#         if not match:
#             print(sContent)
#             raise Exception("Can't find API!")
#         sMatch = match.group(0)
#         sApi = match.group(1)

#         sApiUrl = 'https://www.curseforge.com' + sApi
#         print('==> ' + sApiUrl)
#         return sApiUrl
#     elif sUrl.startswith('https://wow.curseforge.com/projects/'):
#         return sUrl
#     else:
#         raise Exception("Invalid URL!", sUrl)

# def getAddonsUrl(sUrl):
#     sApiUrl = checkCurseAPI(sUrl)
#     resp = None
#     if is_request:
#         resp = getUnRedirectUrlByRequest(sApiUrl)
#     elif is_urllib2:
#         resp = getUnRedirectUrlByUrllib(sApiUrl)
#     sFileUrl = resp.headers['Location']
#     print('==> ' + sFileUrl)
#     return sFileUrl 

#============================================================================

def getZipName(sUrl): 
    # API示例: https://edge.forgecdn.net/files/2747/1/AngryKeystones-v0.18.0.zip
    pattern = re.compile('/(\d+)/(\d+)/([\S ]+.zip)')
    match = pattern.search(sUrl)
    if not match:
        raise Exception("Not find FILE!", sUrl)
    sMatch = match.group(0)
    sMajor = match.group(1)
    sMinor = match.group(2)
    sAddons = match.group(3)
    print('==> [{}]: {}.{}'.format(sAddons, sMajor, sMinor))    
    return sAddons

def checkLocalAddons(sAddons):
    bFile = os.path.isfile(sAddons)
    print('[Check]: {}, {}'.format(bFile, sAddons))
    return bFile

def downloadAddons(sUrl, sAddons):
    if sAddons.find('.zip') < 0:
        raise Exception("DownLoad Invalid ZIP!", sAddons)
    print('[Download]: {}'.format(sAddons))
    if is_request:
        downloadFileByRequest(sUrl, sAddons)
    elif is_urllib2:
        downloadFileByUrllib(sUrl, sAddons)

def installAddons(sZip, sInstallPath):
    if sZip.find('.zip') < 0:
        raise Exception("Extract Invalid ZIP!", sZip)
    filterDir = ['Interface/', 'Interface/AddOns/', 'Interface/readme.txt']
    print('[Install]: {}'.format(sInstallPath))
    extractZip(sZip, sInstallPath, filterDir)

def loadAddonsJson(sConfig):
    if os.path.exists(sConfig) == False:
        return None

    if is_py2:
        with open(sConfig, 'r') as f:
            contents = f.read().decode("UTF-8")
    elif is_py3:
        with open(sConfig, 'r', encoding='UTF-8') as f:
            contents = f.read()

    data = json.loads(contents)
    return data

# def searchAddons():
#     sFlavor = 'wow_retail'
#     sUrl ='https://addons-ecs.forgesvc.net/api/v2/addon/search?categoryId=0&gameId=1&gameVersionFlavor={}'.format(sFlavor)
#     response = urllib2.urlopen(sUrl, timeout=_nTimeOut)
#     contents = response.read().decode('UTF-8')
#     data = json.loads(contents)

def loadAddonsInfo(addonID):
    sUrl = 'https://addons-ecs.forgesvc.net/api/v2/addon/{}'.format(addonID)
    contents = ''
    if is_py2:
        response = urllib2.urlopen(sUrl, timeout=_nTimeOut)
        contents = response.read().decode('UTF-8')
    elif is_py3:
        headers = {'user-agent': _sMozilla}
        response = requests.get(sUrl, headers=headers, timeout=_nTimeOut)
        contents = response.text

    data = json.loads(contents)

    downloadurl = ''
    for obj in data['latestFiles']:
        if obj['gameVersionFlavor'] == 'wow_retail' and obj['releaseType'] == 1:
            downloadurl = obj['downloadUrl']
            break
    return downloadurl

# def testAddonsID():
#     addonsDict = {
#         "details": 61284,
#         "deadly-boss-mods": 3358,
#         "weakauras-2": 65387,
#         "bagnon": 1592,
#         "method-dungeon-tools": 288981,
#         "angry-keystones": 102522,
#         "championcommander": 300882,
#         "lunataotao": 301866,
#         "tullarange": 26753,
#         "pawn": 4646,
#         # "mapster": 14376
#     }
#     return addonsDict

def checkAddons(addonsList):
    addonsDict = {}
    if isinstance(addonsList, list):
        for addon in addonsList:
            key = addon['name']
            value = addon['id']
            addonsDict[key] = value
    return addonsDict

if __name__ == "__main__":
    sPlatform = getOSName()
    configs = loadAddonsJson("config.json")
    if configs == None:
        print('[Invalid Config]')
        sys.exit()

    wowPath = configs[sPlatform]['WowPath']
    if checkDir(wowPath) == False:
        print('[Invalid WowPath]: {}'.format(wowPath))
        sys.exit()

    downloadPath = configs[sPlatform]['TempPath']
    if checkDir(downloadPath) == False:
        print('[Invalid DownloadPath]: {}'.format(downloadPath))
        sys.exit()
    
    # addonsList = testAddonsID()
    addonsList = checkAddons(configs['Addons'])

    print('[Addons Count]: {}'.format(len(addonsList)))
    for k, v in addonsList.items():
        sNowAddons = ''
        try:
            print('[Start]: {}: {}'.format(k, v))
            sUrl = loadAddonsInfo(v)
            sAddonPath = '{}/{}'.format(downloadPath, getZipName(sUrl))

            if(not checkLocalAddons(sAddonPath)):
                sNowAddons = sAddonPath
                downloadAddons(sUrl, sAddonPath)
                installAddons(sAddonPath, wowPath)
        except Exception as sError:
            print('\n[Error]??? {}'.format(sError))
            if sNowAddons != '' and os.path.exists(sNowAddons):
                os.remove(sNowAddons)
                print('[Error]remove temp file')
        print('------------------------------------------------')

    print('[install complete]')
    # input("Press Enter!")
