from django import forms
from django.forms import fields
from datetime import date, datetime
from django.forms.widgets import DateInput, DateTimeInput, EmailInput, NumberInput, Select, TextInput, TimeInput
from apps.schedules.models import RoomPetition, Module, ModuleEvent
from apps.core.models import Room
from django.forms import ModelForm, Textarea
from datetime import date, timedelta, datetime
import time 

class RoomPetitionForm(forms.ModelForm):
    
    class Meta:
        model = RoomPetition
        fields = [
            'event_petition',
            'name_petition',
            'email_petition',
            'room_petition',
            'computer_petition',
            'date_start_petition',
            'date_finish_petition',
            'time_start_petition',
            'time_finish_petition',
            'day_petition',
            'recurrence_petition',
            'memo_petition',
            'type_petition',
            #'status_petition',
            #'datetime_petition',
        ]
        labels = {
            'event_petition':'Nombre del evento:',
            'name_petition':'Nombre del usuario:',
            'email_petition':'Email:',
            'room_petition':'Sala:',
            'computer_petition':'Computadores:',
            'date_start_petition':'Fecha inicio y final:',
            'date_finish_petition':'Fecha inicio y final:',
            'day_petition':'Día:',
            'recurrence_petition':'Recurrencia:',
            'memo_petition':'Mensaje:',
            'type_petition':'Tipo de evento:',
            #'status_petition':'Status:',
            #'datetime_petition':'Dia y hora de la petición:',
        }
        widgets={
            'event_petition':TextInput(attrs={'class':'form-control', 'id':'kt_maxlength_8', 'placeholder':'Ej: NRC7777'}),
            'name_petition':TextInput(attrs={'class':'form-control', 'id':'kt_maxlength_9', 'placeholder':'Ej: Juan Antonio Silva'}),
            'email_petition':EmailInput(attrs={'class':'form-control', 'id':'kt_maxlength_10', 'placeholder':'Ej: Juan@uandresbello.edu'}),
            'room_petition':Select(attrs={'class':'form-control selectpicker'}),
            'computer_petition':NumberInput(attrs={'class':'form-control', 'id':'kt_touchspin_1', 'placeholder':'Ej: 15'}),
            'date_start_petition':DateInput(attrs={'class':'form-control datetimepicker-input', 'id':'kt_datepicker_7', 'data-date-format':'dd/mm/yyyy', 'readonly':'readonly', 'placeholder':'01/01/2022'}),
            'date_finish_petition':DateInput(attrs={'class':'form-control datetimepicker-input', 'id':'kt_datepicker_7', 'data-date-format':'dd/mm/yyyy', 'readonly':'readonly', 'placeholder':'02/01/2022'}),
            'day_petition':Select(attrs={'class':'form-control selectpicker'}),
            'recurrence_petition':Select(attrs={'class':'form-control selectpicker'}),
            'memo_petition':Textarea(attrs={'class':'form-control', 'cols':30, 'rows':3, 'id':'kt_maxlength_11', 'maxlength':'100', 'placeholder':'Ej: Necesario para hacer una prueba'}),
            'type_petition':Select(attrs={'class':'form-control selectpicker'}),
            #'status_petition':Select(attrs={'class':'form-control selectpicker'}),
            #'datetime_petition':DateTimeInput(attrs={'class':'form-control datetimepicker-input'}),
        }
    def __init__(self, modulestart_choice, modulefinish_choice, *args, **kwargs):
        super(RoomPetitionForm, self).__init__(*args,**kwargs)
        self.initial['day_petition'] = '3'
        #self.initial['status_petition'] = 'P'
        self.fields['date_start_petition'].input_formats=[ '%d/%m/%Y' ]
        self.fields['date_finish_petition'].input_formats=[ '%d/%m/%Y' ]
        self.fields['time_start_petition'] = forms.ChoiceField(choices=modulestart_choice, label='Hora inicio:', widget=forms.Select(attrs={'class':'form-control selectpicker'}))
        self.fields['time_finish_petition'] = forms.ChoiceField(choices=modulefinish_choice, label='Hora termino:', widget=forms.Select(attrs={'class':'form-control selectpicker'}))
        #self.fields['room_petition'].widget.choices(get_room_by_filter())
    
    def clean(self):
        super(RoomPetitionForm, self).clean()
        event_petition = self.cleaned_data.get('event_petition')
        name_petition = self.cleaned_data.get('name_petition')
        email_petition = self.cleaned_data.get('email_petition')
        computer_petition = self.cleaned_data.get('computer_petition')
        date_start_petition = self.cleaned_data.get('date_start_petition')
        date_finish_petition = self.cleaned_data.get('date_finish_petition')
        time_start_petition = self.cleaned_data.get('time_start_petition')
        time_finish_petition = self.cleaned_data.get('time_finish_petition')
        day_petition = self.cleaned_data.get('day_petition')
        recurrence_petition = self.cleaned_data.get('recurrence_petition')
        memo_petition = self.cleaned_data.get('memo_petition')
        room_petition = self.cleaned_data.get('room_petition') # if self.cleaned_data.get('room_petition') is not None else get_room_by_filter(efefef,rdfgdfg)
        type_petition = self.cleaned_data.get('type_petition')
        #status_petition = self.cleaned_data.get('status_petition')
        if len(event_petition) < 3:
            self.fields['event_petition'].widget.attrs.update({'class':'form-control is-invalid'})
            self._errors['event_petition'] = self.error_class(['Nombre de evento minimo de 3 letras'])
        else:
            self.fields['event_petition'].widget.attrs.update({'class':'form-control is-valid'})
        if len(name_petition) < 3:
            self.fields['name_petition'].widget.attrs.update({'class':'form-control is-invalid'})
            self._errors['name_petition'] = self.error_class(['Nombre de usuario minimo de 3 letras'])
        else:
            self.fields['name_petition'].widget.attrs.update({'class':'form-control is-valid'})
        if len(email_petition) < 6:
            self.fields['email_petition'].widget.attrs.update({'class':'form-control is-invalid'})
            self._errors['email_petition'] = self.error_class(['Email invalido'])
        else:
            self.fields['email_petition'].widget.attrs.update({'class':'form-control is-valid'})
        if date_start_petition is None:
            self.fields['date_start_petition'].widget.attrs.update({'class':'form-control datetimepicker-input is-invalid'})
            self._errors['date_start_petition'] = self.error_class(['Elija una fecha de inicio valida'])
        else:
            self.fields['date_start_petition'].widget.attrs.update({'class':'form-control datetimepicker-input is-valid'})
        if date_finish_petition is None:
            self.fields['date_finish_petition'].widget.attrs.update({'class':'form-control datetimepicker-input is-invalid'})
            self._errors['date_finish_petition'] = self.error_class(['Elija una fecha de termino valida'])
        else:
            self.fields['date_finish_petition'].widget.attrs.update({'class':'form-control datetimepicker-input is-valid'})
        if time_start_petition > time_finish_petition:
            self._errors['time_finish_petition'] = self.error_class(['Modulo inicial ocurre despues del modulo final'])
        if len(memo_petition) < 4:
            self.fields['memo_petition'].widget.attrs.update({'class':'form-control is-invalid'})
            self._errors['memo_petition'] = self.error_class(['El mensaje debe tener al menos 4 letras'])
        else:
            self.fields['memo_petition'].widget.attrs.update({'class':'form-control is-valid'})
        if room_petition is None:
            self._errors['room_petition'] = self.error_class(['Ingrese una sala valida'])
        return self.cleaned_data
    
class StatusRoomPetitionForm(forms.ModelForm):
    class Meta:
        model = RoomPetition
        fields = ['status_petition',]
        labels = {'status_petition':'Status:',}
        widgets={'status_petition':Select(attrs={'class':'form-control selectpicker'}),}

class ModuleForm(forms.ModelForm):
    class Meta:
        model = Module
        fields = [ 
            'resume_module',
            'name_module',
            'start_module',
            'finish_module',
        ]
        labels = {
            'resume_module':'Identificador',
            'name_module':'Nombre',
            'start_module':'Hora de inicio',
            'finish_module':'Hora de termino',
        }
        widgets={
            'resume_module':TextInput(attrs={'class':'form-control', 'placeholder':'Ej: 1D'}),
            'name_module':TextInput(attrs={'class':'form-control', 'placeholder':'Ej: Módulo 1 Diurno'}),
            'start_module':TimeInput(attrs={'class':'form-control', 'readonly':'readonly', 'id':'kt_timepicker_5', 'placeholder':'Ej: 08:00'}),
            'finish_module':TimeInput(attrs={'class':'form-control', 'readonly':'readonly', 'id':'kt_timepicker_5', 'placeholder':'Ej: 09:00'}),
        }
