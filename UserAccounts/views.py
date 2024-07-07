from django.shortcuts import render,HttpResponse

def signup(request):
    return render (request,'Signup.html')
def Register(request):
    if request.method=="POST":
        username=request.get(req,username)
        password=request.get(req,password)
        email=request.get(req,mail)
        phone=request.get(req,phone)
        return render(request,'Otp.html')
    

def Otp(request):
    
    
    
    
