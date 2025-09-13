from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse

from .models import *
# Create your views here.
def index(request):
    return render(request, "roombook/index.html", {
        'classrooms': Classrooms.objects.all()
    })

def classroom(request, classroom_id):
    classroom = get_object_or_404(Classrooms, pk=classroom_id)
    return render(request, "roombook/classrooms.html", {
        'classroom': classroom,
        'students': classroom.students.all(),
        'non_students': Students.objects.exclude(rooms=classroom).all()
    })

def book(request, classroom_id):
    classroom = get_object_or_404(Classrooms, pk=classroom_id)
    if request.method == "POST":
        student_id = request.POST.get("student")
        if student_id:
            student = get_object_or_404(Students, pk=student_id)
            if classroom.can_add_student():
                student.rooms.add(classroom)
    return HttpResponseRedirect(reverse("classroom", args=(classroom.id,)))