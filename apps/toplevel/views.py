from django.template import loader, Context
from django.http import HttpResponse

def homepage(request):
    t = loader.get_template("toplevel/homepage.html")
    c = Context({})
    return HttpResponse(t.render(c))

