from django.core.validators import FileExtensionValidator
from django.db import models

class Upload(models.Model):
    target_year = models.IntegerField()
    target_month = models.IntegerField()
    excel = models.FileField(upload_to='excel_files/', validators=[FileExtensionValidator(allowed_extensions=["xlsx"], message="Ar keliamas failas yra \".xlsx\"?")])


    @property
    def file_url(self):
        return self.excel.url

    def __str__(self) -> str:
        return self.excel