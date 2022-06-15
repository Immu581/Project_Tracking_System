from django.shortcuts import render,redirect
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from .models import *
import random


# Create your views here.
def login(request):
    if request.method=='POST':
        username=request.POST['username']
        password=request.POST['password']
        #print(username,password)
        if username=="" and password=="":
            #open project coordinators related pages
            p=Project.objects.all()
            if(p.count()!=0):
                pid=[str(i.pid) for i in p]
                title=[str(i.title) for i in p]
                myzip=zip(pid,title)
                return render(request,"Projectdetails.html",{'myzip':myzip,'t':False});
            else:
                return render(request,"Projectdetails.html",{'myzip':[],'t':True});
        elif Mentor.objects.filter(memailid=username,mpassword=password).exists():
            m=Mentor.objects.filter(memailid=username,mpassword=password);
            mid=[i.mid for i in m]
            #print(mid)
            pid,rollno=[],[]
            for i in mid:
                a=Assign.objects.filter(mid=i)
                for j in a:
                    pid.append(j.pid)
                    rollno.append(j.rollno)
            pid=list(set(pid))
            titles=[]
            for i in pid:
                for j in Project.objects.filter(pid=i):
                    titles.append(j.title)
            #print(pid,titles,rollno)
            return render(request,"mentor1.html",{'myzip':zip(pid,titles)})
        elif Project.objects.filter(username=username,password=password).exists():
            #open student related pages
            p=Project.objects.filter(username=username,password=password)
            l=[]
            tit=""
            for i in p:
                l.append(int(i.pid))
                tit=str(i.title)
                break
            #print(l,tit,p)
            s=Assign.objects.filter(pid=l[0])
            rolls=[str(i.rollno) for i in s]
            mentor=""
            for i in Assign.objects.filter(pid=l[0]):
                for j in Mentor.objects.filter(mid=i.mid):
                    mentor=j.mname
            #print(mentor)
            names=[]
            emails=[]
            for i in rolls:
                for j in Student.objects.filter(rollno=i):
                    names.append(j.name)
                    emails.append(j.emailid)
            #print(emails,tit,rolls,names,l)

            d1,d2,d3="","",""
            for i in Review.objects.all():
                if i.r1!='0':d1=i.r1
                else:d1=""
                if i.r2!='0':d2=i.r2
                else:d2=""
                if i.r3!='0':d3=i.r3
                else:d3=""
            r1,r2,r3,avg=[],[],[],[]
            for i in rolls:
                for j in Evaluation.objects.filter(rollno=i):
                    r1.append(j.m1)
                    r2.append(j.m2)
                    r3.append(j.m3)
                    avg.append(j.avg)
            myzip=zip(rolls,names,r1,r2,r3,avg)
            
            return render(request,"student.html",{'title':tit,'mentor':mentor,'emailid':emails,'d1':d1,'d2':d2,'d3':d3,'myzip':myzip})
        else:
            messages.info(request,"username or password in wrong")
            return redirect("/")





        return render(request,"index.html")
    return render(request,"login.html")


def register(request):
    if request.method=="POST":
        title=request.POST['ptitle']
        size=int(request.POST.get('size',7))
        username=request.POST['username']
        password=request.POST['password']
        #store all the details in db;
        if Project.objects.filter(title=title).exists():
            messages.info(request,title+" already registered in another project")
            return render(request,"register1.html")
        elif Project.objects.filter(username=username).exists():
            messages.info(request,username+" already used in another project")
            return render(request,"register1.html")
        #print(size,username,password)
        return render(request,"register2.html",{'title':title,'size':range(size),'username':username,'password':password,'count':size})
    return render(request,"register1.html")

def complete_registration(request):
    name=request.GET.getlist('name')
    rollno=request.GET.getlist('rollno')
    emailid=request.GET.getlist('emailid')
    title=request.GET['ptitle']
    username=request.GET['username']
    password=request.GET['password']
    size=int(request.GET['size'])
    #branch=request.POST.getlist('branch')
    #print(name,rollno,emailid)
    for i in range(len(name)):
        if Student.objects.filter(rollno=rollno[i]).exists():
            messages.info(request,rollno[i]+" already registered in another project")
            return redirect("/register")
        if Student.objects.filter(emailid=emailid[i]).exists():
            messages.info(request,emailid[i]+" already registered in another project")
            return redirect("/register")
        else:
            Student(rollno=rollno[i],emailid=emailid[i],name=name[i]).save()
    Project(title=title,username=username,password=password).save()
    p=Project.objects.all();
    l=[int(i.pid) for i in p if str(i.title)==title]
    #print(l)
    for i in range(len(name)):
        Assign(rollno=rollno[i],pid=l[0]).save();
        Evaluation(rollno=rollno[i],m1=0,m2=0,m3=0,avg=0).save()
    return render(request,"index.html")


