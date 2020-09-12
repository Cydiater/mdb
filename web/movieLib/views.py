import logging
import time

from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.views import generic
from django.urls import reverse

from .models import Movie, Actor, Comment

logging.basicConfig(level=logging.DEBUG)

class IndexView(generic.ListView):
    model = Movie
    template_name = 'movieLib/index.html'
    paginate_by = 20
    ordering = ['-rating']

class ActorIndexView(generic.ListView):
    model = Actor
    template_name = 'movieLib/actorIndex.html'
    paginate_by = 20


class MovieView(generic.DetailView):
    model = Movie
    template_name = 'movieLib/movie.html'

class ActorView(generic.DetailView):
    model = Actor
    template_name = 'movieLib/actor.html'

    def getAdjacencyActors(self):
        bucket = dict()
        movies = Actor.objects.get(pk=self.kwargs.get('pk')).movie_set.all()
        for movie in movies:
            for actor in movie.actors.all() :
                if actor.id != self.kwargs.get('pk'):
                    if not actor.id in bucket:
                        bucket[actor.id] = 0
                    bucket[actor.id] += 1
        adjs = sorted(bucket.items(), key=lambda x: -x[1])[:10]
        for i, adj in enumerate(adjs):
            adjs[i] = (Actor.objects.get(pk=adj[0]), adj[1])
        return adjs

    def get_context_data(self, **kwargs):
        context = super(ActorView, self).get_context_data(**kwargs)
        context["adjacencyActors"] = self.getAdjacencyActors()
        return context

class SearchMovieView(generic.ListView):
    template_name = 'movieLib/search_movies_results.html'
    paginate_by = 20

    def get_context_data(self, **kwargs):
        context = super(SearchMovieView, self).get_context_data(**kwargs)
        context['elapsed_time'] = self.elapsed_time
        context['res_size'] = self.res_size
        return context

    def get_queryset(self):
        time_st = time.time()
        keyword = self.kwargs.get('keyword')
        p1 = Movie.objects.filter(name__contains=keyword)
        p2 = Movie.objects.filter(actors__name__contains=keyword)
        res = (p1 | p2).distinct()
        time_ed = time.time()
        self.elapsed_time = time_ed - time_st
        self.res_size = len(res)
        return res

class SearchActorView(generic.ListView):
    template_name = 'movieLib/search_actors_results.html'
    paginate_by = 20

    def get_context_data(self, **kwargs):
        context = super(SearchActorView, self).get_context_data(**kwargs)
        context['elapsed_time'] = self.elapsed_time
        context['res_size'] = self.res_size
        return context

    def get_queryset(self):
        time_st = time.time()
        keyword = self.kwargs.get('keyword')
        keyword = self.kwargs.get('keyword')
        p1 = Actor.objects.filter(name__contains=keyword)
        p2 = Actor.objects.filter(movie__name__contains=keyword)
        res = (p1 | p2).distinct()
        time_ed = time.time()
        self.elapsed_time = time_ed - time_st
        self.res_size = len(res)
        return res

class SearchCommentView(generic.ListView):
    template_name = 'movieLib/search_comments_results.html'
    paginate_by = 20

    def get_context_data(self, **kwargs):
        context = super(SearchCommentView, self).get_context_data(**kwargs)
        context['elapsed_time'] = self.elapsed_time
        context['res_size'] = self.res_size
        return context

    def get_queryset(self):
        time_st = time.time()
        keyword = self.kwargs.get('keyword')
        queryset = Comment.objects.filter(content__contains=keyword)
        time_ed = time.time()
        self.elapsed_time = time_ed - time_st
        self.res_size = len(queryset)
        return queryset

def searchRouter(request):
    keyword = request.GET["search"]
    category = request.GET["category"]

    if category == "movie":
        return HttpResponseRedirect(reverse('movieLib:searchMovie', args=(keyword,)))

    if category == "actor":
        return HttpResponseRedirect(reverse('movieLib:searchActor', args=(keyword,)))

    if category == "comment":
        return HttpResponseRedirect(reverse('movieLib:searchComment', args=(keyword,)))
