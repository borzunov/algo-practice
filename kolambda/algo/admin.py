from django.contrib import admin

from .models import Algorithm, Submit


class AlgorithmAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}

admin.site.register(Algorithm, AlgorithmAdmin)
admin.site.register(Submit)
