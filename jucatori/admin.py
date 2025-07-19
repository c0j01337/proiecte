from django.contrib import admin
from .models import Jucator, Producator, Categorie, Racheta, ImagineRacheta, Cos, ItemCos

class JucatorAdmin(admin.ModelAdmin):
    list_display = ('nume_complet', 'nationalitate', 'clasament_atp', 'varsta')  # 'ranking' → 'clasament_atp'
    list_filter = ('nationalitate',)
    search_fields = ('nume_complet', 'nationalitate')
    fieldsets = (
        ('Informații personale', {
            'fields': ('nume_complet', 'nationalitate', 'varsta')
        }),
        ('Carieră', {
            'fields': ('clasament_atp', 'debut_profesionist', 'titluri_castigate', 'premii_bani_anul_curent', 'premii_bani_total')
        }),
        ('Date fizice', {
            'fields': ('stil_joc', 'greutate_kg', 'inaltime_cm', 'racheta_partener')
        }),
        ('Fotografii', {
            'fields': ('imagine_principala', 'img1', 'img2', 'img3')
        }),
    )

admin.site.register(Jucator, JucatorAdmin)

class ImagineRachetaInline(admin.TabularInline):
    model = ImagineRacheta
    extra = 3

class RachetaAdmin(admin.ModelAdmin):
    list_display = ('nume', 'producator', 'categorie', 'pret', 'pret_redus', 'stoc', 'in_stoc', 'featured')
    list_filter = ('producator', 'categorie', 'in_stoc', 'featured')
    search_fields = ('nume', 'producator__nume', 'descriere')
    prepopulated_fields = {'slug': ('nume',)}
    inlines = [ImagineRachetaInline]
    fieldsets = (
        ('Informații de bază', {
            'fields': ('nume', 'slug', 'producator', 'categorie', 'imagine_principala', 'imagine_secundara', 'imagine_tertiara')
        }),
        ('Prețuri și stoc', {
            'fields': ('pret', 'pret_redus', 'stoc', 'in_stoc')
        }),
        ('Descrieri', {
            'fields': ('descriere_scurta', 'descriere', 'specificatii')
        }),
        ('Specificații tehnice', {
            'fields': ('greutate', 'marime_cap', 'lungime', 'balans', 'tip_corzi')
        }),
        ('Opțiuni', {
            'fields': ('featured',)
        }),
    )

class ItemCosInline(admin.TabularInline):
    model = ItemCos
    extra = 0

class CosAdmin(admin.ModelAdmin):
    list_display = ('id', 'id_sesiune', 'data_creare', 'total', 'numar_produse')
    inlines = [ItemCosInline]

admin.site.register(Producator)
admin.site.register(Categorie)
admin.site.register(Racheta, RachetaAdmin)
admin.site.register(ImagineRacheta)
admin.site.register(Cos, CosAdmin)
admin.site.register(ItemCos)