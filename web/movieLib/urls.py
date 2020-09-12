from django.urls import path

from . import views

app_name = 'movieLib'

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('<int:pk>', views.MovieView.as_view(), name='movie'),
    path('actors/', views.ActorIndexView.as_view(), name='actorIndex'),
    path('actor/<int:pk>', views.ActorView.as_view(), name='actor'),
    path('search', views.searchRouter, name='search'),
    path('search/movie/<str:keyword>', views.SearchMovieView.as_view(), name='searchMovie'),
    path('search/actor/<str:keyword>', views.SearchActorView.as_view(), name='searchActor'),
    path('search/comment/<str:keyword>', views.SearchCommentView.as_view(), name='searchComment'),
]
