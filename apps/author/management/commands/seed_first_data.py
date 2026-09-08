import csv
from django.contrib.gis.geos import GEOSGeometry
from django.core.management.base import BaseCommand
from apps.classicauthor.models import ClassicAuthor
from apps.author.models import Author, LiteraryWork,Link, Imagen
from apps.genre.models import Genre


class Command(BaseCommand):
    help = "Update kams zipcode by province."

    def add_arguments(self, parser):
        parser.add_argument('csv', type=str)

    def handle(self, *args, **kwargs):
        print('start process...')

        csv_path = kwargs['csv']
        csv_file = open(csv_path, 'r')
        csv_reader = csv.DictReader(csv_file, delimiter=';')

        row_count = 0
        for row in csv_reader:
            print(row)
            self.__process_row(row)
            row_count += 1

        print('row_count: ', row_count)

        print('end process.')

    def __process_row(self, row):
        classic_author_str = row['autorclasico']
        author_str = row['autoractual']
        literary_work_str = row['obra']
        description_str = row['descripcion']
        links_str = row['enlaces']
        images_str = row['urlimagen']
        lon_str = row['longitud']
        lat_str = row['latitud']

        #Autor clasico.
        try:
            classic_author = ClassicAuthor.objects.get(name=classic_author_str.capitalize())
        except ClassicAuthor.DoesNotExist:
            classic_author = ClassicAuthor.objects.get(name='SIN ASIGNAR')

        #Autor.
        author_str_items = author_str.split(' ')
        try:
            author = Author.objects.get(first_name=author_str_items[0])
        except Author.DoesNotExist:
            first_name = author_str_items[0]
            if len(author_str_items)>1:
                last_name = ' '.join(author_str_items[1:])
            else:
                last_name = '-'
            author = Author.objects.create(first_name=first_name, last_name=last_name)

        #Genero.
        genre = Genre.objects.get(name='SIN ASIGNAR')

        #Datos de la obra.
        pnt = GEOSGeometry(f"POINT({lon_str} {lat_str})")
        literary_work = LiteraryWork.objects.create(
            classic_author=classic_author,
            author=author,
            title=literary_work_str,
            genre=genre,
            description=description_str,
            location=pnt
        )

        #enlaces asociados.
        if links_str.strip():
            for link_str in links_str.split(','):
                link_str = link_str.strip()
                if link_str:
                    Link.objects.create(literary_work=literary_work, link=link_str)

        #imagenes asociadas.
        if images_str.strip():
            for image_str in images_str.split(','):
                image_str = image_str.strip()
                if image_str:
                    Imagen.objects.create(literary_work=literary_work, link=image_str)
