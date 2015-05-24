#!/usr/bin/env python
"""database and business objects"""
import sys
import subprocess
import datetime
import random
import decimal
from sqlalchemy import or_
from sqlalchemy import desc
from sqlalchemy import create_engine
from sqlalchemy import Table, Column
from sqlalchemy import Integer, String, Boolean, Numeric, DateTime
from sqlalchemy import DECIMAL
from sqlalchemy import MetaData, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relation, backref
from sqlalchemy.orm import sessionmaker
from decimal import Decimal, ROUND_HALF_EVEN
from money import moneyfmt
import money
import config

Base = declarative_base()

class Item(Base):
    """something the store sells"""
    __tablename__ = 'items'

    id              = Column(Integer, primary_key=True)
    name            = Column(String(255), nullable=False)
    price_id        = Column(Integer, ForeignKey('prices.id'), nullable=False)
    tax_category_id = Column(Integer, ForeignKey('tax_categories.id'), nullable=False)
    plu             = Column(String(5))
    size            = Column(Numeric(8,4))
    size_unit_id    = Column(Integer, ForeignKey('sale_units.id'))  # item size
    count           = Column(Integer, nullable=False)
    last_manual_count   = Column(DateTime)
    is_discontinued = Column(Boolean, nullable=False)

    price = relation('Price')
    tax_category = relation('TaxCategory')
    size_unit = relation('SaleUnit') 
    barcodes = relation('BarcodeItem', backref=backref('item'))
    # Commented out here, but added further down, after I define
    # both Category and category_items:
    #categories = relation('Category', 
    #                    secondary = 'category_items',
    #                    backref=backref('items'))
    deliveries = relation('Delivery', backref=backref('item'))
    dist_items = relation('DistributorItem', backref=backref('item'))
    countlogs = relation('ItemCountLog', backref=backref('item'))

    def __init__(self, name, plu="", price=None, tax_category=None,
        size="", size_unit=None, is_discontinued=False):
        self.name = name
        self.plu = plu
        self.price = price
        self.tax_category = tax_category
        self.size = size
        self.size_unit = size_unit
        self.is_discontinued = is_discontinued

    def __repr__(self):
        barcodes_str = ",".join(bci.barcode  for bci in self.barcodes)
        return "<Item('%s','%s','%s',%s,%s,%s,%d)>"%(
            self.name, barcodes_str, self.plu,
            str(self.price), str(self.size), str(self.size_unit),
            self.is_discontinued)

    def __str__(self):
        return self.name
    
    def n_barcodes(self):
        return len(self.barcodes)

    @property
    def tax_rate(self):
        return self.tax_category.rate
    @property
    def tax_amt(self):
        """How much of the unit sale price (in dollars) is tax."""
        if self.price.is_tax_flat is True:
            return self.tax_rate
        else:
            (_,tax,_) = money.cost(1, self.price.unit_cost, self.tax_rate, False )
            return tax


class Price(Base):
    """how much money an item costs"""
    __tablename__ = 'prices'

    id              = Column(Integer, primary_key=True)
    sale_unit_id    = Column(Integer, ForeignKey('sale_units.id'),
                        nullable=False)     # sold by _____
    unit_cost       = Column(Numeric(10,4), nullable=False)
#    tax = Column(Numeric(4,4), nullable=False)
    is_tax_flat     = Column(Boolean, nullable=False)
        # unused --- Lui 11/03/10

    sale_unit = relation('SaleUnit')

    def __init__(self, sale_unit, unit_cost, is_tax_flat):
        self.sale_unit = sale_unit
        self.unit_cost = unit_cost
        self.is_tax_flat = is_tax_flat

    def __repr__(self):
        return "<Price('%s',%s,%d)>"%(
            self.sale_unit, self.unit_cost, self.is_tax_flat)

    def __str__(self):
        if self.sale_unit is None:
            return moneyfmt(self.unit_cost, curr='$', sep='')
        else:
            return moneyfmt(self.unit_cost, curr='$', sep='')
            #return "%s %s"(moneyfmt(self.unit_cost, curr='$', sep=''),
            #    self.sale_unit)
            

