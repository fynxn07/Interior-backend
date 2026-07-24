import django_filters
from .models import Project


class ProjectFilter(django_filters.FilterSet):
    category = django_filters.CharFilter(field_name="category", lookup_expr="iexact")
    featured = django_filters.BooleanFilter(field_name="featured")

    class Meta:
        model = Project
        fields = ["category", "featured"]