from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.db.models import Q 
from .models import Jucator, Racheta, Producator, Categorie, Cos, ItemCos
import uuid
from django.utils import timezone
from datetime import timedelta

def welcome_page(request):
    return render(request, 'jucatori/welcome.html')

def lista_jucatori(request):
    # Verificăm dacă există un filtru pentru rachetă
    racheta_filter = request.GET.get('racheta', None)
    
    # Aplicăm filtrul dacă există
    if racheta_filter:
        jucatori = Jucator.objects.filter(racheta_partener=racheta_filter).order_by('clasament_atp')
    else:
        jucatori = Jucator.objects.all().order_by('clasament_atp')
    
    return render(request, 'jucatori/lista_jucatori.html', {
        'jucatori': jucatori,
        'selected_filter': racheta_filter  # Transmitem filtrul selectat către template
    })

def detalii_jucator(request, jucator_id):
    jucator = get_object_or_404(Jucator, id=jucator_id)
    return render(request, 'jucatori/detalii_jucator.html', {'jucator': jucator})

def cauta_jucator(request):
    query = request.GET.get('q', '').strip()
    # Adăugăm și preluarea filtrului de rachetă pentru a menține filtrul în căutări
    racheta_filter = request.GET.get('racheta', None)
   
    if query:
        # Debug: print the query to console to check
        print(f"Searching for: '{query}'")
       
        # Get all players first (for debugging)
        all_players = Jucator.objects.all()
        print(f"Total players in database: {all_players.count()}")
        for player in all_players:
            print(f"DB Player: {player.nume_complet}, ID: {player.id}")
       
        # Adăugăm condiția de filtru pentru rachetă dacă există
        base_query = Q(nume_complet__icontains=query) | Q(nationalitate__icontains=query)
        
        if racheta_filter:
            rezultate = Jucator.objects.filter(base_query & Q(racheta_partener=racheta_filter))
        else:
            rezultate = Jucator.objects.filter(base_query)
       
        # Debug: print search results
        print(f"Search results count: {rezultate.count()}")
        for player in rezultate:
            print(f"Found: {player.nume_complet}")
       
        # Check for similar names (in case of typos)
        if not rezultate.exists():
            # Try more lenient search with each word in the query
            words = query.split()
            query_conditions = Q()
            for word in words:
                if len(word) > 2:  # Only use words with more than 2 characters
                    query_conditions |= Q(nume_complet__icontains=word)
           
            if query_conditions:
                # Aplicăm și aici filtrul de rachetă dacă există
                if racheta_filter:
                    rezultate = Jucator.objects.filter(query_conditions & Q(racheta_partener=racheta_filter))
                else:
                    rezultate = Jucator.objects.filter(query_conditions)
                print(f"Lenient search results: {rezultate.count()}")
       
        # Redirect if there's exactly one match
        if rezultate.count() == 1:
            return redirect('detalii_jucator', jucator_id=rezultate.first().id)
       
        # Otherwise show the results
        return render(request, 'jucatori/lista_jucatori.html', {
            'jucatori': rezultate,
            'query': query,
            'rezultate_count': rezultate.count(),
            'selected_filter': racheta_filter  # Trimitem și filtrul selectat
        })
   
    # Default la filtrarea doar după rachetă dacă nu există query
    if racheta_filter:
        jucatori = Jucator.objects.filter(racheta_partener=racheta_filter).order_by('clasament_atp')
    else:
        # Default to showing all players
        jucatori = Jucator.objects.all().order_by('clasament_atp')
    
    return render(request, 'jucatori/lista_jucatori.html', {
        'jucatori': jucatori,
        'selected_filter': racheta_filter
    })

def get_cos_id(request):
    if 'cos_id' not in request.session:
        request.session['cos_id'] = str(uuid.uuid4())
    return request.session['cos_id']

def magazin_rachete(request):
    producator_id = request.GET.get('producator')
    categorie_id = request.GET.get('categorie')
    sortare = request.GET.get('sortare', 'nume')
    query = request.GET.get('q')
    
    rachete = Racheta.objects.filter(in_stoc=True)
    
    if producator_id:
        rachete = rachete.filter(producator_id=producator_id)
    
    if categorie_id:
        rachete = rachete.filter(categorie_id=categorie_id)
    
    if query:
        rachete = rachete.filter(nume__icontains=query)
    
    if sortare == 'pret_crescator':
        rachete = rachete.order_by('pret')
    elif sortare == 'pret_descrescator':
        rachete = rachete.order_by('-pret')
    elif sortare == 'noutati':
        rachete = rachete.order_by('-data_adaugare')
    else:
        rachete = rachete.order_by('nume')
    
    producatori = Producator.objects.all()
    categorii = Categorie.objects.all()
    
    context = {
        'rachete': rachete,
        'producatori': producatori,
        'categorii': categorii,
        'selected_producator': producator_id,
        'selected_categorie': categorie_id,
        'selected_sortare': sortare,
        'query': query
    }
    
    return render(request, 'magazin/magazin_rachete.html', context)

