from django.shortcuts import redirect


def get_redirect_short_link(request, pk):
    return redirect(f'/recipes/{pk}/')
