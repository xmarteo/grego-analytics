from django.shortcuts import render
from django.http import HttpResponse
from analytics.models import *
from analytics.grego_utils import *

def index(request):
  return HttpResponse(open("analytics.html").read())

def query(request, query):
    q = query_from_str(query)
    chants = execute_query(q)
    out = ""
    for c in chants:
        out += '<a href="https://gregobase.selapa.net/chant.php?id={}">{}</a>, '.format(c.id, c.id)
    return HttpResponse(out)
