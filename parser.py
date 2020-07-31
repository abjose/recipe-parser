from bs4 import BeautifulSoup as bs
from jinja2 import Environment, FileSystemLoader
import requests

"""
existing scraper that looks ok: https://github.com/hhursev/recipe-scrapers/tree/master/recipe_scrapers

todo
- style stuff
  - get rid of li ticks / numbers?
  - make 'ingredients' and 'instructions' sections look better
  - make things gray when crossed out
  - make text bigger
  - make 'ingredients' / 'instructions' section titles have bigger fonts
  - center things nicely
- allow scaling recipe
- figure out food database that would allow changing units (ingredient list: https://github.com/kbrohkahn/recipe-parser/blob/master/allIngredients.txt)
- allow changing units
- show nutritional value
- have little warning sign next to ingredients we couldn't find
- figure out how to serve HTML
- put on server
- look for more steps in org
- show error page if can't parse things

eventually
- nicely handle unicode vulgar fractions: https://stackoverflow.com/questions/35012491/parse-%C2%BD-as-0-5-in-python-2-7
- figure out that website that isn't working
"""

def classes(node):
  classes = []
  if node.has_attr('class'):
    classes.extend(node['class'])
  if node.parent.has_attr('class'):
    classes.extend(node.parent['class'])

  # for parent in node.parents:
  #   if parent.has_attr('class'):
  #     classes.extend(parent['class'])
  return classes

# returns true if `word` is contained in any word in `classes`, a list of strings
def classes_contains_word(classes, word):
  for list_word in classes:
    if word in list_word.lower():
      return True
  return False

# returns true if `classes` contains a string containing a word in `words`
def classes_contains(classes, words):
  for word in words:
    if classes_contains_word(classes, word):
      return True
  return False

def probably_ingredients(classes):
  words = ['ingredient']  # lower case
  return classes_contains(classes, words)

def probably_instructions(classes):
  words = ['instruction', 'step', 'prep'] # lower case
  return classes_contains(classes, words)

def clean(string):
  return ' '.join(string.split())

def find(soup, class_checker):
  for ultag in soup.find_all('ul'):
    if class_checker(classes(ultag)):
      return [clean(litag.text) for litag in ultag.find_all('li')]

  for oltag in soup.find_all('ol'):
    if class_checker(classes(oltag)):
      return [clean(litag.text) for litag in oltag.find_all('li')]

  for divtag in soup.find_all('div'):
    if class_checker(classes(divtag)):
      return divtag.stripped_strings

  print("couldn't find anything")
  return []

def write_page(filename, content):
  # filename = "html/" + url
  with open(filename, "w") as f:
    f.write(content)

def get_page(title, ingredients, instructions, page_template):
  return page_template.render(title=title, ingredients=ingredients, instructions=instructions)

if __name__ == "__main__":
  env = Environment(loader=FileSystemLoader(""))
  page_template = env.get_template("page.html")

  page = requests.get('https://itdoesnttastelikechicken.com/veganized-tastys-chocolate-chip-cookies/')
  #page = requests.get('https://chocolatecoveredkatie.com/2016/08/29/vegan-brownies-recipe-best/')
  #page = requests.get('https://cooking.nytimes.com/recipes/1012881-lobster-bisque')
  #page = requests.get('http://veganicecream.blogspot.com/2007/04/ginger-ice-cream.html')  # doesn't work
  #page = requests.get('https://www.epicurious.com/recipes/food/views/chocolate-sorbet-238249')

  soup = bs(page.content, features="lxml")

  print('ingredients:')
  ingredients = find(soup, probably_ingredients)
  for element in ingredients:
    print('-', element)

  print()
  print('instructions:')
  instructions = find(soup, probably_instructions)
  for element in instructions:
    print('-', element)

  write_page("output.html", get_page(soup.title.string, ingredients, instructions, page_template))


  # maybe, to start with, auto-convert to grams and put original measure in parentheses after
  # so like water: 50g (1 cup) or whatever
  # unless it's already grams

  report_url = 'https://api.nal.usda.gov/ndb/V2/reports/'
  search_url = 'https://api.nal.usda.gov/ndb/search/'
  api_key = 'vYcl5wCigiRHtaWoA3DD5R1D1TJHn1POPef5LAcU'
  # params = {'api_key': api_key, 'q': 'espresso powder', 'ds': 'Standard Reference', 'max': 50}
  params = {'api_key': api_key, 'q': 'salt', 'max': 50}


  # find shortest result? or could remove certain keywords like 'industrial'
  # also TRY to ignore branded food items if there are alternatives
  foods = requests.get(search_url, params=params)
  print()
  print(foods.json())
  print()
  shortest = ''
  for food in foods.json()['list']['item']:
    if len(food['name']) < len(shortest) or not shortest:
      shortest = food['name']
    print(food)


  print ('shortest:', shortest)

  # OK, maybe need more intense user interaction?
  # search for a thing and ask user to choose the right one
  # nice if cache that for next time (so they can save the link and not have to answer those questions again)
