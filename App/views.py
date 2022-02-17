from django.shortcuts import render,redirect
from django.contrib import messages
from django.http import HttpResponseNotFound
from faunadb import query as q
from faunadb.objects import Ref
from faunadb.client import FaunaClient
import pytz
import hashlib
import datetime
import requests


API_URL = "http://0.0.0.0:8001"
client = FaunaClient(secret="fnAEffAgzSACTABvMpg2lOwlPquGo_oNvuN1XHbA")
indexes = client.query(q.paginate(q.indexes()))

# Create your views here.
def index(request):
    return render(request,"index.html")


def register(request):
    if request.method == "POST":
        username = request.POST.get("username").strip().lower()
        email = request.POST.get("email").strip().lower()
        password = request.POST.get("password")

        try:
            user = client.query(q.get(q.match(q.index("users_index"), username)))
            messages.add_message(request, messages.INFO, 'User already exists with same username.')
            return redirect("App:register")
        except:
            user = client.query(q.create(q.collection("Users"), {
                "data": {
                    "username": username,
                    "email": email,
                    "password": hashlib.sha512(password.encode()).hexdigest(),
                    "date": datetime.datetime.now(pytz.UTC)
                }
            }))
            messages.add_message(request, messages.INFO, 'Registration successful.')
            return redirect("App:login")
    return render(request,"register.html")


def login(request):
    if request.method == "POST":
        username = request.POST.get("username").strip().lower()
        password = request.POST.get("password")

        try:
            user = client.query(q.get(q.match(q.index("users_index"), username)))
            if hashlib.sha512(password.encode()).hexdigest() == user["data"]["password"]:
                request.session["user"] = {
                    "id": user["ref"].id(),
                    "username": user["data"]["username"]
                }
                return redirect("App:index")
            else:
                raise Exception()
        except:
            messages.add_message(request, messages.INFO,"You have supplied invalid login credentials, please try again!", "danger")
            return redirect("App:login")
    return render(request,"login.html")


def create_resume(request):
    if request.method=="POST":
        data = {
            "user":request.session["user"]["username"],
            "full_name":request.POST.get("name"),
            "address":request.POST.get("address"),
            "phone":request.POST.get("phone"),
            "email":request.POST.get("email"),
            "website":request.POST.get("website"),
            "summary":request.POST.get("summary"),
            "skills":request.POST.get("skills"),
            "education": {
                "1":{
                    "school":request.POST.get("education-1__school"),
                    "start":request.POST.get("education-1__start"),
                    "end":request.POST.get("education-1__end"),
                    "details":request.POST.get("education-1__details"),
                },
                "2":{
                    "school":request.POST.get("education-2__school"),
                    "start":request.POST.get("education-2__start"),
                    "end":request.POST.get("education-2__end"),
                    "details":request.POST.get("education-2__details"),
                },
                "3":{
                    "school":request.POST.get("education-3__school"),
                    "start":request.POST.get("education-3__start"),
                    "end":request.POST.get("education-3__end"),
                    "details":request.POST.get("education-3__details"),
                }
            },
            "job":{
                "1":{
                    "employer":request.POST.get("job-1__employer"),
                    "position":request.POST.get("job-1__position"),
                    "start":request.POST.get("job-1__start"),
                    "end":request.POST.get("job-1__end"),
                    "details":request.POST.get("job-1__details"),
                },
                "2":{
                    "employer":request.POST.get("job-2__employer"),
                    "position":request.POST.get("job-2__position"),
                    "start":request.POST.get("job-2__start"),
                    "end":request.POST.get("job-2__end"),
                    "details":request.POST.get("job-2__details"),
                },
                "3":{
                    "employer":request.POST.get("job-3__employer"),
                    "position":request.POST.get("job-3__position"),
                    "start":request.POST.get("job-3__start"),
                    "end":request.POST.get("job-3__end"),
                    "details":request.POST.get("job-3__details"),
                }
            },
            "project":{
                "1":{
                    "name":request.POST.get("project-1__name"),
                    "end":request.POST.get("project-1__end"),
                    "details":request.POST.get("project-1__details"),
                },
                "2":{
                    "name":request.POST.get("project-2__name"),
                    "end":request.POST.get("project-2__end"),
                    "details":request.POST.get("project-2__details"),
                },
                "3":{
                    "name":request.POST.get("project-3__name"),
                    "end":request.POST.get("project-3__end"),
                    "details":request.POST.get("project-3__details"),
                }
            },
            "references":request.POST.get("references"),
        }
        try:
            requests.get(f'{API_URL}/resume/{data["user"]}')
            resume = client.query(q.get(q.match(q.index("resume_index"), data["user"])))
            quiz = client.query(q.update(q.ref(q.collection("Resume_Info"),resume["ref"].id()), {
                "data": data
            }))
            messages.add_message(request, messages.INFO, 'Resume Info Edited Successfully. Download Resume Now')
            return redirect("App:create-resume")
        except:
            quiz = client.query(q.create(q.collection("Resume_Info"), {
                "data": data
            }))
            messages.add_message(request, messages.INFO, 'Resume Info Saved Successfully. Download Resume Now')
            return redirect("App:resume")
    else:
        try:
            resume_info = client.query(q.get(q.match(q.index("resume_index"), request.session["user"]["username"])))["data"]
            context={"resume_info":resume_info}
            return render(request,"create-resume.html",context)
        except:
            return render(request,"create-resume.html")

def resume(request):
    try:
        resume_info = client.query(q.get(q.match(q.index("resume_index"), request.session["user"]["username"])))["data"]
        context={"resume_info":resume_info}
        print(context)
        return render(request,"resume.html",context)
    except:
        return render(request,"resume.html")