def forget(request):
    if request.method=="POST":
        username=request.POST['username']
        if not Project.objects.filter(username=username).exists():
            messages.info(request,username+" doesnot exists")
            return redirect("/forget")
        subject="OTP status"
        num=random.randint(100000,999999)
        print(username,num)
        message="Your One Time Password (OTP)  is: "+str(num)
        # send mails to all mails corresponding to username 
        p=Project.objects.all();
        l=[int(i.pid) for i in p if str(i.username)==username]
        project_id=l[0];
        l=[]
        a=Assign.objects.all();
        l=[str(i.rollno) for i in a if int(i.pid)==project_id]
        s=Student.objects.all()
        emails=[]
        for i in s:
            for j in l:
                if str(i.rollno)==j:
                    emails.append(str(i.emailid))
                    break;
        #print(emails)
        '''for i in emails:
            if not send_mail(subject,message,settings.EMAIL_HOST_USER,[i],fail_silently=False):
                messages.info(request,"email is not valid")
                return redirect('/forget')'''
        return render(request,"otp.html",{'otp':num,'username':username})
    return render(request,"Forget.html")

def forget_user(request):
    if request.GET['otp1']==request.GET['otp']:
        #print(request.GET['username1'])
        return render(request,"password.html",{'username':request.GET['username1']})
    messages.info(request,"otp is not matching")
    return render(request,"Forget.html")   #need send otp messages to same html page

def change_password(request):
    #if request.method=="POST":
        username=request.GET['username']
        pass1=request.GET['pass1']
        pass2=request.GET['pass2']
        if pass1==pass2:
            #print(username,pass1,pass2)
            p=Project.objects.all()
            l=[int(i.pid) for i in p if str(i.username)==username]
            k=Project(pid=l[0],password=pass1)
            k.save(update_fields=['password'])
            #print(p)
            return render(request,"index.html") # need to show the success page
        else:
            messages.info(request,"passwords are not matching")
            return render(request,'password.html') 


def project(request):
    pid=int(request.GET.get('params'))
    t=Project.objects.filter(pid=pid)
    title=[str(i.title) for i in t]
    a=Assign.objects.filter(pid=pid)
    rollno=[str(i.rollno) for i in a]
    names=[]
    for i in rollno:
        s=Student.objects.filter(rollno=i)
        for j in s:
            names.append(j.name)
            break
    #print(names,rollno,title[0])
    myzip=zip(rollno,names)
    m=Mentor.objects.all()
    mids=[int(i.mid) for i in m]
    #print(mids)
    mod=[]
    mod_id=[]
    for i in mids:
        l=[]
        a=Assign.objects.filter(mid=i)
        for j in a:
            l.append(j.pid)
        if len(set(l))<2:
            k=Mentor.objects.filter(mid=int(i))
            for j in k:
                mod_id.append(i)
                mod.append(j.mname)
    mentors=zip(mod_id,mod)
    if request.method=="POST":
        mid=int(request.POST['size'])
        print(pid,mid)
        s=Assign.objects.filter(pid=pid)
        l=[int(i.id) for i in s]
        #print(l)
        for i in l:
            Assign(id=i,mid=mid).save(update_fields=['mid'])
    # adding mentors is pending
    mentor="";
    a=Assign.objects.filter(pid=pid)
    for i in a:
        if Mentor.objects.filter(mid=i.mid).exists():
            for j in Mentor.objects.filter(mid=i.mid):
                mentor=j.mname
                break
        break
    return render(request,"project.html",{'myzip':myzip,'title':title[0],'mentors':mentors,'mentor':mentor})


