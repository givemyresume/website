from django.shortcuts import render,redirect
from django.contrib import messages
from django.http import HttpResponseNotFound
from django.views.decorators.csrf import csrf_exempt
from faunadb import query as q
from faunadb.objects import Ref
from faunadb.client import FaunaClient
import pytz
import hashlib
import datetime
import requests
import os


API_URL = os.getenv("API_URL")
FAUNA_DB_KEY = os.getenv("FAUNA_DB_KEY")


client = FaunaClient(secret=FAUNA_DB_KEY)
indexes = client.query(q.paginate(q.indexes()))

# Create your views here.
def index(request):
    return render(request,"index.html")


@csrf_exempt
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


@csrf_exempt
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


@csrf_exempt
def create_resume(request):
    if request.method=="POST":
        # print(request.POST)
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
                    "school":request.POST.getlist("education_school")[0],
                    "start":request.POST.getlist("education_start")[0],
                    "end":request.POST.getlist("education_end")[0],
                    "details":request.POST.getlist("education_details")[0],
                },
                "2":{
                    "school":request.POST.getlist("education_school")[1],
                    "start":request.POST.getlist("education_start")[1],
                    "end":request.POST.getlist("education_end")[1],
                    "details":request.POST.getlist("education_details")[1],
                },
                "3":{
                    "school":request.POST.getlist("education_school")[2],
                    "start":request.POST.getlist("education_start")[2],
                    "end":request.POST.getlist("education_end")[2],
                    "details":request.POST.getlist("education_details")[2],
                }
            },
            "job":{
                "1":{
                    "employer":request.POST.getlist("job_employer")[0],
                    "position":request.POST.getlist("job_position")[0],
                    "start":request.POST.getlist("job_start")[0],
                    "end":request.POST.getlist("job_end")[0],
                    "details":request.POST.getlist("job_details")[0],
                },
                "2":{
                    "employer":request.POST.getlist("job_employer")[1],
                    "position":request.POST.getlist("job_position")[1],
                    "start":request.POST.getlist("job_start")[1],
                    "end":request.POST.getlist("job_end")[1],
                    "details":request.POST.getlist("job_details")[1],
                },
                "3":{
                    "employer":request.POST.getlist("job_employer")[2],
                    "position":request.POST.getlist("job_position")[2],
                    "start":request.POST.getlist("job_start")[2],
                    "end":request.POST.getlist("job_end")[2],
                    "details":request.POST.getlist("job_details")[2],
                }
            },
            "project":{
                "1":{
                    "name":request.POST.getlist("project_name")[0],
                    "end":request.POST.getlist("project_end")[0],
                    "details":request.POST.getlist("project_details")[0],
                },
                "2":{
                    "name":request.POST.getlist("project_name")[1],
                    "end":request.POST.getlist("project_end")[1],
                    "details":request.POST.getlist("project_details")[1],
                },
                "3":{
                    "name":request.POST.getlist("project_name")[2],
                    "end":request.POST.getlist("project_end")[2],
                    "details":request.POST.getlist("project_details")[2],
                }
            },
            "references":request.POST.get("references"),
        }
        try:
            quiz = client.query(q.create(q.collection("Resume_Info"), {
                "data": data
            }))
            context={"resume_info":data}
            api_response = requests.get(f'{API_URL}/resume/{data["user"]}').json()
            message = "Resume Info Edited Successfully. Download Resume Now"
            if api_response["status"] == "SUCCESS":
                message = api_response["message"]
            elif api_response["status"] == "FAILED":
                message = api_response["message"]
            messages.add_message(request, messages.INFO, message)
            return render(request,"create-resume.html",context)
        except:
            resume = client.query(q.get(q.match(q.index("resume_index"), data["user"])))
            quiz = client.query(q.update(q.ref(q.collection("Resume_Info"),resume["ref"].id()), {
                "data": data
            }))
            context={"resume_info":data}
            api_response = requests.get(f'{API_URL}/resume/{data["user"]}').json()
            message = "Resume Info Edited Successfully. Download Resume Now"
            if api_response["status"] == "SUCCESS":
                message = api_response["message"]
            elif api_response["status"] == "FAILED":
                message = api_response["message"]
            messages.add_message(request, messages.INFO, message)
            return render(request,"create-resume.html",context)
    else:
        try:
            data = client.query(q.get(q.match(q.index("resume_index"), request.session["user"]["username"])))["data"]
            context={"resume_info":data}
            return render(request,"create-resume.html",context)
        except:
            return render(request,"create-resume.html")

def resume(request):
    return redirect(f"https://givemyresume.github.io/{request.session['user']['username']}")
