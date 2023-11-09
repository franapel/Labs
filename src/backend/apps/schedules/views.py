from django.contrib.messages.api import error
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse, request
from django.urls import reverse
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from apps.core.models import Room, Campus, Workstation
from apps.schedules.models import RoomPetition, Module, ModuleEvent
from apps.schedules.forms import RoomPetitionForm, ModuleForm, StatusRoomPetitionForm
from datetime import date, timedelta, datetime
import time 

def calendar_day(request):
    template_name = "calendar_day.html"
    context = {}
    selectdate = datetime.today().strftime("%d/%m/%Y")
    selectcampus = "all"
    campus_all = Campus.objects.all()
    if request.POST:
        selectdate = datetime.strptime(request.POST['selecteddate'], "%d/%m/%Y").date()
        selectcampus = request.POST['selectedcampus']
    else:
        selectdate = datetime.strptime(selectdate, "%d/%m/%Y").date()
    if selectcampus == "all":
        campus_list = Campus.objects.all()
        roompetition = RoomPetition.objects.filter(status_petition="A")
        room_list = Room.objects.all().order_by( 'campus', 'room_name')
        modulevent = ModuleEvent.objects.filter(day=selectdate)
    else:
        campus_list = Campus.objects.filter(id=selectcampus)
        roompetition = RoomPetition.objects.filter(room_petition__campus__id=selectcampus, status_petition="A")
        room_list = Room.objects.filter(campus__id=selectcampus).order_by( 'campus', 'room_name')
        modulevent = ModuleEvent.objects.filter(petition__room_petition__campus__id=selectcampus, day=selectdate)
    context['roompetition'] = roompetition
    context['campus_list'] = campus_list
    context['campus_all'] = campus_all
    context['room_list'] = room_list
    context['modulevent'] = modulevent
    context['selectdate'] = selectdate
    return render(request, template_name, context)

def calendar_week(request, id):
    template_name="calendar_week.html"
    context={}
    roomobj = Room.objects.get(id = id)
    roompetition = RoomPetition.objects.filter(room_petition = roomobj, status_petition="A").order_by('date_finish_petition')
    modulevent = ModuleEvent.objects.filter(petition__room_petition = roomobj).order_by('day')
    context['roompetition']=roompetition
    context['modulevent']=modulevent
    context['room']=roomobj
    return render(request, template_name, context)

def manage_module(request):
    template_name = "manage_module.html"
    context = {}
    context['moduledata'] = Module.objects.all().order_by('start_module')
    moduleform = ModuleForm(request.POST or None)
    if request.method == 'POST':
        if moduleform.is_valid():
            moduleform.save()
            return HttpResponseRedirect(reverse('manage_module'))
    context['moduleform'] = moduleform
    return render(request, template_name, context)

def manage_module_id(request, id):
    template_name = "manage_module_id.html"
    context = {}
    modid = Module.objects.get(id = id)
    moduleform = ModuleForm(request.POST or None, instance = modid)
    if request.method == 'POST':
        if moduleform.is_valid():
            moduleform.save()
            return HttpResponseRedirect(reverse('manage_module'))
    context['moduleform'] = moduleform
    return render(request, template_name, context)

def deletemodule(request, id):
    Module.objects.filter(id=id).delete()
    return HttpResponseRedirect(reverse('manage_module'))

def manage_request(request):
    template_name="manage_request.html"
    context = {}
    formroom = StatusRoomPetitionForm(request.POST or None)
    context['roompetition'] = RoomPetition.objects.all().order_by('-datetime_petition')
    context['modules'] = Module.objects.all()
    context['formroom'] = formroom
    return render(request, template_name, context)

def manage_request_id(request, id):
    template_name = "manage_request_id.html"
    context = {}
    roompetition = RoomPetition.objects.get(id = id)
    formroom = StatusRoomPetitionForm(request.POST or None, instance = roompetition)
    status = roompetition.status_petition
    if formroom.is_valid():
        formroom.save()
        if status!='A' and roompetition.status_petition=='A':
            reserve_event(roompetition)
        elif status=='A' and roompetition.status_petition!='A':
            delete_event(roompetition)
        return HttpResponseRedirect(reverse('manage_request'))
    #elif request.GET.get('DeleteButton'):
        #RoomPetition.objects.filter(id = request.GET.get('DeleteButton')).delete()
        #return HttpResponseRedirect(reverse('manage_request'))
    context['formlab'] = formroom
    context['roompetition'] = roompetition
    return render(request, template_name, context)

