import urllib.request
import re
import json
import datetime
from flask import Flask, request, jsonify
 
 
def readContentUrl(url):
    userAgent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36'
    header = {'User-Agent': userAgent}
    
    req = urllib.request.Request(url, data=None, headers=header)
    with urllib.request.urlopen(req) as response:
        thePage = response.read()
    return thePage.decode("utf-8")
 
def regexSearchGroup(regex, data):
    matches = re.finditer(regex, data, re.MULTILINE)
 
    listData = []
    for matchNum, match in enumerate(matches, start=1):
        #print ("Match {matchNum} was found at {start}-{end}: {match}".format(matchNum = matchNum, start = match.start(), end = match.end(), match = match.group()))
        
        for groupNum in range(0, len(match.groups())):
            groupNum = groupNum + 1
            listData.append(data[match.start(groupNum) : match.end(groupNum)])
            #print ("Group {groupNum} found at {start}-{end}: {group}".format(groupNum = groupNum, start = match.start(groupNum), end = match.end(groupNum), group = match.group(groupNum)))
 
    return listData
   
def regexSearch(regex, data):
   matchs = re.search(regex, data)
   if matchs: 
      result = data[matchs.start(1): matchs.end(1)]
   else: 
      result = None
   return result

# if userInfor:True then craw id, username, follow, followed by
def crawInformation(url, userInfor, post):
    url = url + "feed/"
    strData = readContentUrl(url)
    strData = re.sub(r"\"config\"(.*?)entry_data", "123456789", strData)
    strData = re.sub(r"\"edge_sidecar_to_children\"(.*?)}}},", "deleteData", strData)
    regexPost = r"\"node\":{\"(__typename.*?)\bedge_media_preview_like\b"
    strPosts = regexSearchGroup(regexPost, strData)

    result = {}
    if userInfor == True: 
        user = {}
        regexUserId = r"\"id\":\"(.*?)\""
        user['userId'] = regexSearchGroup(regexUserId, strData)[0]
        regexEdgeFollow = r"\"edge_follow\":{\"count\":(.*?)},"
        user['edgeFollow'] = regexSearch(regexEdgeFollow, strData)
        regexEdgeFollowedBy = r"\"edge_followed_by\":{\"count\":(.*?)},"
        user['edgeFollowedBy'] = regexSearch(regexEdgeFollowedBy, strData)
        regexUserName =  r"username\":\"(.*?)\"," 
        user['username'] = regexSearchGroup(regexUserName, strData)[0]
        result['user'] = user
        
    if post ==True:
        listPost = []
        for strPost in strPosts:
            post = {}
            regexTypeName = r"typename\":\"(.*?)\","
            post['typeName'] = regexSearch(regexTypeName, strPost)
        
            regexPostId = r"\"id\":\"(.*?)\","
            post['id'] = regexSearch(regexPostId, strPost)
        
            regexShortCode = r"\"shortcode\":\"(.*?)\","
            post['shortCode'] = regexSearch(regexShortCode, strPost)
        
            regexVideoViewCount = r"video_view_count\":(.*?),"
            post['videoViewCount'] = regexSearch(regexVideoViewCount, strPost)
        
            regexCommentCount = r"edge_media_to_comment\":{\"count\":(.*?)},"
            post['commentCount'] = regexSearch(regexCommentCount, strPost)

            regexTakenTimeStamp = r"taken_at_timestamp\":(.*?),"
            timeInteger = regexSearch(regexTakenTimeStamp, strPost)
            post['takenTimeStamp'] = datetime.datetime.fromtimestamp(int(timeInteger)).strftime('%Y-%m-%d %H:%M:%S')

            regexCountLike = r"edge_liked_by\":{\"count\":(.*?)},"
            post['countLike'] = regexSearch(regexCountLike, strPost)

            regexTitle = r"edge_media_to_caption\":{\"edges\":\[{\"node\":{\"text\":\"(.*?)\"}}\]"
            post['title'] = regexSearch(regexTitle, strPost)

            listPost.append(post)
    
        result['post'] = listPost
    return result

url = "https://www.instagram.com/sontungmtp/"
url1 = "https://www.instagram.com/wonhari/"
result = crawInformation(url1, True, True)
app = Flask(__name__)

@app.route('/', methods = ['GET'])
def getListPostUser():
   response = jsonify({
      'result' : result
   })
   response.headers.add('Access-Control-Allow-Origin', '*')
   return response

if __name__ == "__main__":
   app.run()
 
 
 