UNIT_TYPE = {
    0: 'count',
    1: 'weight',
    2: 'volume',
    3: 'area'
}

class SaleUnit(Base):
    """measure by which item is sold"""
    __tablename__ = 'sale_units'

    id = Column(Integer, primary_key=True)
    name = Column(String(20), nullable=False)
    unit_type = Column(Integer, nullable=False)

    def __init__(self, name, unit_type):
        self.name = name
        self.unit_type = unit_type

    def __repr__(self):
        return "<SaleUnit('%s',%d)>"%(self.name, self.unit_type)

    def __str__(self):
        return self.name


class PriceChange(Base):
    """alteration of price (possibly due to special)"""
    __tablename__ = "price_changes"

    id          = Column(Integer, primary_key=True)
    old_price_id= Column(Integer, nullable=False) 
    new_price_id= Column(Integer, nullable=False)
    special_id  = Column(Integer, ForeignKey('specials.id'))

    # self.special  backref from Special.price_changes

    def __init__(self, old_price, new_price, special=None):
        self.old_price = old_price
        self.new_price = new_price
        self.special = special

    def __repr__(self):
        return "<PriceChange(%s,%s,%d)>"%(
            self.old_price, self.new_price, self.special_id)


class Special(Base):
    """named set of price changes"""
    __tablename__ = 'specials'

    id          = Column(Integer, primary_key=True)
    name        = Column(String(255), nullable=False)
    is_active   = Column(Boolean, nullable=False)

    price_changes = relation('PriceChange',
        order_by='PriceChange.special_id',
        backref='special')

    def __init__(self, name, is_active=True):
        self.name = name
        self.is_active = is_active

    def __repr__(self):
        return "<Special('%s',%d)>"%(self.name, self.is_active)

    def __str__(self):
        return self.name

def get_sales(s, n):
    return s.query(Sale).order_by(desc(Sale.time_ended)).limit(n).all()

def _make_ean13():
    return '999'+''.join([str(random.randint(0,9)) for i in xrange(9)])

def new_customer_code():
    """generate random customer account number ('code') that makes sense
       as an EAN-13 barcode."""
    s = get_session()
    for i in xrange(1000):
        code = _make_ean13()
        if 0 == s.query(Customer).filter(Customer.code == code).count():
            return code
    assert False, 'please restart the program'

class Customer(Base):
    """person who buys stuff"""
    __tablename__ = "customers"

    id      = Column(Integer, primary_key=True)
    code    = Column(String(13), nullable=False)
    name    = Column(String(255), nullable=False)
    email   = Column(String(255))
    tel     = Column(String(16))
    postal  = Column(String(1024))
    balance = Column(Numeric(8,2))
    credit  = Column(Numeric(8,2))

    sales = relation('Sale', backref="customer")

    def __init__(self, code="", name="", email="", tel="",
        postal="", balance=Decimal('0.00'), credit=Decimal('0.00')):
        self.name = name
        self.code = code
        self.email = email
        self.tel = tel
        self.postal = postal
        self.balance = balance
        self.credit = credit

    def __repr__(self):
        return "<Customer('%s','%s','%s','%s','%s',%s,%s)>"%(
            self.account_number, self.name, self.email, self.tel,
            self.postal, self.balance, self.credit)

    def __str__(self):
        return self.name


class Clerk(Base):
    """person who sells stuff"""
    __tablename__ = 'clerks'

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    is_valid = Column(Boolean)

    sales = relation("Sale", backref='clerk')
    # self.sales    backref from Sale.clerk

    def __init__(self, name):
        self.name = name
        self.is_valid = True

    def __str__(self):
        return self.name


PAYMENT = {
    0: 'void',
    1: 'cash',
    2: 'check',
    3: 'debit/credit',
    4: 'tab',
    5: 'link'
}

