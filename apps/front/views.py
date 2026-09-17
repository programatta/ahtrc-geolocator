from django.shortcuts import render
from django.views.generic import TemplateView
from apps.classicauthor.models import ClassicAuthor
from apps.author.models import Author, LiteraryWork
from .models import MapConfig


# Create your views here.
class HomePageView(TemplateView):

    def _is_map_open(self):
        if not hasattr(self, '_map_open'):
            self._map_open = MapConfig.load().is_open
        return self._map_open

    def get_template_names(self):
        return ['front/home.html'] if self._is_map_open() else ['front/landing.html']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if not self._is_map_open():
            return context
        context['classicAuthors'] = self._load_classic_data()
        context['literaryWorks'] = self._load_literary_works_data()
        context['totals'] = self._load_totals_data()
        return context

    def _load_classic_data(self):
        return ClassicAuthor.objects.exclude(is_unassigned=True)

    def _load_literary_works_data(self):
        return LiteraryWork.objects.select_related(
            'author', 'classic_author', 'genre'
        ).prefetch_related('link_literarywork').all()

    def _load_totals_data(self):
        totals = {}
        totals['authorCount'] = Author.objects.count()
        totals['literaryworkCount'] = LiteraryWork.objects.filter(location__isnull=False).count()
        totals['classicauthorCount'] = ClassicAuthor.objects.exclude(is_unassigned=True).count()
        return totals
