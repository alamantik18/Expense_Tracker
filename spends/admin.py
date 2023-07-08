from django.contrib import admin
from .models import *


class TagInline(admin.TabularInline):
    model = Tag


@admin.register(Spend)
class SpendAdmin(admin.ModelAdmin):

    def has_add_permission(self, request):
        return False

    list_display = ('amount_spent', 'date_of_creation', 'category')
    search_fields = ('amount_spent', )
    filter = ('category', )
    inlines = (TagInline, )