class Sale(Base):
    """transaction where customer exchanges items for payment"""
    __tablename__ = 'sales'

    id          = Column(Integer, primary_key=True)
    clerk_id    = Column(Integer, ForeignKey('clerks.id'))
    customer_id = Column(Integer, ForeignKey('customers.id'))
    payment     = Column(Integer)
    is_void     = Column(Boolean)
    total       = Column(Numeric(8,2))
    time_started= Column(DateTime)
    time_ended  = Column(DateTime)
    cc_trans    = Column(String(18))
    cc_last4    = Column(String(4))
    cc_name     = Column(String(64))
    cc_auth     = Column(String(20))
    cc_brand    = Column(String(15))
    cc_pnref    = Column(String(10))

    # self.customer backref from Customer.sales
    # self.clerk    backref from Clerk.sales
    items = relation("SaleItem", backref=backref('sale'), cascade="all, delete, delete-orphan")

    def __init__(self, clerk, customer):
        self.clerk = clerk
        self.items = [] # backrefs are fucked up for deleting
        self.customer = customer
        self.payment = 0
        self.is_void = False
        self.total = Decimal('0.00')
        self.time_started = datetime.datetime.now()
        self.time_ended = None
        self.cc_trans = ''
        self.cc_last4 = ''
        self.cc_name = ''

    @property
    def tax_amt(self):
        return sum( si.tax  for si in self.items )
    @property
    def base_cost(self):
        '''total = base_cost + tax'''
        return sum( si.cost  for si in self.items )
    
    def check_tax_consistency(self):
        assert self.total == self.base_cost + self.tax_amt

    def has_tab_payment(self):
        return 807 in [ si.item.id for si in self.items ]

    def tab_payment_amount(self):
        return  sum( i.total  for i in self.items  if i.item.id == 807 )

    def __str__(self):
        return self.total


class SaleItem(Base):
    """record of item exchanged in a sale"""
    __tablename__ = 'sale_items'

    id          = Column(Integer, primary_key=True)
    sale_id     = Column(Integer, ForeignKey('sales.id'), nullable=False)
    item_id     = Column(Integer, ForeignKey('items.id'), nullable=False)
    quantity    = Column(Numeric(10,4))
    unit_cost   = Column(Numeric(10,4))
    cost        = Column(Numeric(8,2), nullable=False)
    tax         = Column(Numeric(8,2), nullable=False)
    total       = Column(Numeric(8,2), nullable=False)
    is_refund   = Column(Boolean, nullable=False)

    #sale = relation(Sale, backref=backref('items', order_by=id))
    item = relation('Item')     # crosses database boundary

    def __init__(self, sale, item, quantity, unit_cost,
                 cost, tax, total, is_refund=False):
        self.sale = sale
        self.item = item
        self.quantity = quantity
        self.unit_cost = unit_cost
        self.cost = cost
        self.tax = tax 
        self.total = total
        self.is_refund = is_refund

    def __str__(self):
        return self.item.name

class TabLog(Base):
    """log of tab transactions"""
    __tablename__ = 'tab_log'

    id          = Column(Integer, primary_key=True)
    customer_id = Column(Integer, ForeignKey('customers.id'), nullable=False)
    old_balance = Column(DECIMAL(8,2))
    new_balance = Column(DECIMAL(8,2))
    when_logged = Column(DateTime)

    customer = relation('Customer')

    def __init__(self, customer, old_balance, new_balance, when_logged):
        self.customer       = customer
        self.old_balance    = old_balance
        self.new_balance    = new_balance
        self.when_logged    = when_logged

    def __repr__(self):
        return '''TabLog{ customer: "%s", when_logged: "%s", old_balance: %.2f, new_balance: %.2f }''' % ( self.customer, self.when_logged, self.old_balance, self.new_balance )

    def __str__(self):
        d = self.delta()
        if d >= 0:
            s = "CHARGED"
        else:
            s = "PAID"
        return """Customer %d (%s) %s $%.2f ($%.2f -> $%.2f) on %s""" % (
                self.customer_id,
                self.customer.name,
                s,
                abs(d),
                self.old_balance,
                self.new_balance,
                self.when_logged
            )

    def delta(self):
        return self.new_balance - self.old_balance

    def is_payment(self):
        return self.new_balance < self.old_balance
    def is_full_payment(self):
        return self.new_balance <= 0

    def find_sale(self):
        """If the given transaction record is a tab CHARGE, find the Sale that charged to it.  If it's a tab PAYMENT, just say None."""
        if self.is_payment() is True:
            return None
        session = get_session()
        # let SQL find sales by the right customer, and paid by tab
        paid_by_tab = [ k  for (k,v) in PAYMENT.items()  if v == 'tab' ][0]
        x = session.query(Sale)
        x = x.filter_by(customer_id = self.customer_id)
        x = x.filter_by(payment = paid_by_tab)
        sales_list = x.all()
        # now filter based on time and amount
        close_enough = datetime.timedelta(seconds = 10)
        sales_list = [ s for s in sales_list
                        if abs(s.time_ended - self.when_logged) <= close_enough ]
        sales_list = [ s for s in sales_list
                        if s.total == self.delta() ]
            # TODO: check that one
        assert len(sales_list) <= 1     # gotta be a better way
        try:
            return sales_list[0]
        except IndexError:  # oops???
            return None

