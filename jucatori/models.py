from django.db import models
from django.utils.text import slugify

class Jucator(models.Model):
    id = models.AutoField(primary_key=True)
    nume_complet = models.CharField(max_length=100)
    nationalitate = models.CharField(max_length=50)
    titluri_castigate = models.IntegerField(default=0)
    premii_bani_anul_curent = models.IntegerField(default=0, help_text='Premii în bani anul curent ($)')
    premii_bani_total = models.IntegerField(default=0, help_text='Total premii în bani ($)')
    debut_profesionist = models.IntegerField(help_text='Anul debutului profesionist')
    varsta = models.IntegerField()
    clasament_atp = models.IntegerField()
    stil_joc = models.CharField(max_length=300)
    greutate_kg = models.IntegerField()
    inaltime_cm = models.IntegerField()
    racheta_partener = models.CharField(max_length=100)
    
    # Imagini păstrate din modelul anterior
    imagine_principala = models.ImageField(upload_to='jucatori/', blank=True, null=True)
    img1 = models.ImageField(upload_to='jucatori/galerie/', blank=True, null=True)
    img2 = models.ImageField(upload_to='jucatori/galerie/', blank=True, null=True)
    img3 = models.ImageField(upload_to='jucatori/galerie/', blank=True, null=True)
    
    def __str__(self):
        return self.nume_complet
    
class Producator(models.Model):
    nume = models.CharField(max_length=100)
    descriere = models.TextField(blank=True, null=True)
    logo = models.ImageField(upload_to='producatori/', blank=True, null=True)
    
    class Meta:
        verbose_name_plural = "Producători"
    
    def __str__(self):
        return self.nume

class Categorie(models.Model):
    nume = models.CharField(max_length=100)
    descriere = models.TextField(blank=True, null=True)
    
    class Meta:
        verbose_name_plural = "Categorii"
    
    def __str__(self):
        return self.nume

class Racheta(models.Model):
    nume = models.CharField(max_length=200)
    slug = models.SlugField(max_length=250, unique=True, blank=True)
    producator = models.ForeignKey(Producator, on_delete=models.CASCADE, related_name='rachete')
    categorie = models.ForeignKey(Categorie, on_delete=models.SET_NULL, null=True, blank=True, related_name='rachete')
    pret = models.DecimalField(max_digits=10, decimal_places=2)
    pret_redus = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    descriere_scurta = models.CharField(max_length=255, blank=True)
    descriere = models.TextField()
    specificatii = models.TextField(blank=True)
    greutate = models.CharField(max_length=50, blank=True, null=True)
    marime_cap = models.CharField(max_length=50, blank=True, null=True)
    lungime = models.CharField(max_length=50, blank=True, null=True)
    balans = models.CharField(max_length=50, blank=True, null=True)
    tip_corzi = models.CharField(max_length=100, blank=True, null=True)
    stoc = models.IntegerField(default=0)
    imagine_principala = models.ImageField(upload_to='rachete/')
    imagine_secundara = models.ImageField(upload_to='rachete/', blank=True, null=True)
    imagine_tertiara = models.ImageField(upload_to='rachete/', blank=True, null=True)
    data_adaugare = models.DateTimeField(auto_now_add=True)
    in_stoc = models.BooleanField(default=True)
    featured = models.BooleanField(default=False)
    
    class Meta:
        verbose_name_plural = "Rachete"
        ordering = ['-data_adaugare']
    
    def __str__(self):
        return f"{self.producator.nume} {self.nume}"
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.producator.nume}-{self.nume}")
        super().save(*args, **kwargs)
    
    def are_reducere(self):
        return self.pret_redus is not None and self.pret_redus < self.pret
    
    def pret_final(self):
        if self.are_reducere():
            return self.pret_redus
        return self.pret
    
    def procent_reducere(self):
        if self.are_reducere():
            reducere = ((self.pret - self.pret_redus) / self.pret) * 100
            return int(reducere)
        return 0

class ImagineRacheta(models.Model):
    racheta = models.ForeignKey(Racheta, on_delete=models.CASCADE, related_name='imagini')
    imagine = models.ImageField(upload_to='rachete_imagini/')
    este_principala = models.BooleanField(default=False)
    ordine = models.IntegerField(default=0)
    
    class Meta:
        verbose_name_plural = "Imagini Rachete"
        ordering = ['ordine']
    
    def __str__(self):
        return f"Imagine pentru {self.racheta.nume}"

class Cos(models.Model):
    id_sesiune = models.CharField(max_length=100)
    data_creare = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "Coșuri"
    
    def __str__(self):
        return f"Coș {self.id}"
    
    def total(self):
        return sum(item.subtotal() for item in self.items.all())
    
    def numar_produse(self):
        return sum(item.cantitate for item in self.items.all())

class ItemCos(models.Model):
    cos = models.ForeignKey(Cos, on_delete=models.CASCADE, related_name='items')
    racheta = models.ForeignKey(Racheta, on_delete=models.CASCADE)
    cantitate = models.IntegerField(default=1)
    data_adaugare = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "Itemi Coș"
    
    def __str__(self):
        return f"{self.cantitate} x {self.racheta.nume}"
    
    def subtotal(self):
        return self.racheta.pret_final() * self.cantitate


