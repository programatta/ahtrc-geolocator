from django.shortcuts import render
from django.views.generic import TemplateView
from apps.classicauthor.models import ClassicAuthor
from apps.author.models import LiteraryWork


# Create your views here.
class HomePageView(TemplateView):
    template_name='front/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['classicAuthors'] = self._load_classic_data()
        context['literaryWorks'] = self._load_literary_works_data()
        return context

    def _load_classic_data(self):
        return ClassicAuthor.objects.exclude(name='SIN ASIGNAR')

    def _load_literary_works_data(self):
        return LiteraryWork.objects.select_related(
            'author', 'classic_author', 'genre'
        ).prefetch_related('link_literarywork').all()