#####
# New classes:

class BarcodeItem(Base):
    """each item's barcodes"""
    __tablename__ = 'barcode_items'

    id              = Column(Integer, primary_key=True)
    item_id         = Column(Integer, ForeignKey('items.id'), nullable=False)
    barcode         = Column(String(16))

    # self.item     backref from Item.barcodes

    def __init__(self, item, barcode):
        self.item = item
        self.barcode = barcode

    def __repr__(self):
        return """<Barcode: "%s" for item "%s">""" % (self.barcode, self.item.name)

    def __str__(self):
        return self.barcode

    def startswith(self, prefix):
        return self.barcode.startswith(prefix)

class Category(Base):
    """item categories"""
    __tablename__ = 'categories'

    id      = Column(Integer, primary_key=True)
    name    = Column(String(255), nullable=False)

    # self.items    backref from Item.categories

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return """<Category "%s">""" % self.name

    def __str__(self):
        return self.name


category_items = Table('category_items', Base.metadata,
        Column('item_id', Integer, ForeignKey('items.id')) ,
        Column('cat_id', Integer, ForeignKey('categories.id'))
        )
Item.categories = relation(Category, secondary=category_items, backref="items")

class Delivery(Base):
    """guess"""
    __tablename__ = 'deliveries'

    id              = Column(Integer, primary_key=True)
    time_delivered  = Column(DateTime)
    item_id         = Column(Integer, ForeignKey('items.id'), nullable=False)
    amount          = Column(Numeric(8,2))
    dist_id         = Column(Integer, ForeignKey('distributors.id'))

    # self.item     backref from Item.deliveries
    # self.distributor  backref from Distributor.deliveries

    def __init__(self, time_delivered, item, amount, distributor):
        self.time_delivered = time_delivered
        self.item = item
        self.amount = amount
        self.distributor = distributor

    def __repr__(self):
        return """<Delivery {time_delivered: "%s", item: "%s", amount: %.2f, distributor: "%s"}>""" % (self.time_delivered, self.item.name, self.amount, self.distributor.name)

class Distributor(Base):
    """guess"""
    __tablename__ = 'distributors'

    id      = Column(Integer, primary_key=True)
    name    = Column(String(255), nullable=False)
    phone   = Column(String(10))

    deliveries = relation('Delivery', backref=backref('distributor'))
    dist_items  = relation('DistributorItem', backref=backref('distributor'))

    def __init__(self, name, phone):
        self.name = name
        self.phone = phone

    def __repr__(self):
        return """<Distributor name: "%s" phone: %s>""" % (self.name, self.phone)
    def __str__(self):
        return self.name

