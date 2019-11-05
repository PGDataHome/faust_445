#! /usr/bin/env python3

"""

Votre mission

Ça y est, votre application décolle ! À vous la gloire, le succès et les smoothies aux fruits frais ! Mais avant d'appeler votre banque pour la convaincre de vous prêter de quoi acheter le yacht de vos rêves, il va falloir mettre en place un système d'analytics pour mesurer le nombre de visites de votre site.
Objectif

Dans cette activité, vous allez modifier la topologie analytics vue dans les chapitres précédents (et disponible sur Github) pour récolter des statistiques par page et par utilisateur.

Votre mission est de créer un bolt nommé UserPageVisitCount qui va afficher en continu dans la console le nombre de visites réalisées dans la dernière heure, par page et par utilisateur, toutes les trente secondes. Ce bolt sera connecté au spout page-visits avec l'identifiant user-page-visit-counts.

Ce bolt ne devra pas conserver de données en mémoire entre deux appels à sa méthode execute(), par exemple sous la forme d'attributs.

Attention ! Il faut que les statistiques affichées soient correctes, même lorsque le bolt est exécuté de manière distribuée sur plusieurs workers en même temps.
Livrable

Vous livrerez dans un fichier zip le code du répertoire analytics du dépôt Github indiqué ci-dessus, dans lequel vous aurez modifié le fichier App.java et ajouté le fichier UserPageVisitCount.java.

"""

from random import random
from datetime import timedelta, datetime
import faust

import aiohttp
import asyncio
import json
import jsonpickle
import random

class PageVisit(faust.Record, serializer='json', isodates=True):
	url: str
	userid: int

class VisitStat(faust.Record, serializer='json', isodates=True):
	total: int
	nb: int

	def __init__(self, nb: int = 0, total: int = 0) :
		self.nb = nb
		self.total = total
	
	def decode(str):
		t, n = json.decode( str )
		return( VisitStat( t, n ))
	
	def encode(self):
		v = { 'total': self.total, 'nb': self.nb }
		return( json.encode( v ))

app = faust.App(
    'analytics',
    broker='kafka://localhost:9092',
)

# windowSize ( min )
windowSize = 60

# timeDelay ( sec )
timeDelay = 30

page_visits = app.topic('page-visits', key_type=str, value_type=PageVisit)
# page_visits = app.topic('page-visits', key_type=str, value_type=PageVisit).maybe_declare()

urls_total = app.SetTable(
		'urls_total',
	    #v0: value_type=VisitStat,
	    value_type=str,
		).hopping((windowSize+1)*60, timeDelay, timedelta(minutes=(windowSize+1)), True)
		# ).hopping((windowSize+1)*60, timeDelay, expires=timedelta(minutes=(windowSize+1)), key_index=True)

user_total = app.SetTable(
		'user_total',
	    value_type=VisitStat,
		).hopping((windowSize+1)*60, timeDelay, timedelta(minutes=(windowSize+1)), True)
		# ).hopping(((windowSize+1)*60, timeDelay, expires=timedelta(minutes=(windowSize+1)), key_index=True)

def update_table( t, idx, nb ):
	table = t[idx]

	first = VisitStat.decode( table.delta(deltatime(minutes=windowSize)))
	last = table.delta(deltatime(seconds=timeDelay))

	total = last.total + nb - first.nb

	table = VisitStat( total, nb ).encode()

@app.timer(interval=timeDelay)
@app.agent( page_visits )
async def UrlVisitCountBolt(visits):
	nb = 0
	async for visit in visits.group_by( PageVisit.url ):
		nb += 1

	update_table( urls_total, url, nb )
	# total = urls_total[url].total + nb - urls_total[url].delta(deltatime(minutes=windowSize))

@app.timer(interval=timeDelay)
@app.agent( page_visits )
async def UserVisitCountBolt(visits):
	nb = 0
	async for visit in visits.group_by( PageVisit.userid ):
		nb += 1

	update_table( user_total, url, nb )
	# total = user_total[url].total + nb - user_total[url].delta(deltatime(minutes=windowSize))

UrlsList = [
	"http://example.com/index.html",
	"http://example.com/404.html",
	"http://example.com/subscribe.html"
	]

UsersList = list( range(5) )

@app.timer(interval=1.0)
async def PageVisitSpout():
	url = random.choices( UrlsList )
	id = random.choices( UsersList )


	await page_visits.send(
		key=url,
		value=PageVisit( url, id )
		)

if __name__ == '__main__':
	app.main()
