from django.shortcuts import render, redirect
from starlight.settings import MAIN_SITE_URL

def index(request):
    return redirect('/prelaunch/')
    # todo when prelaunch ends return redirect(MAIN_SITE_URL)
