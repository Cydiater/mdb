import logging
import urllib.request
import urllib.parse
import time
import json
import re
import os
import html as HTML

logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')

classMovieCnt = 300
singleFetchCnt = 20
sleepTimeS = 1
timeoutS = 5

fetchIDBaseURL = "https://movie.douban.com/j/search_subjects"
fetchType = "movie"
moviePageLimit = 20
movieCalsses = ["科幻", "爱情", "文艺", "华语", "动作"]

fetchMovieBaseURL = "https://movie.douban.com/subject/{}/"
fetchActorBaseURL = "https://movie.douban.com"

allMovieJsonFilepath = "./movies.json"
allActorJsonFilepath = "./actors.json"

actorSet = set()

pageIDQueue = []
movieIDQueue = []

movieInfoQueue = []
movieImageQueue = []

actorInfoQueue = []
actorImageQueue = []

def getRandomHeaders():
    return {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.83 Safari/537.36"
    }

def getMovieURL(id):
    return fetchMovieBaseURL.format(id)

def parseInfo(html):
    regex = re.compile(r'<script type=\"application/ld\+json\">(.*?)</script>', re.DOTALL)
    results = regex.findall(html)
    assert len(results) == 1
    try:
        text = results[0].replace('\n', '').replace('\r', '').replace('\t', '')
        return json.loads(text)
    except Exception as e:
        logging.warning(f'error = {str(e)} text = {text}')
        raise e

def parseActorDescription(html):
    regex = re.compile(r'<span class="all hidden">(.*?)</span>', re.DOTALL)
    results = regex.findall(html)
    if len(results) == 0:
        regex = re.compile(r'<div id="intro" class="mod">(.*?)<div class="bd">(.*?)</div>', re.DOTALL)
        results = regex.search(html)
        if results == None:
            return "unknown"
        return results.group(2).strip().replace('<br>', '\n').replace('<br/>', '\n')
    return results[0].strip().replace('<br>', '\n').replace('<br/>', '\n')

def parseMovieDescription(html):
    regex = re.compile(r'<span property="v:summary"(.*?)>(.*?)</span>', re.DOTALL)
    results = regex.search(html)
    return results.group(2).strip().replace('<br>', '\n').replace('<br/>', '\n')

def getMovieComments(html):
    regex = re.compile(r'<span class="short">(.*?)</span>', re.DOTALL)
    results = regex.findall(html)
    for i, result in enumerate(results):
        results[i] = HTML.unescape(result)
    return results[:5];

def isNormalPage(html):
    if not "<title>" in html:
        return False
    title = str(html).split('<title>')[1].split('</title>')[0]
    return "(豆瓣)" in title

def getMovieInfo(url):
    info = {}
    try:
        req = urllib.request.Request(url, headers=getRandomHeaders())
        with urllib.request.urlopen(req, timeout=timeoutS) as response:
            html = response.read().decode('utf-8')
            if not isNormalPage(html):
                logging.warning(f'html = {html}')
                raise RuntimeError("get douban login page")
            infoJson = parseInfo(html)
            info["name"] = HTML.unescape(infoJson["name"])
            info["description"] = HTML.unescape(parseMovieDescription(html))
            info["rating"] = infoJson["aggregateRating"]["ratingValue"]
            info["genre"] = HTML.unescape(infoJson["genre"])
            actors = infoJson["actor"]
            for i, actor in enumerate(actors):
                actors[i] = HTML.unescape(actor)
            info["actors"] = actors[:10];
            info["comments"] = getMovieComments(html)
            info["imageURL"] = infoJson["image"]
            return info;
    except Exception as e:
        logging.warning(f'error = {str(e)} info = {json.dumps(info)}')
        raise RuntimeError("get movie error")

def getMovieIDList(pageID, pageTag):
    getMovieIDQuery = {
        "type": fetchType,
        "tag": pageTag,
        "page_limit": moviePageLimit,
        "page_start": pageID
    }
    url = fetchIDBaseURL + '?' + urllib.parse.urlencode(getMovieIDQuery)
    logging.info(f'fetch id url = {url}')
    ids = []
    req = urllib.request.Request(url, headers=getRandomHeaders())
    try:
        with urllib.request.urlopen(req, timeout=timeoutS) as response:
            text = response.read()
            IDsJson = json.loads(text)["subjects"]
            for IDJson in IDsJson:
                ids.append( IDJson['id'] )
            return ids
    except Exception as e:
        logging.warning(str(e))
        raise RuntimeError('network error')

def downloadImage(url, filepath):
    logging.info(f'downloading url = {url} filepath = {filepath}')
    try:
        urllib.request.urlretrieve(url, filename=filepath)
    except:
        raise RuntimeError('network error')

def parseIDfromURL(url):
    regex = re.compile(r'/celebrity/(\d+)/')
    results = regex.findall(url)
    assert len(results) == 1
    return results[0];

def parseGender(html):
    regex = re.compile(r'<span>性别</span>:(.*?)</li>', re.UNICODE | re.DOTALL)
    results = regex.findall(html)
    if len(results) == 0:
        return 'unknown'
    return HTML.unescape(results[0].strip())

def parseConstellation(html):
    regex = re.compile(r'<span>星座</span>:(.*?)</li>', re.UNICODE | re.DOTALL)
    results = regex.findall(html)
    if len(results) == 0:
        return 'unknown'
    return HTML.unescape(results[0].strip())

def parseBirthday(html):
    regex = re.compile(r'<span>出生日期</span>:(.*?)</li>', re.UNICODE | re.DOTALL)
    results = regex.findall(html)
    if len(results) == 0:
        return 'unknown'
    return HTML.unescape(results[0].strip())

