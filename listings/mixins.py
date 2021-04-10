from django.shortcuts import redirect
from django.contrib import messages
from django.http import HttpResponse
import json


class OwnerShipMixin:
    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if request.user == obj.owner:
            return super().dispatch(request, *args, **kwargs)
        else:
            messages.error(
                request, ('You are not allowed to modify this Post'))
            return redirect('accounts:dashboard')
