import os
import json
import base64
from analytics.models import *
from collections import defaultdict
from urllib.parse import quote, unquote

"""
Query objects are JSON objects with the structure:
{
    "filters": {
        ...
    }
}
"""

def str_from_query(query):
  payload = json.dumps(query)
  encoded = base64.urlsafe_b64encode(payload.encode()).decode()
  return quote(encoded)

def query_from_str(s):
  payload = base64.urlsafe_b64decode(
      unquote(s).encode()
  ).decode()
  return json.loads(payload)

def execute_query(query):
  """
  Runs an unserialized query (captured from the URL) and returns a queryset of Gregobase entries matching that query.
  """
  queryset = Chant.objects.all()
  filters = query.get("filters", {})
  queryset = queryset.filter(**filters)
  return queryset

def duplicate_usage():
  dupl_values = defaultdict(int)
  for chant in Chant.objects.all():
    dupl_values[chant.duplicateof] += 1
  softdeleted = dupl_values[-1]
  nonduplicates = dupl_values[None]
  duplicates = sum( [dupl_values[x] for x in dupl_values if x not in [-1, None] ] )
  softdeleted_query = {
    "filters": {
      "duplicateof": -1
    }
  }
  nonduplicates_query = {
    "filters": {
      "duplicateof": None
    }
  }
  duplicates_query = {
    "filters": {
      "duplicateof__gt": -1
    }
  }
  out1 = "<a href=query/{}>{} chants are soft-deleted without duplication</a><br>".format(str_from_query(softdeleted_query), softdeleted)
  out2 = "<a href=query/{}>{} chants are not duplicates</a><br>".format(str_from_query(nonduplicates_query), nonduplicates)
  out3 = "<a href=query/{}>{} chants are soft-deleted as duplicates</a><br><br>".format(str_from_query(duplicates_query), duplicates)
  return out1+out2+out3

def version_usage():
  versions = defaultdict(int)
  for chant in Chant.objects.filter(duplicateof=None):
    versions[chant.version] += 1
  out = "{} different versions : <br>".format(len(versions))
  versions = {k: v for k, v in sorted(versions.items(), key=lambda item: item[1])}
  for version in versions :
    query = {
      "filters": {
        "version": version,
        "duplicateof": None
      }
    }
    out += "<a href=query/{}>{} : {}</a><br>".format(str_from_query(query), version, versions[version])
  return out

def version_by_source():
  out = ""
  for source in Source.objects.all():
    versions = defaultdict(int)
    for chant in source.chants.filter(duplicateof = None):
      versions[chant.version] +=1
    out += "<a href=https://gregobase.selapa.net/source.php?id={}>{} ({})</a> : ".format(source.id, source.title, source.year)
    for version in versions:
      query = {
        "filters": {
          "sources": source.id,
          "version": version,
          "duplicateof": None
        }
      }
      out += "<a href=query/{}>{} : {}</a>, ".format(str_from_query(query), version, versions[version])
    out += "<br>"
  out += "No source : "
  versions = defaultdict(int)
  for chant in Chant.objects.filter(sources = None, duplicateof = None) :
    versions[chant.version] += 1
  for version in versions:
    query = {
      "filters": {
        "sources": None,
        "version": version,
        "duplicateof": None
      }
    }
    out += "<a href=query/{}>{} : {}</a>, ".format(str_from_query(query), version, versions[version])
  return out

def opart_usage():
  out = ""
  oparts = defaultdict(int)
  for chant in Chant.objects.filter(duplicateof = None):
    oparts[chant.office_part] += 1
  oparts = {k: v for k, v in sorted(oparts.items(), key=lambda item: item[1])}
  for opart in oparts:
    query = {
      "filters": {
        "office_part": opart,
        "duplicateof": None
      }
    }
    out += "<a href=query/{}>{} : {}</a>, ".format(str_from_query(query), opart, oparts[opart])
  out += "<br>"
  return out

def same_title_version_usage():
  out = ""
  mydic = defaultdict(list)
  for chant in Chant.objects.filter(duplicateof = None):
    mydic[ (chant.incipit, chant.version, chant.office_part) ].append(chant)
  for x in mydic:
    if len(mydic[x]) > 1:
      (incipit, version, usage) = x
      out += "<br>{} \"{}\" ({}) : ".format(usage, incipit, version)
      for c in mydic[x]:
        out += "<a href=https://gregobase.selapa.net/chant.php?id={}>{}</a> ".format(c.id, c.id)
  return out

def same_gabc():
  out = ""
  mydic = defaultdict(list)
  shorts = []
  for chant in Chant.objects.filter(duplicateof = None):
    if (not chant.gabc) or (len(chant.gabc) < 10):
      shorts.append(chant)
    else:
      mydic[chant.gabc].append(chant)
  for gabc in mydic:
    if len(mydic[gabc]) > 1:
      out += "<br>{}... : ".format(gabc[:20])
      for c in mydic[gabc]:
        out += "<a href=https://gregobase.selapa.net/chant.php?id={}>{}</a> ".format(c.id, c.id)
  out += "<br>Chants with abnormally short gabc: "
  for c in shorts:
    out += "<a href=https://gregobase.selapa.net/chant.php?id={}>{}</a> ".format(c.id, c.id)
  return out

def tag_usage():
  out = ""
  mydic = defaultdict(int)
  for chant in Chant.objects.filter(duplicateof = None):
    for tag in chant.tags.all():
      mydic[tag] += 1
  for tag in mydic:
    query = {
      "filters": {
        "tags": tag.id,
        "duplicateof": None
      }
    }
    out += "<br><a href=query/{}>{} : {}</a>, ".format(str_from_query(query), tag.tag, mydic[tag])
  return out

def export_to_nocturnale():
  path_to_code2gid = "../nocturnale/data_sources/code_to_gid.tsv"
  path_to_export = "../nocturnale/data_sources/nr02_export.tsv"
  entryseparator = "\t\t\t\t\t\t\t\t\t"
  l = open(path_to_code2gid).readlines()
  l = [x.strip().split('\t') for x in l]
  out = open(path_to_export, "w")
  for [code, gid] in l:
    c = Chant.objects.get(id=int(gid))
    try:
      gabc = eval(c.gabc)
    except:
      gabc = ""
    try:
      gabcv = eval(c.gabc_verses)
    except:
      gabcv = ""
    out.write('\t'.join([ code, str(c.mode), str(c.mode_var), gabc+gabcv   ])+entryseparator)
  out.close()