def addmentors(request):
    if request.method=="POST":
        name=request.POST['name']
        emailid=request.POST['emailid']
        password=request.POST['password']
        #print(name,emailid)
        try:
            if(Mentor.objects.filter(memailid=emailid).exists()):
                messages.info(request,name+" already exists")
            else:
                Mentor(mname=name,memailid=emailid,mpassword=password).save()
                messages.info(request,name+" details are added successfully")
        except:
            messages.info(request,"something went wrong")
        return redirect('/addmentors')
    return render(request,"Addmentors.html")

def reviewdates(request):
    if request.method=="POST":
        dates=request.POST['dates']
        reviewno=request.POST['reviewno']
        if(dates!=""):
            if(reviewno=="1"):
                Review(id=1,r1=dates).save(update_fields=['r1'])
            if(reviewno=="2"):
                Review(id=1,r2=dates).save(update_fields=['r2'])
            if(reviewno=="3"):
                Review(id=1,r3=dates).save(update_fields=['r3'])
    r=Review.objects.all()
    l=[]
    for i in r:
        print(i)
        if(i.r1!='0'):l.append(i.r1)
        else:l.append("")
        if(i.r2!="0"):l.append(i.r2)
        else:l.append("")
        if(i.r3!="0"):l.append(i.r3)
        else:l.append("")
    #print(l)
    return render(request,"Reviewdates.html",{'a':l[0],'b':l[1],'c':l[2]})

def projectdetails(request):
    p=Project.objects.all()
    if(p.count()!=0):
        pid=[str(i.pid) for i in p]
        title=[str(i.title) for i in p]
        myzip=zip(pid,title)
        return render(request,"Projectdetails.html",{'myzip':myzip,'t':False});
    else:
        return render(request,"Projectdetails.html",{'myzip':[],'t':True});


def marks(request):
    pid=int(request.GET.get('params'))
    titles=[str(i.title) for i in Project.objects.filter(pid=pid)]
    rollno=[str(i.rollno) for i in Assign.objects.filter(pid=pid)]
    #print(pid,titles)
    names=[]
    for i in rollno:
        s=Student.objects.filter(rollno=i)
        for j in s:
            names.append(j.name)
    d1,d2,d3="","",""
    for i in Review.objects.all():
        if i.r1!='0':d1=i.r1
        else:d1=""
        if i.r2!='0':d2=i.r2
        else:d2=""
        if i.r3!='0':d3=i.r3
        else:d3=""
    if request.method=="POST":
        rollno1=request.POST.getlist('rollno1')
        r11=request.POST.getlist('r11')
        r12=request.POST.getlist('r12')
        r13=request.POST.getlist('r13')
        #print(rollno1,r11,r12,r13)
        k=0
        for i in rollno1:
            for j in Evaluation.objects.filter(rollno=i):
                r1=float(r11[k])
                r2=float(r12[k])
                r3=float(r13[k])
                avg1=float((r1+r2+r3)/3)
                #print(r1,r2,r3,avg1)
                Evaluation(rollno=i,m1=r1,m2=r2,m3=r3,avg=avg1).save(update_fields=['m1','m2','m3','avg'])
            k+=1
    r1,r2,r3,avg=[],[],[],[]
    for i in rollno:
        for j in Evaluation.objects.filter(rollno=i):
            r1.append(j.m1)
            r2.append(j.m2)
            r3.append(j.m3)
            avg.append(j.avg)
    #print(r1,r2,r3,avg)  
    myzip=zip(rollno,names,r1,r2,r3,avg)
    return render(request,"mentor.html",{'myzip':myzip,'pid':pid,'titles':titles[0],'d1':d1,'d2':d2,"d3":d3})


def mentorreport(request):
    n=[ i.mname for i in Mentor.objects.all()]
    ids=[ i.mid for i in Mentor.objects.all()]
    if request.method=="POST":
        name=request.POST['size']
        #print(name)
        pids=[]
        #rollnos=[]
        for i in Assign.objects.filter(mid=name):
            #rollnos.append(i.rollno)
            if i.pid not in pids:
                pids.append(i.pid)
        titles=[]
        students=[]
        for i in pids:
            for j in Project.objects.filter(pid=i):
                if j.title not in titles:
                    titles.append(j.title)
            # redirect to some html page



            
        return render(request,"mentorreport2.html",{'myzip':myzip})
    

    return render(request,"mentorreport.html",{'myzip':zip(n,ids)})