import enum
from pyexpat import model
from django.shortcuts import redirect, render
from django.views.generic import TemplateView
from django.core.files.storage import FileSystemStorage
from django.core.mail import EmailMessage

import sys
import os
sys.path.append("..")
from classModule.class_ics import Worker, createMailAddress

from .models import Upload
from .forms import UploadForm
from .models import Upload

def upload(request):

    Upload.objects.all().delete()
    Worker.clean_list()

    form = Upload()
    if request.method == 'POST':
        form = UploadForm(request.POST, request.FILES)
        
        if form.is_valid():
            form.save()
            
            form_data = Upload.objects.latest('id')
            path = os.path.join(os.path.dirname(os.path.dirname(__file__))) + "/media/" + form_data.excel.name

            Worker.magicWrapper(path, form_data.target_year, form_data.target_month) 

            return redirect('after_upload')

    else:
        form = UploadForm()

    return render(request, 'upload.html', {'form': form})
    
def upload_list(request):
    upload = Upload.objects.all()
    return render(request, 'upload_list.html', {'upload': upload})

def after_upload(request):

    # ------------ [ [name, email, completionMessage, path], ... ]
    data = Worker.displayInformationArray

    for index, sublist in enumerate(data):
        # ------ ------ ------ ------ ------ ------ ------ ------ ------ ------ ------  createMailAddress(file_path)
        msg = EmailMessage(f'Darbo grafikas {Worker.targetYear}-{Worker.targetMonth}', '', 'schedulify@domka.lt', ['domantas.karpinskas@ideal.lt'])
        msg.content_subtype = "html"  
        msg.attach_file(data[index][3])
        #msg.send()

    return render(request, 'after_upload.html', {'data': data})
0