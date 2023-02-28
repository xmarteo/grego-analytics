from django.db import models
from django.db.models import IntegerField, CharField, TextField, ForeignKey, ManyToManyField
from functools import cmp_to_key
import roman

class Source(models.Model):
  id = IntegerField(primary_key=True)
  year = IntegerField()
  period = CharField(max_length = 127, null=True)
  editor = CharField(max_length = 127, null=True)
  title = CharField(max_length = 255)
  description = TextField(null=True)
  caption = TextField(null=True)
  pages = TextField(null=True)
  urls = TextField(null=True)

class User(models.Model):
  id = IntegerField(primary_key=True)

class Tag(models.Model):
  id = IntegerField(primary_key=True)
  tag = CharField(max_length = 255)

class Chant(models.Model):
  id = IntegerField(primary_key=True)
  incipit = CharField(max_length = 255, null=True)
  cantusid = CharField(max_length = 31, null=True)
  version = CharField(max_length = 127, null=True)
  initial = IntegerField()
  office_part = CharField(max_length = 15, null=True)
  mode = CharField(max_length = 7, null=True)
  mode_var = CharField(max_length = 15, null=True)
  transcriber = CharField(max_length = 127, null=True)
  commentary = CharField(max_length = 255, null=True)
  headers = TextField(null=True)
  gabc = TextField(null=True)
  gabc_verses = TextField(null=True)
  tex_verses = TextField(null=True)
  remarks = TextField(null=True)
  copyrighted = IntegerField()
  duplicateof = IntegerField(null=True)
  tags = ManyToManyField(Tag, related_name='chants')
  sources = ManyToManyField(Source, through='ChantSource', related_name='chants')

class ChantSource(models.Model):
  chant = ForeignKey(Chant, on_delete=models.CASCADE, related_name='chantsources')
  source = ForeignKey(Source, on_delete=models.CASCADE, related_name='chantsources')
  page = CharField(max_length = 15, null=True)
  sequence = IntegerField(null=True)
  extent = IntegerField(null=True)

class PleaseFix(models.Model):
  chant = ForeignKey(Chant, on_delete=models.CASCADE, null=True)
  pleasefix = TextField(null=True)
  time = IntegerField()
  user = ForeignKey(User, null=True, on_delete=models.SET_NULL, related_name='reported')
  fixed = IntegerField()
  fixed_by = ForeignKey(User, null=True, on_delete=models.SET_NULL, related_name='fixed')
  fixed_time = IntegerField()

class Proofreading(models.Model):
  chant = ForeignKey(Chant, on_delete=models.CASCADE)
  user = ForeignKey(User, on_delete=models.CASCADE)
  time = IntegerField()

def chantsource_queryset_sortbypage(qset):
  """This sorts a queryset of chantsources according to the page.
  first come roman numeral pages
  then normal-numbered pages
  then pages of the form 123*
  then pages of the form [123]
  then pages of the form »123»
  """
  def pagecompare(p1, p2):
    # first, check if one of them is roman
    try:
      rp1 = roman.fromRoman(p1)
      # p1 is roman, if not, see except block
      try:
        rp2 = roman.fromRoman(p2)
        # p2 is roman as well as p1, if not, see except block
        return (rp1-rp2) # will be negative if p1 < p2
      except roman.InvalidRomanNumeralError:
        return -1 # only p1 is roman : p1 < p2
    except roman.InvalidRomanNumeralError:
      try:
        rp2 = roman.fromRoman(p2)
        # only p2 is roman:
        return 1 # p1 > p2
      except roman.InvalidRomanNumeralError:
        pass
    # second, check if one of them has quotes
    if p1[-1] == '»':
      if p2[-1] == '»':
        return int(p1[1:-1])-int(p2[1:-1])
      else: # p1 has quotes but not p2 : p1 > p2
        return 1
    else :
      if p2[-1] == '»': # p2 has quotes but not p1 : p1 < p2
        return -1
      else : # no quotes involved, and no romans
        pass
    # third, check if one of them has brackets
    if p1[-1] == ']':
      if p2[-1] == ']':
        return int(p1[1:-1])-int(p2[1:-1])
      else: # p1 has brackets but not p2 : p1 > p2
        return 1
    else :
      if p2[-1] == ']': # p2 has brackets but not p1 : p1 < p2
        return -1
      else: # no brackets, no romans, no quotes involved
        pass
    # fourth, check if one of them has a star
    if p1[-1] == '*':
      if p2[-1] == '*':
        return int(p1[:-1])-int(p2[:-1])
      else: # p1 has a star but not p2 : p1 > p2
        return 1
    else :
      if p2[-1] == '*': # p2 has a star but not p1 : p1 < p2
        return -1
      else: # no stars, no brackets, no romans, no quotes involved
        return int(p1)-int(p2)
  qset = qset.order_by("sequence")
  return sorted(qset, key=cmp_to_key(lambda x1,x2 : pagecompare(x1.page, x2.page)))