def parseBirthplace(html):
    regex = re.compile(r'<span>出生地</span>:(.*?)</li>', re.UNICODE | re.DOTALL)
    results = regex.findall(html)
    if len(results) == 0:
        return 'unknown'
    return HTML.unescape(results[0].strip())

def parseProfession(html):
    regex = re.compile(r'<span>职业</span>:(.*?)</li>', re.UNICODE | re.DOTALL)
    results = regex.findall(html)
    if len(results) == 0:
        return 'unknown'
    return HTML.unescape(results[0].strip())

def parseImageURL(html):
    regex = re.compile(r'"点击看大图"[\s\n\t]*src="(.*?)">', re.UNICODE | re.DOTALL)
    results = regex.findall(html)
    if len(results) == 0:
        return 'unknown'
    return HTML.unescape(results[0].strip())

def getActorInfo(url):
    logging.info(f'url = {url}')
    info = {}
    try:
        req = urllib.request.Request(url, headers=getRandomHeaders())
        with urllib.request.urlopen(req, timeout=timeoutS) as response:
            html = response.read().decode('utf-8')
            if not isNormalPage(html):
                raise RuntimeError("get douban login page")
            info["gender"] = parseGender(html)
            info["constellation"] = parseConstellation(html)
            info["birthday"] = parseBirthday(html)
            info["birthplace"] = parseBirthplace(html)
            info["profession"] = parseProfession(html)
            info["imageURL"] = parseImageURL(html)
            info["description"] = parseActorDescription(html)
            return info
    except Exception as e:
        logging.warning(f'error = {str(e)}')
        raise RuntimeError("get actor info error")

if __name__ == '__main__':

    movies = []
    actors = []

    for i in range(0, classMovieCnt, singleFetchCnt):
        for tag in movieCalsses:
            pageIDQueue.append({"id": i, "tag": tag})

    while len(pageIDQueue) > 0:
        pageID = pageIDQueue.pop();
        try:
            movieIDs = getMovieIDList(pageID["id"], pageID["tag"])
            movieIDQueue.extend(movieIDs)
            logging.info(f'fetch page {movieIDs}')
        except RuntimeError as e:
            logging.warning(f'fetch page {pageID} failed')
            pageIDQueue.insert(0, pageID)

    movieIDQueue = list(set(movieIDQueue))

    curMovieCnt = 1
    while len(movieIDQueue) > 0:
        id = movieIDQueue.pop();
        logging.info(f'current id = {id} cnt = {curMovieCnt}')
        url = getMovieURL(id)
        logging.info(f'url = {url}')
        try:
            time.sleep(sleepTimeS)
            info = getMovieInfo(url)
            curMovieCnt = curMovieCnt + 1;
        except RuntimeError as e:
            movieIDQueue.insert(0, id)
            logging.warning(f'get movie info error id = {id}')
            continue
        info["id"] = str(id)
        movies.append(info)
        logging.info(f'info = {json.dumps(info, ensure_ascii=False)}')
        for actor in info["actors"]:
            actorSet.add(json.dumps(actor, ensure_ascii=False))
        logging.info(f'size of actorSet = {len(actorSet)}')

        movieImageQueue.append({
            "url": info["imageURL"],
            "path": f"../image/movie/{id}.jpg"
        })

    with open(allMovieJsonFilepath, 'w') as f:
        json.dump(movies, f, ensure_ascii=False)

    curMovieCnt = 1
    while len(movieImageQueue) > 0:
        movieImage = movieImageQueue.pop()
        logging.info(f'curMovieCnt = {curMovieCnt}')
        try:
            downloadImage(movieImage["url"], movieImage["path"])
            curMovieCnt = curMovieCnt + 1
        except RuntimeError as e:
            movieImageQueue.insert(0, movieImage)
            logging.warning(f'get movie image error image = {movieImage}')
            continue

    actorInfoQueue = list(actorSet)

    curActorCnt = 1
    while len(actorInfoQueue) > 0:
        actorJson = actorInfoQueue.pop()
        try:
            url = json.loads(actorJson)["url"]
        except:
            logging.info(f'actorJson = {actorJson}')
        id = parseIDfromURL(url)
        logging.info(f'id = {id} curActorCnt = {curActorCnt}')
        try:
            time.sleep(sleepTimeS)
            actor = getActorInfo(fetchActorBaseURL + url)
            curActorCnt = curActorCnt + 1
        except RuntimeError as e:
            actorInfoQueue.insert(0, actorJson)
            logging.warning(f'get actor info error actor = {actorJson}')
            continue

        actor["name"] = HTML.unescape(json.loads(actorJson)["name"].strip())
        actor["id"] = str(id)
        logging.info(f'actor json = {json.dumps(actor, ensure_ascii=False)}')
        time.sleep(sleepTimeS)
        actors.append(actor)

        if actor["imageURL"] != 'unknown':
            actorImageQueue.append({
                "url": actor["imageURL"],
                "path": f"../image/actor/{id}.jpg"
            })

    curActorCnt = 1
    while len(actorImageQueue) > 0:
        actorImage = actorImageQueue.pop()
        logging.info(f'curActorCnt = {curActorCnt}')
        try:
            downloadImage(actorImage["url"], actorImage["path"])
            curActorCnt = curActorCnt + 1
        except RuntimeError as e:
            actorImageQueue.insert(0, actorImage)
            logging.warning(f'get actor image error image = {actorImage}')
            continue

    with open(allActorJsonFilepath, 'w') as f:
        json.dump(actors, f, ensure_ascii=False)
