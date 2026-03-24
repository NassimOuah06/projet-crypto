from django.contrib import admin

# Register your models here.
from .models import User, Med, Pat, Dossier, Consultation

admin.site.register(User)
admin.site.register(Med)
admin.site.register(Pat)
admin.site.register(Dossier)
admin.site.register(Consultation)

