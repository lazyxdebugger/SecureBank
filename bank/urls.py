from django.urls import path

from .views import (
    homePageView,
    loginView,
    dashboardView,
    logoutView,
    transferView,
    confirmView,
    searchTransactionsView,
    accountView
)


urlpatterns = [
    path('', homePageView, name='home'),
    path('login/', loginView, name='login'),
    path('dashboard/', dashboardView, name='dashboard'),
    path('logout/', logoutView, name='logout'),
    path('transfer/', transferView, name='transfer'),
    path('confirm/', confirmView, name='confirm'),
    path('search/', searchTransactionsView, name='search'),
    path('account/', accountView, name='account'),
]