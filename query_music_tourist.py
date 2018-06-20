#Provides user-friendly readable summary of acts and associated groups for a given location.

#Import libraries
import logging
import rdflib
from _pyio import open

#Call logging library
logging.basicConfig()


#Query for releases from acts with a direct connection to the location
act_query = """
PREFIX mo: <http://www.semanticweb.org/rishi/ontologies/music_tourist#> 
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
SELECT DISTINCT ?music_act ?startedOn
WHERE {	?music_act rdf:type mo:Act .
		?music_act xsd:gYear ?startedOn .
      }"""

#Query for releases from acts with a direct connection to the location
act_releases = """
PREFIX mo: <http://www.semanticweb.org/rishi/ontologies/music_tourist#> 
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
SELECT DISTINCT ?music_act ?music_release
WHERE {	?music_act rdf:type mo:Act .
		?music_act mo:isPerformerOf ?music_release .
      }"""

#Query for releases from groups currently linked to an act with a direct connection
#to the location      
current_group_releases = """
PREFIX mo: <http://www.semanticweb.org/rishi/ontologies/music_tourist#> 
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>  
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
SELECT DISTINCT ?current_group ?related_work ?music_act
WHERE { ?current_group rdf:type mo:CurrentGroup .
		?current_group mo:isPerformerOf ?related_work .	
		?music_act mo:presentMemberOf ?current_group .									
      }"""
    
#Query for releases from groups previously linked to an act with a direct connection
#to the location      
previous_group_releases = """
PREFIX mo: <http://www.semanticweb.org/rishi/ontologies/music_tourist#> 
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#> 
SELECT DISTINCT ?previous_group ?related_work ?music_act
WHERE { ?previous_group rdf:type mo:PreviousGroup .
		?previous_group mo:isPerformerOf ?related_work .
		?music_act mo:formerMemberOf ?previous_group .										
      }"""

#Generate the graph from the local store
g=rdflib.Graph()
result=g.parse("example.owl", "xml")


#Print releases from local artists
print ('\n')
print ('\033[1m'+'Artists from this Location')    
print ('{0:30s}{1:12s}'.format("--Act--","--Started--"))
for i,j in g.query(act_query):
    print ('\033[0m'+'{0:30s}{1:12s}'.format(str(i)[28:],str(j)[0:4]))

#Print releases from local artists
print ('\n')
print ('\033[1m'+'Releases by Artists from this Location')    
print ('{0:30s}{1:12s}'.format("--Act--","--Track--"))
for i,j in g.query(act_releases):
    print ('\033[0m'+'{0:30s}{1:50s}'.format(str(i)[28:],str(j)[28:]))

#Print releases from bands currently connected to local artists
print ('\n')
print ('\033[1m'+'Releases by Groups Currently Associated with Artists from this Location')
print ('{0:30s}{1:50s}{2:30s}'.format("--Act--","--Track--","--Association--"))
for i,j,k in g.query(current_group_releases):
    print ('\033[0m'+'{0:30s}{1:50s}{2:30s}'.format(str(i)[28:],str(j)[28:],str(k)[28:]))

#Print releases from bands previously connected to local artists    
print ('\n')
print ('\033[1m'+'Releases by Groups Previously Associated with Artists from this Location')
print ('{0:30s}{1:50s}{2:30s}'.format("--Act--","--Track--","--Association--"))
for i,j,k in g.query(previous_group_releases):
    print ('\033[0m'+'{0:30s}{1:50s}{2:30s}'.format(str(i)[28:],str(j)[28:],str(k)[28:]))
