genre_corresp_table = {
"an" : "122",
"in" : "143",
"of" : "149",
"gr" : "137",
"hy" : "139",
"co" : "130",
"tr" : "159"}


def fetch(incipit, genre):
  try:
    incipit = "+".join(incipit.split())
    genre = genre_corresp_table[genre]
    url = "https://cantus.uwaterloo.ca/search?op=starts&t={}&genre={}&cid=&mode=&feast=&volpiano=All".format(incipit, genre)
    r = requests.get(url)
    s = r.text
    body = s.split("<tbody>")[1].split("</tbody>")[0]
    rows = body.split("<tr")[1:]
    raw_ids = [line.split("<td")[8] for line in rows]
    raw_ids = [x.split("</a>")[0].split(">")[-1] for x in raw_ids]
    ids = list(set(raw_ids))
    ids = [x for x in ids if len(x.strip()) > 0]
    if ids == []:
      raise Exception("Trouvé des ids mais tous vides")
    return (True, ids)
  except Exception as e:
    return (False, e)

def glink(id):
  return "https://gregobase.selapa.net/chant.php?id=" + id

def clink(id):
  return "http://cantusindex.org/id/" + id

def output_results(list_of_results, outfile):
  out = open(outfile, "w")
  for d in list_of_results:
    s = "Cantus IDs : "
    for cid in d['cantus_ids']:
      cid = str(cid)
      s += "<a href="+clink(cid)+">"+cid+"</a> ; "
    s += "Chants : "
    for gid in d['gregobase_ids']:
      id = eval(gid)
      s += "<a href="+glink(id)+">"+id+"</a> ; "
    s += "<br>"
    out.write(s+"\n")
  out.close()