def request_delete_id(request, id):
    RoomPetition.objects.filter(id=id).delete()
    return HttpResponseRedirect(reverse('manage_request'))

def reserve_event(petition):
    date_current = petition.date_start_petition
    date_finish = petition.date_finish_petition
    weekDay = petition.day_petition
    recurrence_petition = int(petition.recurrence_petition)
    modules = Module.objects.filter(start_module__range=(petition.time_start_petition,petition.time_finish_petition)).order_by('start_module')
    #event_dates = [date_start + timedelta(days=x) for x in range((date_finish-date_start).days + 1) if (date_start + timedelta(days=x)).weekday() == time.strptime(weekDay, '%w').tm_wday]
    event_dates = []
    while date_current < date_finish:
        if date_current.weekday() == time.strptime(weekDay, '%w').tm_wday or recurrence_petition == 1:
            event_dates.append(date_current)
            date_current = date_current + timedelta(days=recurrence_petition)
        else:
            date_current = date_current + timedelta(days=1)
    module_events = []
    for ed in event_dates:
        for m in modules:
           module_events.append(ModuleEvent(petition=petition, module=m, day=ed))
    ModuleEvent.objects.bulk_create(module_events)
    return False

def delete_event(petition):
    ModuleEvent.objects.filter(petition=petition).delete()

def report_data(request):
    template_name = "report_data.html"
    context = {}
    event_count = {}
    taza = {}
    totalmodule = 0
    selectdate = datetime.today().strftime("%d/%m/%Y")
    selectdate2 = datetime.today().strftime("%d/%m/%Y")
    campus_list = Campus.objects.all().order_by('name')
    campus_select = Campus.objects.all().order_by('name')
    if request.POST:
        selectedcampus = request.POST['selectedcampus']
        selectdate = datetime.strptime(request.POST['selecteddate'], "%d/%m/%Y").date()
        selectdate2 = datetime.strptime(request.POST['selecteddate2'], "%d/%m/%Y").date()
        modulevent = ModuleEvent.objects.filter(day__range=[selectdate, selectdate2]).order_by('day')
        if selectedcampus != 'all':
            campus_select = Campus.objects.filter(id=selectedcampus).order_by('name')
            modulevent = ModuleEvent.objects.filter(day__range=[selectdate, selectdate2], petition__room_petition__campus=selectedcampus).order_by('day')
    else:
        selectdate = datetime.strptime(selectdate, "%d/%m/%Y").date()
        selectdate2 = datetime.strptime(selectdate2, "%d/%m/%Y").date()
        modulevent = ModuleEvent.objects.filter(day__range=[selectdate, selectdate2]).order_by('day')
    totalevent = modulevent.count()
    for dt in daterange(selectdate, selectdate2):
        if dt.weekday() != 6:
            totalmodule=totalmodule+1
    totalmodule_range = totalmodule * Module.objects.all().count()
    room_list = Room.objects.all().order_by('campus', 'room_name')
    for r in room_list:
        num = ModuleEvent.objects.filter(day__range=[selectdate, selectdate2], petition__room_petition=r).count()
        if num == 0:
            result = 0
        else:
            result =  round(Module.objects.all().count() / num,3)
        taza[r.id] = result
        event_count[r.id] = ModuleEvent.objects.filter(day__range=[selectdate, selectdate2], petition__room_petition=r).count()
    context['taza'] = taza
    context['event_count'] = event_count
    context['totalevent'] = totalevent
    context['totalmodule_range'] = totalmodule_range
    context['selectdate2'] = selectdate2
    context['selectdate'] = selectdate
    context['campus_list'] = campus_list
    context['campus_select'] = campus_select
    context['room_list'] = room_list
    context['modulevent'] = modulevent
    return render(request, template_name, context)

def daterange(date1, date2):
    for n in range(int ((date2 - date1).days)+1):
        yield date1 + timedelta(n)

def reserve_room(request):
    template_name = "reserve_room.html"
    context = {}
    campusobj = Campus.objects.all()
    modulestart_choice = []
    modulefinish_choice = []
    for o in Module.objects.all().order_by('start_module'):
        modulestart_choice.append((o.start_module, str(o)))
        modulefinish_choice.append((o.finish_module, str(o)))

    formroom = RoomPetitionForm(modulestart_choice, modulefinish_choice,request.POST or None, initial={'status_petition':'P'})
    context['campusobj'] = campusobj
    context['formroom'] = formroom
    if request.method == 'POST':
        if formroom.is_valid():
            formroom.save()
            return HttpResponseRedirect(reverse('calendar_day'))
    return render(request, template_name, context)