def detalii_racheta(request, slug):
    racheta = get_object_or_404(Racheta, slug=slug)
    rachete_similare = Racheta.objects.filter(producator=racheta.producator).exclude(id=racheta.id)[:4]
    
    context = {
        'racheta': racheta,
        'rachete_similare': rachete_similare
    }
    
    return render(request, 'magazin/detalii_racheta.html', context)

@require_POST
def adauga_in_cos(request):
    racheta_id = request.POST.get('racheta_id')
    cantitate = int(request.POST.get('cantitate', 1))
    
    if cantitate <= 0:
        return JsonResponse({'error': 'Cantitatea trebuie să fie un număr pozitiv'}, status=400)
    
    racheta = get_object_or_404(Racheta, id=racheta_id)
    
    # Verificăm stocul
    if cantitate > racheta.stoc:
        return JsonResponse({'error': f'Doar {racheta.stoc} bucăți disponibile'}, status=400)
    
    cos_id = get_cos_id(request)
    cos, created = Cos.objects.get_or_create(id_sesiune=cos_id)
    
    # Verificăm dacă produsul există deja în coș
    item_cos, item_created = ItemCos.objects.get_or_create(
        cos=cos,
        racheta=racheta,
        defaults={'cantitate': 0}
    )
    
    # Actualizăm cantitatea
    if not item_created:
        item_cos.cantitate += cantitate
    else:
        item_cos.cantitate = cantitate
    
    item_cos.save()
    
    return JsonResponse({
        'success': True,
        'mesaj': f'{racheta.nume} a fost adăugat în coș',
        'numar_produse': cos.numar_produse()
    })

def vizualizare_cos(request):
    cos_id = get_cos_id(request)
    cos, created = Cos.objects.get_or_create(id_sesiune=cos_id)
    
    context = {
        'cos': cos
    }
    
    return render(request, 'cos.html', context)

@require_POST
def actualizeaza_cos(request):
    racheta_id = request.POST.get('racheta_id')
    cantitate = int(request.POST.get('cantitate', 0))
    
    cos_id = get_cos_id(request)
    cos = get_object_or_404(Cos, id_sesiune=cos_id)
    
    try:
        item = ItemCos.objects.get(cos=cos, racheta_id=racheta_id)
        
        if cantitate <= 0:
            item.delete()
            mesaj = "Produsul a fost eliminat din coș"
        else:
            racheta = item.racheta
            if cantitate > racheta.stoc:
                return JsonResponse({'error': f'Doar {racheta.stoc} bucăți disponibile'}, status=400)
                
            item.cantitate = cantitate
            item.save()
            mesaj = "Cantitatea a fost actualizată"
            
        return JsonResponse({
            'success': True,
            'mesaj': mesaj,
            'numar_produse': cos.numar_produse(),
            'total': float(cos.total())
        })
    except ItemCos.DoesNotExist:
        return JsonResponse({'error': 'Produsul nu există în coș'}, status=404)

@require_POST
def elimina_din_cos(request):
    racheta_id = request.POST.get('racheta_id')
    
    cos_id = get_cos_id(request)
    cos = get_object_or_404(Cos, id_sesiune=cos_id)
    
    try:
        item = ItemCos.objects.get(cos=cos, racheta_id=racheta_id)
        item.delete()
        
        return JsonResponse({
            'success': True,
            'mesaj': "Produsul a fost eliminat din coș",
            'numar_produse': cos.numar_produse(),
            'total': float(cos.total())
        })
    except ItemCos.DoesNotExist:
        return JsonResponse({'error': 'Produsul nu există în coș'}, status=404)
    
def abonamente(request):
    """Pagina principală cu opțiunile de abonamente"""
    return render(request, 'magazin/abonamente.html')

def abonament_formular(request, tip):
    """Formular pentru selectarea unui abonament specific"""
    if tip not in ['basic', 'premium']:
        # Redirectare în cazul unui tip nevalid
        return redirect('abonamente')
    
    context = {
        'tip': tip
    }
    return render(request, 'magazin/abonament_formular.html', context)

def procesare_plata(request):
    """Procesează datele de plată și redirecționează către pagina de confirmare"""
    if request.method == 'POST':
        # Aici ar fi logica de procesare a plății cu un serviciu real
        # De exemplu integrare cu Stripe, PayPal etc.
        
        # Pentru demo, doar extragem datele din formular
        tip_abonament = request.POST.get('tip_abonament')
        email = request.POST.get('email')
        
        # Generăm un ID de comandă
        id_comanda = str(uuid.uuid4())[:8].upper()
        
        # Calculăm data următoarei facturări
        data_urmatoare = timezone.now() + timedelta(days=30)
        data_urmatoare_facturare = data_urmatoare.strftime('%d/%m/%Y')
        
        context = {
            'tip_abonament': tip_abonament,
            'email': email,
            'id_comanda': id_comanda,
            'data_urmatoare_facturare': data_urmatoare_facturare
        }
        
        return render(request, 'magazin/confirmare_plata.html', context)
    
    # Dacă nu e POST, redirectăm la pagina de abonamente
    return redirect('abonamente')