class DistributorItem(Base):
    """Things distributors carry."""
    __tablename__ = 'distributor_items'

    id              = Column(Integer, primary_key=True)
    item_id         = Column(Integer, ForeignKey('items.id'), nullable=False)
    dist_id         = Column(Integer, ForeignKey('distributors.id'), nullable=False)
    dist_item_id    = Column(Integer)   # ???
    wholesale_price = Column(Numeric(8,2))
    case_size       = Column(Numeric(8,2))
    case_unit_id    = Column(Integer, ForeignKey('sale_units.id'))

    case_unit = relation('SaleUnit')
    # self.distributor  backref from Distributor.dist_items
    # self.item         backref from Item.dist_items

    def __init__(self, item, distributor, wholesale_price, case_size, case_unit):
        self.item = item
        self.distributor = distributor
        self.wholesale_price = wholesale_price
        self.case_size = case_size
        self.case_unit = case_unit

    @property
    def markup(self):
        """OP markup: (sale price) / (bought price)"""
        # Fail if we don't buy and sell it by the same unit:
#        assert self.case_unit == self.item.size_unit
            # should do something smarter instead
        sale_unit_price = self.item.price.unit_cost
        wholesale_unit_price = self.wholesale_price / self.case_size
        return sale_unit_price / wholesale_unit_price

    @property
    def margin(self):
        """OP margin: [(sale price) - (bought price)] / (sale price)"""
        return 1 - (decimal.Decimal(1) / self.markup)

class ItemCountLog(Base):
    """manual item counts"""
    __tablename__ = 'item_count_log'

    id          = Column(Integer, primary_key=True)
    item_id     = Column(Integer, ForeignKey('items.id'), nullable=False)
    old_count   = Column(Integer)
    new_count   = Column(Integer)
    when_logged = Column(DateTime)

    # self.item     backref from Item.countlogs

    def __init__(self, item, old_count, new_count, when_logged):
        self.item = item
        self.old_count = old_count
        self.new_count = new_count
        self.when_logged = when_logged

class TaxCategory(Base):
    """guess"""
    __tablename__ = 'tax_categories'

    id      = Column(Integer, primary_key=True)
    name    = Column(String(255))
    rate    = Column(Numeric(4,4))

    def __init__(self, name, rate):
        self.name = name
        self.rate = rate

    def __repr__(self):
        return """<TaxCategory "%s" at %.4f>""" % (self.name, self.rate)
    
    def __str__(self):
        return self.name


#####

# List of classes backed by the inventory database
_inventory_tables = [
        BarcodeItem,
        Category,
#        CategoryItem,
        Delivery,
        Distributor,
        DistributorItem,
        ItemCountLog,
        Item,
        Price,
        PriceChange,
        SaleUnit,
        Special,
        TaxCategory,
    ]
# List of classes backed by the register_tape database
_registertape_tables = [ Clerk, Customer, Sale, SaleItem, TabLog ]

_inv_engine = None
_reg_engine = None
_session = None
_Session = None
def connect():
    global _inv_engine
    global _reg_engine
    global _Session
    _inv_engine = create_engine('mysql://%s:%s@%s/%s'%(
        config.get('db-user'), config.get('db-passwd'),
        config.get('db-host'), config.get('db-name-inv')))
    _reg_engine = create_engine('mysql://%s:%s@%s/%s'%(
        config.get('db-user'), config.get('db-passwd'),
        config.get('db-host'), config.get('db-name-reg')))
    _Session = sessionmaker(twophase=True)
    # Set up binding between each class and the appropriate DB
    D = { }
    for c in _inventory_tables:
        D[c] = _inv_engine
    for c in _registertape_tables:
        D[c] = _reg_engine
    _Session.configure( binds = D )

def get_session():
    global _session
    if _reg_engine is None:
        connect()
    assert _Session is not None
    if _session is None:
        _session = _Session()

    # this nifty `sqlalchemy' library supports having lots of different
    # sessions in flight corresponding to different transactions with
    # the db engine.
    #
    # however, it isn't completely obvious to me how to synchronize
    # pending updates between sessions.
    #
    # this was proving to be a bit of a headache, so i'm going to use
    # exactly one global session. here it is:
