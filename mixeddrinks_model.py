"""SQLAlchemy model for mixed drinks and their ingredients

    ****** NOTE: be sure to create a db named mixeddrinks ******

    Ways to work with this data model: 

    First clear the db, just in case
    >>> db.drop_all()
    >>> db.create_all()

    Make a drink: 
    >>> marge = MixedDrink(drink_name='margarita')

    Is it in the db? No.
    >>> MixedDrink.query.all()
    []

    How about after adding? No.
    >>> db.session.add(marge)
    >>> MixedDrink.query.all()
    []

    How about after committing? Now marge has an ID! 
    >>> db.session.commit()
    >>> marge
    <MixedDrink drink_id=1 drink_name=margarita>
 
    But no components
    >>> marge.components
    []

    Let's make some tequila
    >>> teq = Ingredient(ingredient_name='tequila')

    Doesn't have an ingredient_id yet, because we haven't committed
    >>> teq
    <Ingredient ingredient_id=None ingredient_name=tequila>

    Add the tequlia to the session and commit to get an ingredient_id
    >>> db.session.add(teq)
    >>> teq
    <Ingredient ingredient_id=None ingredient_name=tequila>
    >>> db.session.commit()
    >>> teq
    <Ingredient ingredient_id=1 ingredient_name=tequila>
    >>> teq.ingredient_id
    1
    >>> marge.drink_id
    1


    Here's one way to add a component to marge: explicitly make an entry in the
    drink ingredient table (its name is irrelevant, hence 'fred')
    >>> fred = DrinkIngredient(drink_id=marge.drink_id, ingredient_id=teq.ingredient_id)
    >>> db.session.add(fred)
    >>> db.session.commit()
    >>> marge.components
    [<Ingredient ingredient_id=1 ingredient_name=tequila>]


    But another (better) way is to use the components relationship
    >>> limey = Ingredient(ingredient_name='lime juice')
    >>> marge.components.append(limey)
    >>> marge.components
    [<Ingredient ingredient_id=1 ingredient_name=tequila>, <Ingredient ingredient_id=None ingredient_name=lime juice>]

    Now if we commit, limey is committed even though it wasn't added, because 
    it's included in the change to marge, and marge *has* been added
    >>> db.session.commit()

    What drinks contain tequila? 
    >>> teq.libations
    [<MixedDrink drink_id=1 drink_name=margarita>]

    What drinks contain lime juice? 
    >>> limey.libations
    [<MixedDrink drink_id=1 drink_name=margarita>]

    Let's make another drink with tequila
    >>> sunny = MixedDrink(drink_name='tequila sunrise')
    >>> sunny.components.append(teq)
    >>> sunny.components
    [<Ingredient ingredient_id=1 ingredient_name=tequila>]

    Now what drinks contain tequila? 
    >>> teq.libations
    [<MixedDrink drink_id=1 drink_name=margarita>, <MixedDrink drink_id=None drink_name=tequila sunrise>]

    And lime? 
    >>> limey.libations
    [<MixedDrink drink_id=1 drink_name=margarita>]

    What can we do with marge? 
    >>> dir(marge)
    ['__class__', '__delattr__', '__dict__', '__doc__', '__format__', '__getattribute__', '__hash__', '__init__', '__mapper__', '__mapper_cls__', '__module__', '__new__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '__sizeof__', '__str__', '__subclasshook__', '__table__', '__tablename__', '__weakref__', '_decl_class_registry', '_sa_class_manager', '_sa_instance_state', 'components', 'drink_id', 'drink_name', 'metadata', 'query', 'query_class']

    We can add more ingredients to the tequlia sunrise
    >>> oj = Ingredient(ingredient_name='orange juice')
    >>> sunny.components.append(oj)

    >>> sunny.components
    [<Ingredient ingredient_id=1 ingredient_name=tequila>, <Ingredient ingredient_id=None ingredient_name=orange juice>]
    >>> oj.libations
    [<MixedDrink drink_id=None drink_name=tequila sunrise>]

    >>> cran = Ingredient(ingredient_name='cranberry juice')
    >>> cran.libations.append(sunny)
    >>> sunny.components
    [<Ingredient ingredient_id=1 ingredient_name=tequila>, <Ingredient ingredient_id=None ingredient_name=orange juice>, <Ingredient ingredient_id=None ingredient_name=cranberry juice>]

    >>> db.session.commit()

"""

from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from datetime import datetime

# This is the connection to the PostgreSQL database; we're getting this through
# the Flask-SQLAlchemy helper library. On this, we can find the `session`
# object, where we do most of our interactions (like committing, etc.)

app = Flask(__name__)
db = SQLAlchemy()


##############################################################################
# Model definitions

class Ingredient(db.Model):
    """Type of ingredient"""

    __tablename__ = "ingredients"

    ingredient_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    ingredient_name = db.Column(db.String(32))

    # libations is the attribute name to get the drinks associated with 
    # this ingredient
    
    # components is the attribute name to get the ingredients associated 
    # with a MixedDrink object
    
    libations = db.relationship('MixedDrink', secondary='drink_ingredients',
                            backref='components')

    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<Ingredient ingredient_id=%s ingredient_name=%s>" % (
                                    self.ingredient_id, self.ingredient_name)

class MixedDrink(db.Model):

    __tablename__ = 'drinks'

    drink_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    drink_name = db.Column(db.String(32))

    # this is a reasonable alternative to line 32
    # components = db.relationship('Ingredients', secondary='drink_ingredients',
    #                         backref='libations')


    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<MixedDrink drink_id=%s drink_name=%s>" % (
                                    self.drink_id, self.drink_name)


class DrinkIngredient(db.Model):
    """association table between drinks and ingredients"""

    # this is an association table; it does not contain any interesting fields
    # Noelis would call it 'frankentable'

    __tablename__ = 'drink_ingredients'

    drinkingredient_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    drink_id = db.Column(db.Integer, db.ForeignKey('drinks.drink_id'))
    ingredient_id = db.Column(db.Integer, db.ForeignKey('ingredients.ingredient_id'))


##############################################################################
# Helper functions

def connect_to_db(app, db_uri='postgresql:///mixeddrinks'):
    """Connect the database to our Flask app."""

    # Configure to use our PostgreSQL database
    app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
#    app.config['SQLALCHEMY_ECHO'] = True
    db.app = app
    db.init_app(app)

if __name__ == '__main__':

    connect_to_db(app)
    db.create_all()

    print "connected to DB"   

    import doctest

    if doctest.testmod().failed == 0:
        print "\n*** ALL TESTS PASS! GO HAVE A DRINK!\n"                   

 
