import warnings
warnings.filterwarnings('ignore', category=FutureWarning)
from flask import abort, render_template, Flask
import logging
import db

APP = Flask(__name__)

# Start page
@APP.route('/')
def index():
    stats = {}
    stats = db.execute('''
    SELECT * FROM
      (SELECT COUNT(*) n_categories FROM Category)
    JOIN
      (SELECT COUNT(*) n_cities FROM City)
    JOIN
      (SELECT COUNT(*) n_continents FROM Continent)
    JOIN 
      (SELECT COUNT(*) n_countries FROM Country)
    JOIN 
      (SELECT COUNT(*) n_institutions FROM Institution)
    JOIN 
      (SELECT COUNT(*) n_laureates FROM Laureate)
    JOIN 
      (SELECT COUNT(*) n_nobels FROM Nobel)
    JOIN 
      (SELECT COUNT(*) n_persons FROM Person)
    ''').fetchone()
    logging.info(stats)
    return render_template('index.html',stats=stats)

# Categories
@APP.route('/categories/')
def list_categories():
    categories = db.execute(
      '''
      SELECT CategoryID, Name, FullName
      FROM Category
      ORDER BY CategoryID
      ''').fetchall()
    return render_template('category-list.html', categories=categories)

# Category
@APP.route('/categories/<int:id>/')
def get_category(id):
    category = db.execute(
      '''
      SELECT *
      FROM Category
      WHERE CategoryID = ?
      ''', [id]).fetchone()
    return render_template('category.html', category=category)

# Nobels
@APP.route('/nobels/')
def list_nobels():
    nobels = db.execute(
      '''
      SELECT *
      FROM Nobel
      ORDER BY NobelID
      ''').fetchall()
    return render_template('nobel-list.html', nobels=nobels)

#Nobel
@APP.route('/nobels/<int:id>/')
def get_nobel(id):
  nobel = db.execute(
      '''
      SELECT *
      FROM Nobel 
      WHERE NobelID = ?
      ''', [id]).fetchone()

  if nobel is None:
     abort(404, 'Nobel id {} does not exist.'.format(id))

  laureates = db.execute(
    '''
    SELECT Laureate.Name as Name
    FROM Nobel 
    JOIN Prize
    ON Nobel.NobelID = Prize.NobelID
    JOIN Laureate 
    ON Prize.LaureateID = Laureate.LaureateID 
    WHERE Nobel.NobelID = ?
    ''', [id]).fetchall()
  
  category = db.execute(
      '''
      SELECT Category.Name as CategoryName, Category.FullName as CategoryFullName
      FROM  Nobel JOIN Category ON Nobel.CategoryID = Category.CategoryID
      WHERE Nobel.NobelID = ? 
      ''', [id]).fetchone()

  return render_template('nobel.html', nobel=nobel, laureates = laureates, category = category)

# ///////////////////////////////////////////////////////////
# Prizes
@APP.route('/prizes/')
def list_prizes():
    prizes = db.execute(
      '''
      SELECT *
      FROM Prize
      ''').fetchall()
    return render_template('prize-list.html', prizes=prizes)
# ///////////////////////////////////////////////////////////

# ///////////////////////////////////////////////////////////
# Institutions
@APP.route('/institutions/')
def list_institutions():
    institutions = db.execute(
      '''
      SELECT Institution.LaureateID, Institution.NativeName, Laureate.Name, Institution.Acronym, Institution.FoundationDate
      FROM Institution
      JOIN Laureate on Institution.LaureateID = Laureate.LaureateID
      ''').fetchall()
    return render_template('institution-list.html', institutions=institutions)
# ///////////////////////////////////////////////////////////

# ///////////////////////////////////////////////////////////
# Persons
@APP.route('/persons/')
def list_persons():
    persons = db.execute(
      '''
      SELECT Person.LaureateID, Laureate.Name, Person.BirthDate, Person.Gender, Person.Affiliation, Person.DeathDate
      FROM Person
      JOIN Laureate on Person.LaureateID = Laureate.LaureateID 
      ''').fetchall()
    return render_template('person-list.html', persons=persons)
# ///////////////////////////////////////////////////////////
# Laureates
@APP.route('/laureates/')
def laureates():
    laureates = db.execute(
    '''
    SELECT *
    FROM Laureate                       
    ''').fetchall()
    return render_template('laureate-list.html', laureates=laureates)

# Laureate
@APP.route('/laureates/<int:id>/')
def get_laureate(id):
    laureate = db.execute(
      '''
      SELECT *
      FROM Laureate
      WHERE LaureateID = ?
      ''', [id]).fetchone()
    return render_template('laureate.html', laureate=laureate)
# ///////////////////////////////////////////////
# Laureates Info

@APP.route('/laureatesinfo/')
def list_laureatesinfo():
    laureates = db.execute(
    '''
    SELECT 
    Laureate.LaureateID,
    Laureate.Name AS LaureateName,
    City.Name AS City,
    Country.Name AS Country,
    Continent.Name AS Continent
      FROM Laureate
      JOIN City ON Laureate.CityID = City.CityID
      JOIN Country ON City.CountryID = Country.CountryID
      JOIN Continent ON Country.ContinentID = Continent.ContinentID
      ORDER BY LaureateID
    ''').fetchall()
    return render_template('laureate-info-list.html', laureates=laureates)
