from django.contrib import admin
from django.core import serializers

from .models import InteractionType, Interaction2, InteractionCategory, Results
from aklub.models import Event

import nested_admin


@admin.register(InteractionType)
class InteractionTypeAdmin(admin.ModelAdmin):
    pass


@admin.register(Interaction2)
class InteractionsAdmin(admin.ModelAdmin):
    def change_view(self, request, object_id, form_url='', extra_context=None):
        data = {}
        data['display_fields'] = serializers.serialize('json', InteractionType.objects.all())
        data['required_fields'] = [field.name for field in Interaction2._meta.get_fields() if not field.null]
        return super().change_view(request, object_id, form_url, extra_context=data,)

    def add_view(self, request, form_url='', extra_context=None):
        data = {}
        data['display_fields'] = serializers.serialize('json', InteractionType.objects.all())
        data['required_fields'] = [field.name for field in Interaction2._meta.get_fields() if not field.null]
        return super().add_view(request, form_url, extra_context=data,)


@admin.register(InteractionCategory)
class InteractionCategoryAdmin(admin.ModelAdmin):
    pass


@admin.register(Results)
class ResultsAdmin(admin.ModelAdmin):
    pass


class InteractionInline(nested_admin.NestedTabularInline):
    model = Interaction2
    extra = 0
    can_delete = True
    show_change_link = True
    #readonly_fields = ('type', 'created_by', 'handled_by',)
    fk_name = 'user'
    """
    def get_queryset(self, request):
        qs = super(InteractionInline, self).get_queryset(request)
        qs = qs.filter(type__in=('individual', 'auto')).order_by('-date')
        qs = qs.select_related('created_by', 'handled_by')
        return qs
    """
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "event":
            if not request.user.has_perm('aklub.can_edit_all_units'):
                kwargs["queryset"] = Event.objects.filter(administrative_units__in=request.user.administrated_units.all())
            else:
                kwargs["queryset"] = Event.objects.all()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)