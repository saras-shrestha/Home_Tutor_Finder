from django.shortcuts import render
# Create your views here.

def admin_dashboard(request):
    return render(request, "admin_panel/admin_dashboard.html")

def admin_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
    return render(request, "admin_panel/admin_login.html")
    
