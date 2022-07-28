from pyexpat import model
from django.shortcuts import redirect, render
from django.views.generic import TemplateView
from django.core.files.storage import FileSystemStorage
from django.core.mail import EmailMessage

import sys
import os
sys.path.append("..")
from classModule.class_ics import Worker

from .models import Upload
from .forms import UploadForm
from .models import Upload

class homepage(TemplateView):
    template_name = 'home.html'

def upload(request):
    form = Upload()
    if request.method == 'POST':
        form = UploadForm(request.POST, request.FILES)
        print(request.POST)
        
        if form.is_valid():
            form.save()
            
            form_data = Upload.objects.latest('id')
            path = os.path.join(os.path.dirname(os.path.dirname(__file__))) + form_data.excel.url

            Worker.initiate_from_excel(path)
            ics_file_location = Worker.do_ics(form_data.target_year, form_data.target_month)
            print(form_data.target_month)
            print(form_data.target_year)
            name_list = Worker.name_list()
            Worker.clean_list()

            request.session['ics_file_location'] = ics_file_location
            request.session['name_list'] = name_list
            request.session['target_year'] = form_data.target_year
            request.session['target_month'] = form_data.target_month

            return redirect('after_upload')

    else:
        form = UploadForm()

    return render(request, 'upload.html', {'form': form})
    
def upload_list(request):
    upload = Upload.objects.all()
    return render(request, 'upload_list.html', {'upload': upload})

def after_upload(request):
    ics_file_location = request.session.get('ics_file_location')
    names = request.session.get('name_list')
    year = request.session.get('target_year')
    month = request.session.get('target_month')

    # need to create a function which creates an email addres from the path!!!
    for file_path in ics_file_location:
        msg = EmailMessage(f'Darbo grafikas {year}-{month}', '', 'schedulify@domka.lt', ['domantas.karpinskas@ideal.lt'])
        msg.content_subtype = "html"  
        msg.attach_file(file_path)
        msg.send()

    Upload.objects.all().delete()

    return render(request, 'after_upload.html', {'names': names})
