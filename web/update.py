import logging
import json
import os
import re
import html

logging.basicConfig(level=logging.DEBUG)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "web.settings")
import django
django.setup()

from movieLib.models import Movie, Actor, Comment

def parseIDfromURL(url):
    regex = re.compile(r'/celebrity/(\d+)/')
    results = regex.findall(url)
    assert len(results) == 1
    return results[0];

if __name__ == '__main__':

    Actor.objects.all().delete()
    Movie.objects.all().delete()

    cnt = 0
    with open('actors.json', 'r') as f:
        actors = json.load(f)
        for actor in actors:
            aid = int(actor["id"])
            ImagePath = f'/static/image/actor/{aid}.jpg'
            if not os.path.exists('movieLib' + ImagePath):
                ImagePath = '/static/image/404/actor.png'
            a = Actor.objects.create(id=aid,
                                     name=html.unescape(actor["name"]),
                                     gender=html.unescape(actor["gender"]),
                                     birthday=actor["birthday"],
                                     birthplace=actor["birthplace"],
                                     constellation=actor["constellation"],
                                     profession=actor["profession"],
                                     description=actor["description"].replace('<br />', '\n').strip().replace(' ', ''),
                                     imagePath=ImagePath)
            cnt += 1
            logging.info(f'actor cnt = {cnt} actor = {a}')

    cnt = 0
    with open('movies.json', 'r') as f:
        movies = json.load(f)
        for movie in movies:
            mid = int(movie["id"])
            ImagePath = f'/static/image/movie/{mid}.jpg'
            if not os.path.exists('movieLib' + ImagePath):
                ImagePath = '/static/image/404/movie.jpg'
            m = Movie.objects.create(id=mid,
                                     name=html.unescape(movie["name"]),
                                     rating=movie["rating"],
                                     description=movie["description"].replace('<br />', '\n').strip().replace(' ', ''),
                                     genre='/'.join(movie["genre"]),
                                     imagePath=ImagePath)
            for comment in movie["comments"]:
                Comment.objects.create(content=comment.replace('<span property="v:summary">', ''), movie=m)
            for actor in movie["actors"]:
                try:
                    aid = int(parseIDfromURL(actor["url"]))
                    a = Actor.objects.get(pk=aid)
                    m.actors.add(a)
                except Exception as e:
                    m.delete();
                    logging.error(str(e))
                    break;
            cnt += 1
            logging.info(f'movie cnt = {cnt} movie = {m}')
