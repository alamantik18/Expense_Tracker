from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.shortcuts import render, redirect
from django.utils.text import slugify
from django.views.generic import CreateView
from django.contrib.auth import get_user_model
from django.db.models import Sum

from datetime import datetime, timedelta

from .forms import *


@login_required(login_url='account_login')
def user_spends(request):
    user = get_user_model().objects.get(pk=request.user.pk)
    return render(request, 'app/home_page.html', {'spends': user.user_spends.all()})


@method_decorator(login_required(login_url='account_login'), 'dispatch')
class CreateSpend(CreateView):
    template_name = 'app/create_spend.html'
    success_url = 'my_spends'

    def get(self, request, *args, **kwargs):
        form_spend, form_tag = CreateSpendForm(user=request.user), CreateTagForm
        return render(request, self.template_name, {'form_spend': form_spend, 'form_tag': form_tag})

    def post(self, request, *args, **kwargs):
        form_spend, form_tag = CreateSpendForm(request.POST, user=request.user), CreateTagForm(request.POST)
        if form_spend.is_valid() and form_tag.is_valid():
            spend = form_spend.save()
            if form_tag:
                tag_names = form_tag.cleaned_data['name'].split()
                for tag_name in tag_names:
                    tag = Tag.objects.create(name=tag_name, spend=spend)
                    tag.save()
            spend.save()
            return redirect(self.success_url)
        else:
            return render(request, self.template_name, {'form_spend': form_spend, 'form_tag': form_tag})


@method_decorator(login_required(login_url='account_login'), 'dispatch')
class ViewReports(CreateView):
    template_name = 'app/view_reports.html'

    @staticmethod
    def get_spends_by_term(request, data_term: int) -> dict:
        user = get_user_model().objects.get(pk=request.user.pk)
        today = datetime.now().date()
        spends_term = user.user_spends.filter(date__gt=today - timedelta(days=data_term)).order_by('date').values('date').annotate(total_amount=Sum('amount_spent'))
        amount_spend = user.user_spends.filter(date__gt=today - timedelta(days=data_term)).aggregate(
            total_amount=Sum('amount_spent'))
        print(type(spends_term.values_list('date', flat=True)), type(spends_term.values_list('amount_spent', flat=True)))
        return {"spends": {
                    "dates": [spend['date'].strftime('%y-%m-%d') for spend in spends_term],
                    "amounts": [spend['total_amount'] for spend in spends_term],
                },
                "amount_spend": amount_spend}

    def get(self, request, *args, **kwargs):
        user = get_user_model().objects.get(pk=request.user.pk)
        spends = user.user_spends.all()
        data_week = self.get_spends_by_term(request, 7)
        data_month = self.get_spends_by_term(request, 30)
        data_threemonth = self.get_spends_by_term(request, 90)
        data_halfyear = self.get_spends_by_term(request, 180)
        data_year = self.get_spends_by_term(request, 365)
        context = {
            'spends': spends,
            'data_week': data_week,
            'data_month': data_month,
            'data_threemonth': data_threemonth,
            'data_halfyear': data_halfyear,
            'data_year': data_year,
        }
        return render(request, self.template_name, context)
