from django.contrib.auth.views import LoginView
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.contrib.auth import get_user_model, login, authenticate
from django.views.generic.edit import CreateView
from django.db.models.query_utils import Q

from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import EmailMessage
from django.contrib.auth.decorators import login_required

from .forms import SignupForm, LoginForm, CustomSetPasswordForm, CustomPasswordResetForm
from .tokens import account_activation_token


def activateEmail(request, user, to_email, email_type='activate'):
    email_subject = f'Подтверждение электронной почты для сайта ExpenseTracker'
    message = render_to_string(
        'account/email_confirmation_template.html', {
            'domain': get_current_site(request).domain,
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': account_activation_token.make_token(user),
            'email_type': email_type,
            'protocol': 'https' if request.is_secure() else 'http',
        }
    )
    email = EmailMessage(email_subject, message, to=[to_email])
    if email.send():
        print('Электронное письмо отправлено.')
    else:
        print(f'Не удалось отправить письмо на адрес {to_email}')


class SignupView(CreateView):
    template_name = 'account/signup.html'
    form_class = SignupForm
    success_url = reverse_lazy('my_spends')

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('my_spends')
        form = self.get_form()
        return render(request, self.template_name, context={'form': form})

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            email = form.cleaned_data.get('email')
            user.save()
            activateEmail(request, user, email)
            return redirect('confirmation_email')
        else:
            form = self.get_form()
            return render(request, self.template_name, context={'form': form})


class CustomLoginView(CreateView):
    form_class = LoginForm
    template_name = 'account/login.html'
    redirect_authenticated_user = True

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('my_spends')
        form = self.get_form()
        return render(request, self.template_name, context={'form': form})

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            user = authenticate(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password'],
            )
            login(request, user)
            return redirect('my_spends')
        else:
            form = self.get_form()
            print(form.errors.values)
            return render(request, self.template_name, context={'form': form})


def confirmation_email(request):
    if request.user.is_authenticated:
        return redirect('my_spends')
    return render(request, 'account/email_confirmation_sent.html')


def activate_account(request, uidb64, token):
    User = get_user_model()
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except Exception:
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        return redirect('account_login')
    else:
        return redirect('account_signup')


class ChangePassword(CreateView):
    template_name = 'account/password_change.html'
    success_url = 'account_login'

    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('my_spends')
        user = request.user
        form = CustomSetPasswordForm(user)
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        user = request.user
        form = CustomSetPasswordForm(user, request.POST)
        if form.is_valid():
            form.save()
            return redirect(self.success_url)
        else:
            form = CustomSetPasswordForm(user, request.POST)
            return render(request, self.template_name, context={'form': form})


class ResetPassword(CreateView):
    template_name = 'account/password_reset.html'
    form_class = CustomPasswordResetForm
    success_url = 'account/login.html'

    def get(self, request, *args, **kwargs):
        form = self.get_form()
        return render(request, self.template_name, context={'form': form})

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            user_email = form.cleaned_data.get('email')
            associated_user = get_user_model().objects.filter(Q(email=user_email)).first()
            if associated_user:
                activateEmail(request, associated_user, user_email, email_type='reset')
                message = 'На вашу почту отправлено письмо. Пожалуйста, подтвердите пароль и авторизуйтесь'
                form = LoginForm()
                return render(request, self.success_url, context={'form': form, 'message': message})
            else:
                message = 'Указанный адрес электронной почты не зарегистрирован.'
                form = self.get_form()
                return render(request, self.template_name, context={'form': form, 'error': message})


def password_reset_confirm(request, uidb64, token):
    User = get_user_model()
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
        print(user)
    except:
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        if request.method == 'POST':
            form = CustomSetPasswordForm(user, request.POST)
            if form.is_valid():
                form.save()
                return redirect('my_spends')
            else:
                form = CustomSetPasswordForm(user, request.POST)
                return render(request, 'account/password_reset_confirm.html', context={'form': form})

        form = CustomSetPasswordForm(user)
        return render(request, 'account/password_reset_confirm.html', {'form': form})
    else:
        return redirect("account_signup")