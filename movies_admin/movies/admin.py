from django.contrib import admin
from .models import Genre, Filmwork, GenreFilmwork, Person, PersonFilmwork


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    search_fields = ('name',)


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    search_fields = ('full_name',)


class GenreFilmworkInline(admin.TabularInline):
    model = GenreFilmwork
    autocomplete_fields = ('genre', 'film_work',)
    # list_display = (
    #     'get_genres',
    # )
    # list_prefetch_related = (..., 'genres')
    #
    # def get_queryset(self, request):
    #     queryset = (
    #         super()
    #         .get_queryset(request)
    #         .prefetch_related(*self.list_prefetch_related)
    #     )
    #     return queryset
    #
    # def get_genres(self, obj):
    #     return ','.join([genre.name for genre in obj.genres.all()])
    #
    # get_genres.short_description = 'Жанры фильма'

class PersonFilmworkInline(admin.TabularInline):
    model = PersonFilmwork
    autocomplete_fields = ('person', 'film_work',)


@admin.register(Filmwork)
class FilmworkAdmin(admin.ModelAdmin):
    inlines = (GenreFilmworkInline, PersonFilmworkInline)

    # Отображение полей в списке
    list_display = ('title', 'type', 'creation_date', 'rating',)

    # Фильтрация в списке
    list_filter = ('type', 'rating',)

    # Поиск по полям
    search_fields = ('title', 'description', 'id',)
