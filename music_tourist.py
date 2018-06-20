#Builds an ontology of music artists who were born, lived, died or started in a given
#geographical location, queried by text string. Groups in which the artists were or are
#a member are also added. Releases and key metadata for all related acts are stored.

#Import libraries
from SPARQLWrapper import SPARQLWrapper, RDF, JSON, XML
import rdflib
from rdflib.graph import Graph, URIRef
from rdflib.namespace import Namespace
from rdflib import plugin
from rdflib.plugins.memory import IOMemory
import sys

#Query endpoint
endpoint = SPARQLWrapper("http://dbpedia.org/sparql")

#Location variable for query - CHANGE THIS TO BUILD ONTOLOGIES FOR DIFFERENT PLACES
Location=str(sys.argv[1])

#Query script using SPARQL syntax
construct_query=('''
PREFIX mo: <http://www.semanticweb.org/rishi/ontologies/music_tourist#>
PREFIX dbpedia-owl: <http://dbpedia.org/ontology/>
PREFIX foaf: <http://xmlns.com/foaf/0.1/>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> 
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX schema: <http://schema.org/>
PREFIX xml: <http://www.w3.org/XML/1998/namespace>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>


CONSTRUCT {
?music_act rdf:type mo:Act .
?music_act mo:startingPlaceOf ?origin .
?origin rdf:type mo:Place .
?music_act mo:livedIn ?lived .
?lived rdf:type mo:Place .
?music_act mo:livesIn ?lives .
?lives rdf:type mo:Place .
?music_act mo:bornIn ?born .
?born rdf:type mo:Place .
?music_act mo:diedIn ?died .
?died rdf:type mo:Place .
mo:Place mo:description ?about .
?music_act xsd:gYear ?startedOn .
?music_act schema:endDate ?endedOn .
?music_act mo:description ?about .
?music_act mo:presentMemberOf ?current_group .
?current_group rdf:type mo:CurrentGroup .
?current_group xsd:gYear ?startedOn .
?current_group schema:endDate ?endedOn .
?current_group mo:description ?about .
?music_act mo:formerMemberOf ?previous_group .
?previous_group rdf:type mo:PreviousGroup .
?previous_group xsd:gYear ?startedOn .
?previous_group schema:endDate ?endedOn .
?previous_group mo:description ?about .
?music_release rdf:type mo:Release .
?related_work rdf:type mo:Release .
?current_group mo:isPerformerOf ?related_work .
?previous_group mo:isPerformerOf ?related_work .
?music_act mo:isPerformerOf ?music_release .
}

WHERE {
?music_act rdf:type schema:MusicGroup .
OPTIONAL	{?music_act dbpedia-owl:activeYearsStartYear ?startedOn}
OPTIONAL	{?music_act dbpedia-owl:activeYearsEndYear ?endedOn}
OPTIONAL	{?music_act dbpedia-owl:origin ?origin}
OPTIONAL	{?music_act dbpedia-owl:hometown ?lived}
OPTIONAL	{?music_act dbpedia-owl:residence ?lives}
OPTIONAL 	{?music_act dbpedia-owl:birthPlace ?born}
OPTIONAL 	{?music_act dbpedia-owl:deathPlace ?died}
FILTER 		(regex(str(?origin), "%(place)s") ||
			 regex(str(?lived), "%(place)s") || 
			 regex(str(?lives), "%(place)s") || 			 
			 regex(str(?born),"%(place)s") || 
			 regex(str(?died), "%(place)s"))			 
OPTIONAL {
		?current_group dbpedia-owl:bandMember ?music_act .
		?current_group dbpedia-owl:activeYearsStartYear ?startedOn .
		OPTIONAL {?current_group dbpedia-owl:activeYearsEndYear ?endedOn .}
		OPTIONAL {?current_group dbpedia-owl:abstract ?about
				FILTER (LANG(?about)="en")	
				}
		OPTIONAL {?related_work dbpedia-owl:musicalArtist ?current_group}
		}
OPTIONAL {
		?previous_group dbpedia-owl:formerBandMember ?music_act .
		?previous_group dbpedia-owl:activeYearsStartYear ?startedOn .
		OPTIONAL {?previous_group dbpedia-owl:activeYearsEndYear ?endedOn .}
		OPTIONAL {?previous_group dbpedia-owl:abstract ?about
				FILTER (LANG(?about)="en")
				}
		OPTIONAL {?related_work dbpedia-owl:musicalArtist ?previous_group}		
		}
OPTIONAL {?music_release dbpedia-owl:musicalArtist ?music_act}
OPTIONAL {?music_act dbpedia-owl:abstract ?about
		FILTER (LANG(?about)="en")
		}		
}'''%{'place':Location})

# Create query
endpoint.setQuery(construct_query)

# Set the return format to XML
endpoint.setReturnFormat(XML)


# Turn the query into a readable format
graph = endpoint.query().convert()


# Index for line numbers
i = 0

# List all triples to verify the RDF graph for debugging
for s,p,o in graph:
	print(i,s,p,o)
	i=i+1

# Create the local RDF store and save graph
memory_store=IOMemory()
graph_id=URIRef("http://www.semanticweb.org/store/music_tourist")
g = Graph(store=memory_store, identifier=graph_id)
rdflib.plugin.register('sparql', rdflib.query.Processor, 'rdfextras.sparql.processor', 'Processor')
rdflib.plugin.register('sparql', rdflib.query.Result, 'rdfextras.sparql.query', 'SPARQLQueryResult')

# Parse the results to the .owl ontology and update
g = endpoint.query().convert()
g.parse("music_tourist.owl")
g.serialize("example.owl", "xml")