# ///////////////////////////////////////////////

# Laureate Info
@APP.route('/laureatesinfo/<int:id>/')
def get_laureateinfo(id):
  laureate = db.execute(
      '''
      SELECT A.LaureateID as LaureateID, A.Name as Name
      FROM laureate A
      WHERE A.LaureateID = ?
      ''', [id]).fetchone()

  if laureate is None:
     abort(404, 'Laureate id {} does not exist.'.format(id))

  address = db.execute(
    '''
      SELECT City.Name AS City, Country.Name AS Country, Continent.Name AS Continent
      FROM Laureate
      JOIN City ON Laureate.CityID = City.CityID
      JOIN Country ON City.CountryID = Country.CountryID
      JOIN Continent ON Country.ContinentID = Continent.ContinentID
      WHERE LaureateID = ?
    ''', [id]). fetchone()

  prizes = db.execute(
    '''
    SELECT
        Category.Name AS PrizeName,
        Nobel.Year AS Year,
        Nobel.Motivation AS Motivation,
        Prize.Portion AS Portion
    FROM
        Laureate
    JOIN
        Prize ON Laureate.LaureateID = Prize.LaureateID
    JOIN
        Nobel ON Prize.NobelID = Nobel.NobelID
    JOIN
        Category ON Nobel.CategoryID = Category.CategoryID
    WHERE
        Laureate.LaureateID = ?
    ''', [id]).fetchall()

  return render_template('laureate-info.html', laureate=laureate, address = address, prizes = prizes)

# ////////////////////////////////////////////////////
@APP.route('/laureatesinfo/search/<expr>/')
def search_laureate(expr):
    expr = '%' + expr + '%'
    # Query for names starting with the expression
    laureates = db.execute(
        '''
        SELECT LaureateID, Name
        FROM laureate
        WHERE Name LIKE ?
        ''', [expr]).fetchall()
    return render_template('laureate-search.html', laureates=laureates)
# ///////////////////////////////////////////////////////////
# Cities
@APP.route('/cities/')
def cities():
    cities = db.execute(
    '''
    SELECT *
    FROM City
    ORDER BY Name                     
    ''').fetchall()
    return render_template('city-list.html', cities=cities)

# City
@APP.route('/cities/<int:id>/')
def get_city(id):
    city = db.execute(
      '''
      SELECT *
      FROM City
      WHERE CityID = ?
      ''', [id]).fetchone()
    return render_template('city.html', city=city)
# ///////////////////////////////////////////////////////////
# Countries
@APP.route('/countries/')
def countries():
    countries = db.execute(
    '''
    SELECT *
    FROM Country   
    ORDER BY Name                    
    ''').fetchall()
    return render_template('country-list.html', countries=countries)

# Country
@APP.route('/countries/<int:id>/')
def get_country(id):
    country = db.execute(
      '''
      SELECT *
      FROM Country
      WHERE CountryID = ?
      ''', [id]).fetchone()
    return render_template('country.html', country=country)
# ///////////////////////////////////////////////////////////
# Continents
@APP.route('/continents/')
def continents():
    continents = db.execute(
    '''
    SELECT *
    FROM Continent  
    ORDER BY Name                    
    ''').fetchall()
    return render_template('continent-list.html', continents=continents)

# Continent
@APP.route('/continents/<int:id>/')
def get_continent(id):
    continent = db.execute(
      '''
      SELECT *
      FROM Continent
      WHERE ContinentID = ?
      ''', [id]).fetchone()
    return render_template('continent.html', continent=continent)

# ////////////////////////////////////////////////////
# Search by country with highest no. of nobel prizes
@APP.route('/by-country/')
def list_countries():
    countries = db.execute(
        '''
        SELECT Country.Name AS Country, COUNT(*) AS Count
        FROM Prize
        JOIN Laureate ON Prize.LaureateID = Laureate.LaureateID
        JOIN City ON Laureate.CityID = City.CityID
        JOIN Country ON City.CountryID = Country.CountryID
        GROUP BY Country 
        ORDER BY Count DESC, Country
        ''').fetchall()
    return render_template('country-list-byno.html', countries=countries)

# ////////////////////////////////////////////////////
# Laureates who have won more than one nobel prizes
@APP.route('/laureates-many-prizes/')
def laureates_many_prizes():
    laureates = db.execute(
        '''
        WITH N AS (SELECT Laureate.LaureateID, Laureate.Name, Count(*) AS NumofPrizes
        FROM Laureate JOIN Prize
        ON Laureate.LaureateID = Prize.LaureateID
        GROUP BY Laureate.LaureateID)
        SELECT * 
        FROM N
        WHERE NumofPrizes > 1
        ORDER BY N.Name
        ''').fetchall()
    return render_template('laureates-many-prizes.html', laureates=laureates)

  
