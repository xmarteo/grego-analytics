import xml.etree.ElementTree as ET
import os
from analytics.models import *
from collections import defaultdict
from analytics.grego_utils import *

def flush_and_import():
  data = ET.parse('grego.xml')
  db = data.getroot()[1]
  sources = [line for line in db if line.attrib['name'] == 'gregobase_sources']
  chants = [line for line in db if line.attrib['name'] == 'gregobase_chants']
  tags = [line for line in db if line.attrib['name'] == 'gregobase_tags']
  chantsources = [line for line in db if line.attrib['name'] == 'gregobase_chant_sources']
  chanttags = [line for line in db if line.attrib['name'] == 'gregobase_chant_tags']
  pleasefixes = [line for line in db if line.attrib['name'] == 'gregobase_pleasefix']
  proofreadings = [line for line in db if line.attrib['name'] == 'gregobase_proofreading']

  Proofreading.objects.all().delete()
  PleaseFix.objects.all().delete()
  ChantSource.objects.all().delete()
  Chant.objects.all().delete()
  Tag.objects.all().delete()
  User.objects.all().delete()
  Source.objects.all().delete()

  print("importing sources")
  for source in sources:
    attrib_dict = {}
    for info in source:
      attrib_dict[info.attrib['name']] = info.text
    s = Source()
    s.id = eval(attrib_dict['id'])
    s.year = eval(attrib_dict['year'])
    s.period = attrib_dict['period']
    s.editor = attrib_dict['editor']
    s.title = attrib_dict['title']
    s.description = attrib_dict['description']
    s.caption = attrib_dict['caption']
    s.pages = attrib_dict['pages']
    s.urls = attrib_dict['urls']
    s.save()
  print("importing chants")
  for chant in chants:
    attrib_dict = {}
    for info in chant:
      attrib_dict[info.attrib['name']] = info.text
    c = Chant()
    c.id = eval(attrib_dict['id'])
    c.incipit = attrib_dict['incipit']
    c.cantusid = attrib_dict['cantusid']
    c.version = attrib_dict['version']
    c.initial = eval(attrib_dict['initial'])
    c.office_part = attrib_dict['office-part']
    c.mode = attrib_dict['mode']
    c.mode_var = attrib_dict['mode_var']
    c.transcriber = attrib_dict['transcriber']
    c.commentary = attrib_dict['commentary']
    c.headers = attrib_dict['headers']
    c.gabc = attrib_dict['gabc']
    c.gabc_verses = attrib_dict['gabc_verses']
    c.tex_verses = attrib_dict['tex_verses']
    c.remarks = attrib_dict['remarks']
    c.copyrighted = eval(attrib_dict['copyrighted'])
    if attrib_dict['duplicateof'] == 'NULL' :
      c.duplicateof=None
    else :
      c.duplicateof = eval(attrib_dict['duplicateof'])
    c.save()
  print("importing tags")
  for tag in tags:
    attrib_dict = {}
    for info in tag:
      attrib_dict[info.attrib['name']] = info.text
    t = Tag()
    t.id = eval(attrib_dict['id'])
    t.tag = attrib_dict['tag']
    t.save()
  print("importing chant sources")
  for chantsource in chantsources:
    attrib_dict = {}
    for info in chantsource:
      attrib_dict[info.attrib['name']] = info.text
    cs = ChantSource()
    try:
      chant = Chant.objects.get(id = eval(attrib_dict['chant_id']) )
    except:
      print(attrib_dict['chant_id'])
      raise
    source = Source.objects.get(id = eval(attrib_dict['source']) )
    cs.chant = chant
    cs.source = source
    cs.page = attrib_dict['page']
    cs.sequence = eval(attrib_dict['sequence'])
    cs.extent = (attrib_dict['extent'])
    cs.save()
  print("importing chant tags")
  for chanttag in chanttags:
    attrib_dict = {}
    for info in chanttag:
      attrib_dict[info.attrib['name']] = info.text
    chant = Chant.objects.get(id = eval(attrib_dict['chant_id']) )
    tag = Tag.objects.get(id = eval(attrib_dict['tag_id']) )
    chant.tags.add(tag)
    chant.save()
  print("importing pleasefixes")
  for pleasefix in pleasefixes:
    attrib_dict = {}
    for info in pleasefix:
      attrib_dict[info.attrib['name']] = info.text
    pf = PleaseFix()
    try:
      chant = Chant.objects.get(id = eval(attrib_dict['chant_id']) )
      pf.chant = chant
    except:
      pass
    pf.pleasefix = attrib_dict['pleasefix']
    pf.time = eval(attrib_dict['time'])
    pf.fixed = eval(attrib_dict['fixed'])
    pf.fixed_time = eval(attrib_dict['fixed_time'])
    user_id = attrib_dict['user_id']
    if (user_id is not None) and (user_id not in ['NULL', '']) :
      (user, created) = User.objects.get_or_create(id = eval(user_id) )
      pf.user = user
    fixer_id = attrib_dict['fixed_by']
    if (fixer_id is not None) and (user_id not in ['NULL', '']) :
      (fixer, created) = User.objects.get_or_create(id = eval(fixer_id) )
      pf.fixed_by = fixer
    pf.save()
  print("importing prooofreading data")
  for proofreading in proofreadings:
    attrib_dict = {}
    for info in proofreading:
      attrib_dict[info.attrib['name']] = info.text
    pr = Proofreading()
    chant = Chant.objects.get(id = eval(attrib_dict['chant_id']) )
    (user, created) = User.objects.get_or_create(id = eval(attrib_dict['user_id']) )
    pr.chant = chant
    pr.user = user
    pr.time = eval(attrib_dict['time'])
    pr.save()

def generate_analytics():
  template = open("analytics_template.html").read()
  template = template.split("SEPARATOR")
  content = [duplicate_usage(), version_usage(), version_by_source(), opart_usage(), same_title_version_usage(), same_gabc(), tag_usage(), ""]
  result = [item for pair in zip(template, content) for item in pair]
  f = open("analytics.html", 'w')
  f.write("".join(result))
  f.close()
