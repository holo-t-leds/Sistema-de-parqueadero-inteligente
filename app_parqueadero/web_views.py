from django.shortcuts import render


def demo_login(request):
    return render(request, 'app_parqueadero/login.html')