#    global all_items
#    global all_barcodes
#    all_items = list( _session.query(Item).filter(item_filter) )
#    all_barcodes = list( _session.query(BarcodeItem).join(Item).filter(item_filter) )
    return _session

def make_db():
    """drop and re-initialize database"""
    db_sql = [
        "drop database if exists %s;"%(config.get('db-name')),
        "create database %s;"%(config.get('db-name')),
        "grant all on %s.* to '%s'@'%s' identified by '%s';"%(
            config.get('db-name'),
            config.get('db-user'), config.get('db-host'),
            config.get('db-passwd')) ]

    # prompt user and issue commands to mysql shell 
    print "warning: this will destroy the current pos database if any."
    print "hit ctrl+C at the prompt unless you are really sure."
    print
    import getpass
    admin_passwd = getpass.getpass("mysql admin password:")
    try:
        mysql = subprocess.Popen([config.get('db-mysql-path'),
            '-h', config.get('db-host'),
            '-u', config.get('db-mysql-admin'),
            '--password=%s'%(admin_passwd)],
            stdin=subprocess.PIPE)
    except OSError, e:
        if e.errno == 2:
            print "couldn't find mysql shell;",
            print "make sure --db-mysql-path is correct"
            sys.exit(1)
        else:
            print "error running mysql shell"
            sys.exit(1)

    try:
        mysql.communicate('\n'.join(db_sql))
    except:
        print 'error creating database'
        sys.exit(2)
    if mysql.returncode != 0:
        print 'error creating database'
        sys.exit(2)

    print 'created database.'

    # now have sqlalchemy create tables.
    connect()
    Base.metadata.bind = _engine
    Base.metadata.create_all()

    # populate some stuff for sanity.
    s = get_session()
    s.add_all([
        SaleUnit('each', 0),
        SaleUnit('count', 0),
        SaleUnit('oz', 1),
        SaleUnit('lbs', 1),
        SaleUnit('g', 1),
        SaleUnit('kg', 1),
        SaleUnit('fl oz', 2),
        SaleUnit('pt', 2),
        SaleUnit('qt', 2),
        SaleUnit('mL', 2),
        SaleUnit('L', 2),
        ])
    s.flush()
 
def _find_unit(s, name):
    q = s.query(SaleUnit).filter(SaleUnit.name == name)
    if q.all():
        return q.all()[0]
    else:
        print "unrecognized unit: %s"%(name)
        sys.exit(2)

def import_prices():
    s = get_session()
    fname = config.get('db-import')
    try:
        price_list = file(fname)
    except:
        print "can't open price list %s"%(fname)
        sys.exit(2)

    header = price_list.readline()
    items = []
    prices = []
    price = None
    print 'building db objects'
    for n, line in enumerate(price_list):
        try:
            (barcode, plu, cost, sale_unit_name, size, name) = line.split('\t')
            (size_qty, size_unit_name) = size.split(' ', 1)
            size = decimal.Decimal(size_qty)
            name = name.strip()
        except:
            print "%s: line %d: %s"%(fname, 2+n, line)
            sys.exit(2)
        if cost != "":
            price = Price(_find_unit(s, sale_unit_name),
                decimal.Decimal(cost),
                decimal.Decimal('.0200'),
                False)
            prices.append(price)
        if barcode == 'nc':
            barcode = ''
        item = Item(name, barcode, plu, price,
                    size, _find_unit(s, size_unit_name),
                    False)
        items.append(item)
    s.add_all(prices)
    s.flush()
    s.add_all(items)
    s.flush()
    print 'added %d items'%(len(items))

# sqlalchemy operator for filtering out unstocked, discontinued Items:
item_filter = or_( Item.is_discontinued == False , Item.count > 0 )
all_items = None
all_barcodes = None
all_names = None
all_plus = None
#all_items = get_session().query(Item).filter(item_filter).all()
#all_barcodes = get_session().query(BarcodeItem).join(Item).filter(item_filter).all()

if __name__ == "__main__":
    config.parse_cmdline(sys.argv[1:])
    if config.get('db-init'):
        make_db()
    elif config.get('db-import'):
        import_prices()
