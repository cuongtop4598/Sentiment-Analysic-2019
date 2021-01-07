
from django.shortcuts import render
from django.template import loader
from django.http import HttpResponse,HttpResponseRedirect,JsonResponse
from .forms import SubmitForm,LearnForm
from sentimentAnalysis import STMALS
from django.core.files.storage import FileSystemStorage
from .loadFile import read_file
from research.settings import MEDIA_ROOT
from .models import Submit,Brand,Phone,Comment,Learn
from django.utils import timezone
from Tiki.crawl import Tiki
from .forms import SelectForm,RadioForm
import json
from .updateDB import create_connection,updateBrand,updatePhone


def predict(request):
    fcmt = SubmitForm(request.POST or None)
    fselect = SelectForm(request.POST or None)
    flearn = LearnForm(request.POST or None)
    if request.method == "POST":
        if fcmt.is_valid():
            option = int(request.POST['selectlist'])
            cmt = fcmt.cleaned_data['comment']
            eluavate = STMALS.sentiment_analyse(cmt,option)
            content = { 'fc' : fcmt,
                        'fs':fselect,
                        'data_cmt' : [eluavate,cmt],
                        'fl' : flearn,
                    }
            return render(request,'kaan/predict.html',content)
        if flearn.is_valid():
            flearn.save()
            content = { 'fc' : fcmt,
                        'fs':fselect,
                        'data_cmt' : [0,""],
                        'fl' : flearn,
                    }
            return render(request,'kaan/predict.html',content)
    else :
        data_cmt = [0,""]
        content = { 'fc' : fcmt,
                    'fs':fselect,
                    'data_cmt':data_cmt,
                    'fl' : flearn,
                    }
        return render(request,'kaan/predict.html',content)

def AboutView(request):
    return render(request,"kaan/about.html",{})

def login(request):
    return HttpResponse("login")
    
def register(request):
    return HttpResponse("register")

def viewAnalysis(request):
    brands = Brand.objects.all().order_by("amount")[::-1]
    phones = Phone.objects.all().order_by("sold")[::-1]
    comments = Comment.objects.all()
    brands_label = [brand.trademark for brand in brands]
    brands_amount = [brand.amount for brand in brands]
    total_cmts = [sum([phone.sold for phone in phones if phone.brand_id == brand.id]) for brand in brands]
    return render(request,"kaan/analysis/analysis_Base.html",{"Brands":brands,"Phones": phones,"Comments" : comments,"brands_amount":brands_amount,"total_cmts":total_cmts,"brands_label":brands_label})

def product(request):
    phones = Brand.objects.all()
    items = Phone.objects.order_by("sold")[::-1]
    return render(request,"kaan/analysis/product.html",{'items':items,'phones': phones })

def update(request):
    if request.method == "POST":
        choiceB  = request.POST["choicesB"]
        choiceP = request.POST["choicesP"]
        b = Brand.objects.get(pk =choiceB)
        tiki = Tiki()
        if choiceP == "0" :
            connect = create_connection("db.sqlite3")
            
            skus = tiki.get_SKU(b.url)
            for sku in skus :
                tmp = Phone.objects.all().filter(sku=sku)
                if tmp == [] :
                    try :
                        info = tiki.get_Info(tmp.productURL)
                        data = (info[0],info[1],info[2],info[3],info[4],info[5],b.id,info[6],info[7],info[9])
                        updateBrand(connect,data,info[8])
                    except:
                        return HttpResponse("Not Succesful !!!")
            tiki.driver.quit()
            return HttpResponse("Successful!!!")
        else :
            p = Phone.objects.get(pk = choiceP)
            connect = create_connection("db.sqlite3")
            try:
                data = tiki.get_Info(p.productURL)
                updatePhone(connect,p.id,data)
            except:
                return HttpResponse("Not Successful !!")
            tiki.driver.quit()
            return HttpResponse("Successful-Hi!")
    Brands = Brand.objects.all()
    Phones = Phone.objects.all()
    Comments = Comment.objects.all()
    return render(request,"kaan/update.html",{"Brands" : Brands,"Phones": Phones,"Comments" : Comments})