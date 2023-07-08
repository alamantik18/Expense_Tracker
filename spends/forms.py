from django import forms

from .models import Spend, Tag


class CreateSpendForm(forms.Form):
    CATEGORY_CHOICES = (
        ('', '--------'),
        ('groceries', 'продукты'),
        ('transportation', 'транспорт'),
        ('entertainment', 'развлечения'),
        ('housing', 'дом'),
        ('medical', 'медицина'),
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(CreateSpendForm, self).__init__(*args, **kwargs)

    amount_spend = forms.FloatField(
        required=True,
        help_text='Потраченная сумма.',
        label='Сумма операции',
        widget=forms.NumberInput(attrs={'class': 'form-create full-row', 'placeholder': 'Сумма'}),
    )
    description = forms.CharField(
        help_text='Введите описание покупки',
        label='Описание операции',
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-create', 'placeholder': 'Описание', 'rows': '5'}),
    )
    date = forms.DateTimeField(
        label='Дата',
        widget=forms.DateInput(
            attrs={
                'class': 'form-create datepicker',
                'placeholder': 'Дата траты',
                'id': 'datepicker',
                'autocomplete': 'off',
            }),
        input_formats=('%Y-%m-%d', '%Y.%m.%d')
    )
    category = forms.ChoiceField(
        choices=CATEGORY_CHOICES,
        label='Категория',
        required=False,
        widget=forms.Select(attrs={'class': 'form-create category-select', 'placeholder': 'Категория'}),
    )

    class Meta:
        model = Spend
        fields = ('amount_spend', 'description', 'date', 'category')

    def save(self):
        amount_spend, description, date, category, user = self.cleaned_data.get('amount_spend'), \
            self.cleaned_data.get('description'), \
            self.cleaned_data.get('date'), \
            self.cleaned_data.get('category'), \
            self.user
        spend = Spend.objects.create(
            description=description,
            amount_spent=amount_spend,
            date=date,
            category=category,
            user_id=user.pk
        )
        spend.save()
        return spend


class CreateTagForm(forms.ModelForm):
    name = forms.CharField(
        help_text='Введите свои теги',
        label='Теги',
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-create', 'placeholder': 'Теги'}),
    )

    class Meta:
        model = Tag
        fields = ('name',)