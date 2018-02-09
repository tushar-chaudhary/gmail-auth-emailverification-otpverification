import random
import hashlib
import os
import requests
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from .forms  import SignupForm
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from .tokens  import account_activation_token
from django.contrib.auth.models import User
from django.core.mail import EmailMessage


def signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.refresh_from_db()  # load the profile instance created by the signal
            user.save()
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=user.username, password=raw_password)
            login(request, user)
            current_site = get_current_site(request)
            message = render_to_string('acc_active_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user),
            })
            mail_subject = 'Activate your blog account.'
            to_email = form.cleaned_data.get('email')
            email = EmailMessage(mail_subject, message, to=[to_email])
            email.send()
            return render(request, 'confirm.html', {})

    else:
        form = SignupForm()
    return render(request, 'signup.html', {'form': form})

def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user, backend='django.contrib.auth.backends.ModelBackend')
        # return redirect('home')
        return render(request,'confirmed.html', {})

    else:
        return HttpResponse('Activation link is invalid!')


def index(request):
    """Displays the page that asks for the phone number"""
    return render(request, "verify/sms.html")

def verify(request):
    """Displays the page that asks for the verification code"""
    # if the form wasn't submitted properly, then go to index page
    try:
        phoneNumber = request.POST['phonenumber']
    except:
        return render(request, "verify/sms.html")

    verificationCode = str(random.randint(1000000, 9999999))

    # the check sequence is sent to the next page to verify if the code entered is correct
    checkSequence = hashlib.sha1((verificationCode+str(os.environ.get("SEED"))).encode("utf-8")).hexdigest()

    sendVerificationCode(phoneNumber, verificationCode)
    return render(request, "verify/verification.html", {"code": checkSequence})

def checkCode(request):
    """Checks if the verification code entered is correct"""
    try:
        verificationCode = request.GET['verification']
        correctCheckSequence = request.GET['code']
    except:
        return render(request, "verify/sms.html")

    # check the correct check sequence against the check sequence based on the verification code provided
    checkSequence = hashlib.sha1((verificationCode+str(os.environ.get("SEED"))).encode("utf-8")).hexdigest()
    if checkSequence == correctCheckSequence:
        return HttpResponse("1")
    else:
        return HttpResponse("0")

def sendVerificationCode(phoneNumber, verificationCode):
    """Sends the verification code to the provided phone number using TILL API"""
    if len(phoneNumber) < 10:
        return              # doesn't give the user an error message - just doesn't send the message

    TILL_URL = "https://platform.tillmobile.com/api/send/?username=chaudharyt1997@gmail.com&api_key=05f2985c90baeae282b64de22779b842edafce13"
    requests.post(TILL_URL, json={"phone":[phoneNumber], "text": "Verication code: " + str(verificationCode)})


def home(request):
	return render(request, 'home.html')
