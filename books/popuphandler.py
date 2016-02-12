from django.utils.html import escape
from django.shortcuts import render_to_response
from django.http import HttpResponse
from django import forms


def handle_pop_add(request, addForm, field):
    if request.method == "POST":
        form = addForm(request.POST)
        if form.is_valid():
            try:
                new_object = form.save()
            except forms.ValidationError:
                new_object = None
            if new_object:
                return HttpResponse(
                    '<script type="text/javascript">'
                    'opener.dismissAddAnotherPopup(window, "%s", "%s");'
                    '</script>' %
                    (escape(new_object._get_pk_val()), escape(new_object)))

    else:
        form = addForm()

    page_context = {'form': form, 'field': field}
    return render_to_response("popupadd.html", page_context)
