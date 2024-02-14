
#!/usr/bin/env python3
# op_db_library.py
# Patrick McQuighan
# This is the central library for interacting with the OpenProduce databases, inventory and register_tape.
# The library provides all of the functionality for querying the databases: selects, updates, inserts, deletes
# It is meant to be imported by any webtools that want to interact with the database and maybe the POS or other
# scripts.
#
# IMPORTANT: If precise sale total values are needed make sure to separate summing the COST values for LINK sales
#   and summing the TOTAL values for NON-LINK sales since LINK sales don't include sales tax but taxes are still logged
#   in the database.  The only time this matters so far is for reporting sales tax so is handled in get_sales_tax_report
#   See that function for details.  Other things that use sales totals mostly just sum over SaleItem.cost except for
#   in hours.py.
#
# Additionally, note that some data from the database is cached in memory to avoid excess queries such as sale units
#  This happens at the bottom of this file.
#
# Note that currently some functions will return something of class Decimal, and others will return floats.  Comparing
#  floats to decimals gives strange behavior, so if the caller needs to do such a comparison (eg for colors in catalog.py)
#  make sure to set everything to be a float.  Addtionally, arithmetic can't be done between Decimal and floats

import datetime
import decimal

from sqlalchemy import desc
from sqlalchemy import func
from sqlalchemy import create_engine
from sqlalchemy import Table, Column
from sqlalchemy import Integer, String, Boolean, Numeric, DateTime, Text
from sqlalchemy import MetaData, ForeignKey
from sqlalchemy import and_, not_, or_
from sqlalchemy import distinct

from sqlalchemy.orm import mapper
from sqlalchemy.orm import relation, backref
from sqlalchemy.orm import sessionmaker
from decimal import Decimal, ROUND_HALF_EVEN
from functools import reduce

from db_config import register_tape_db_config, inventory_db_config


def format_db_url (config):
    base = "mysql://%s:%s@%s" % (config['db_user'], config['db_pass'], config['db_host'])
    if config['db_port']:
        base = base + ":%s" % (config['db_port'])
    return base + "/" + config['db_name']

# Locations of databases. format is 'mysql://user:passwd@host/db
register_tape_loc = format_db_url(register_tape_db_config)
inventory_loc = format_db_url(inventory_db_config)

# Constants from the web server
ITEM_INFO_PAGE = "item_info.py"           # location of the item_info.py page
CATEGORY_INFO_PAGE = "category_info.py"   # location of the category_info.py page

# Constants from the database
SLUSHFUND = 151                      # customer ID of the slushfund account
# payment types as defined in db.py
# ugh, changing the same constant in two different files, great software design us - CR 1/18/22
PAYMENT = {
    0: 'void',
    1: 'cash',
    2: 'check',
    3: 'debit/credit',
    4: 'tab',
    5: 'link',
    6: 'paid online',
    7: 'manual credit/debit'
   
}


LINK_PAYMENT = 5

TAB_PAYMENT = 807                    # item ID of 'tab payment'
CASH_BACK = 909                      # item id of 'cash back'

MARZIPAN_OPEN = datetime.datetime(2008,8,1)   # date when marzipan was first used
FIRST_SALES = datetime.datetime(2008,7,31) # date first sales were recorded

DAY_START_HOUR = 4                     # used eg in get_daily_sales to define the hour range that we
                                       # want considered to be part of the same day.  In this case, 4am-3:59am will be one day.

# Used to map lists of elements returned from a query to just ids
def to_id (t):
    return t.get_id()

#########################################
# Functions that other tools use
#########################################
def get_item_info_page_link(item_id):
    '''returns a string that can be used directly as the value of an a href
    with item_id set to id'''
    return ''.join([ITEM_INFO_PAGE,'?itemid=',str(item_id)])

def get_category_info_page_link(category_id):
    '''returns a string that can be used directly as teh value of an a href
    with catid set to id'''
    return ''.join([CATEGORY_INFO_PAGE,'?categoryid=',str(category_id)])

def get_item(item_id):
    '''returns an item object with the given id.  if not found returns None'''
    return inv_session.query(Item).filter(Item.id == item_id).one()

def get_price(price_id):
    return inv_session.query(Price).filter(Price.id == price_id).one()

def add_delivery(item_id, amt, distributor=None):
    '''note that the item's count is not affected but will be displayed as updated'''
    if distributor != None:
        delivery = Delivery(datetime.datetime.now(), item_id, amt, dist_id = distributor)
    else:
        delivery = Delivery(datetime.datetime.now(), item_id, amt)
    inv_session.add(delivery)
    inv_session.flush()

def add_barcode_item(item_id, barcode):
    newbi = BarcodeItem(item_id, barcode)
    inv_session.add(newbi)
    inv_session.flush()

def add_item(name, s, sizeunit_name, PLU, count, price, taxcat_name, display_name, description, price_unit=None):
    '''if price_unit != None then this creates a new price object, then creates the item
       otherwise it assumes that the price passed in is an already existing price_id'''
    taxcat = get_tax_category_byname(taxcat_name)
    sizeunit = get_unit_byname(sizeunit_name).id

    if price_unit != None:
        priceunit = get_unit_byname(price_unit).id
        p_id = add_price(price, priceunit)
        newitem = Item(name, p_id, count, taxcat.id, plu=PLU, size=s, size_unit=sizeunit, last_count=datetime.datetime.now(),display_name=display_name,description=description)
    else:
        newitem = Item(name, price, count, taxcat.id, plu=PLU, size=s, size_unit=sizeunit, last_count=datetime.datetime.now(), display_name=display_name, description=description)
    inv_session.add(newitem)
    inv_session.flush()

    return newitem.id

def add_price(price, unit):
    '''adds a new price to the database by value price is the value eg 3.40 and unit is the sale_unit_id'''
    newprice = Price(unit,price,0)
    inv_session.add(newprice)
    inv_session.flush()
    return newprice.id

def add_new_price(price):
    '''adds a new price to the database. initializes it with values from some old price'''
    newprice = Price(price.sale_unit_id, price.unit_cost, price.is_tax_flat)
    inv_session.add(newprice)
    inv_session.flush()
    return newprice

def set_price_sale_unit_id(price, id):
    price.sale_unit_id = id
    inv_session.flush()

def set_item_size_unit(item,s_u):
    '''s_u is a size_unit_id'''
    item.size_unit_id = s_u
    inv_session.flush()

def set_item_size(item,size):
    item.size = size
    inv_session.flush()

def set_item_price(item, newid):
    '''sets an item's price_id to newid'''
    old_price = item.price_id
    item.price_id = newid
    inv_session.flush()

def set_item_name(item, newname):
    item.name = newname
    inv_session.flush()

def set_item_display_name(item, newname):
    item.display_name = newname
    inv_session.flush()

def set_item_description(item, newname):
    item.description = newname
    inv_session.flush()

def set_item_weight(item, weight):
    item.weight = weight
    inv_session.flush()

def set_item_popularity(item, new_pop):
     item.popularity = int(new_pop)
     inv_session.flush()

def set_item_barcode(item, oldbarcode, newbarcode):
    '''Changes the barcode_item corresponding to (item.id, oldbarcode) to be (item.id, newbarcode)'''
    old_barcode_item = inv_session.query(BarcodeItem).filter(and_(BarcodeItem.item_id == item.id, BarcodeItem.barcode == oldbarcode)).one()
    old_barcode_item.barcode = newbarcode
    inv_session.flush()

def price_item_count(price_id):
    '''returns the number of items that have a particular price id (and at least 1 distributor)'''
    return inv_session.query(func.count('*')).filter(and_(Item.id == DistributorItem.item_id, Distributor.id == DistributorItem.dist_id, Item.price_id == price_id)).one()[0]

def get_items_with_price_id (price_id):
    '''returns a list of all items with a given price_id'''
    return inv_session.query(Item).filter(Item.price_id == price_id).all()

def set_price(price, value):
    price.unit_cost = value
    inv_session.flush()

def get_distributors():
    '''returns a list of all distributors'''
    dists = inv_session.query(Distributor).order_by(Distributor.name).all()
    return dists

def get_categories():
    '''returns a list of categories'''
    cats = inv_session.query(Category).order_by(Category.name).all()
    return cats

def get_tax_categories():
    '''returns a list of tax categories'''
    return inv_session.query(TaxCategory).order_by(TaxCategory.name).all()

def get_units():
    '''return a list of all units'''
    return inv_session.query(SaleUnit).all()

def get_recent_item_deliveries(item,days):
    start = datetime.datetime.now() - datetime.timedelta(days = days)
    return inv_session.query(Delivery).filter(and_(Delivery.time_delivered > start,Delivery.item_id == item.id)).all()

def get_recent_item_sales(item,days,include_slush):
    start = datetime.datetime.now() - datetime.timedelta(days = days)
    return filter_valid_sales(reg_session.query(Sale,SaleItem), slushfund=include_slush,start_date=start).filter(SaleItem.item_id == item.id).all()

def get_recent_item_count_log(item,days):
    start = datetime.datetime.now() - datetime.timedelta(days = days)
    return inv_session.query(ItemCountLog).filter(and_(ItemCountLog.when_logged>start,ItemCountLog.item_id == item.id)).all()

def get_distributor_byname(name):
    return inv_session.query(Distributor).filter(Distributor.name == name).one()

def get_category(cat_id):
    return inv_session.query(Category).filter(Category.id == cat_id).one()

def get_unit(unit_id):
    return inv_session.query(SaleUnit).filter(SaleUnit.id == unit_id).one()

def get_distributor(dist_id):
    return inv_session.query(Distributor).filter(Distributor.id == dist_id).one()

def get_tax_category(taxcat_id):
    return inv_session.query(TaxCategory).filter(TaxCategory.id == taxcat_id).one()

def get_tax_category_byname(taxcatname):
    return inv_session.query(TaxCategory).filter(TaxCategory.name == taxcatname).one()

def get_category_byname(catname):
    return inv_session.query(Category).filter(Category.name == catname).one()

def get_unit_byname(unitname):
    return inv_session.query(SaleUnit).filter(SaleUnit.name == unitname).one()

def add_category(name):
    inv_session.add(Category(name))
    inv_session.flush()

def add_distributor(name):
    inv_session.add(Distributor(name))
    inv_session.flush()

def add_tax_category(name,rate):
    inv_session.add(TaxCategory(name,rate))
    inv_session.flush()

def update_tax_category(taxcat, rate):
    taxcat.rate = rate
    inv_session.flush()

def remove_tax_category(taxcat):
    id = taxcat.id
    inv_session.delete(taxcat)
    for i in inv_session.query(Item).filter(Item.tax_category_id == id).all():
        i.tax_category_id = 0
    inv_session.flush()

def remove_category(cat):
    id = cat.id
    inv_session.delete(cat)
    for c_i in inv_session.query(CategoryItem).filter(CategoryItem.cat_id == id).all():
        inv_session.delete(c_i)
    inv_session.flush()

def remove_distributor(dist):
    id = dist.id
    inv_session.delete(dist)
    for d_i in inv_session.query(DistributorItem).filter(DistributorItem.dist_id == id).all():
        inv_session.delete(d_i)
    inv_session.flush()

def set_barcode_item_byid(bc_item_id, newbarcode):
    to_change = inv_session.query(BarcodeItem).filter(BarcodeItem.id == bc_item_id).one()
    to_change.barcode = newbarcode
    inv_session.flush()

def get_barcode_item(item,bc):
    return inv_session.query(BarcodeItem).filter(and_(BarcodeItem.item_id == item.id,BarcodeItem.barcode == bc)).one()

def get_distributor_item_byid(distitemid):
    return inv_session.query(DistributorItem).filter(DistributorItem.id == distitemid).one()

def get_distributor_item(item,distributor):
    '''returns a distributor item searched by item and distributor'''
    # TO FIX:
    '''should really just use .one() but for some reason there are a couple of non-unique item/distributor pairs so .one() gives errors. Hopefully this gets sorted out soon'''
    return inv_session.query(DistributorItem).filter(and_(DistributorItem.item_id == item.id, DistributorItem.dist_id == distributor.id)).all()[0]

def get_distributor_item_margin(item, distributor,dist_item=None):
    ''' returns the margin on a given item coming from a given distributor as a percentage 0->100'''
    if dist_item == None:
        dist_item = get_distributor_item(item,distributor)
    each_cost = dist_item.get_each_cost()
    op_price = item.get_price()
    tax = item.get_tax_value()

    if op_price - tax > 0:
        margin = (1.0 - each_cost/(op_price - tax)) * 100
    else:
        margin = 100

    return margin

def set_item_discontinued(item, val):
    item.is_discontinued = val
    inv_session.flush()

def is_price(price_id):
    return not (inv_session.query(Price).filter(Price.id == price_id).all() == [])

def is_category_byname(catname):
    return not (inv_session.query(Category).filter(Category.name == catname).all() == [])

def is_category(price_id):
    return not (inv_session.query(Category).filter(Category.id == price_id).all() == [])

def is_tax_category(tax_cat_id):
    return not (inv_session.query(TaxCategory).filter(TaxCategory.id == tax_cat_id).all() == [])

def is_tax_category_byname(taxcatname):
    return not (inv_session.query(TaxCategory).filter(TaxCategory.name == taxcatname).all() == [])

def is_category_item(item, cat):
    return not (inv_session.query(CategoryItem).filter(and_(CategoryItem.item_id == item.id, CategoryItem.cat_id == cat.id)).all() == [])

def is_distributor_byname(name):
    return not (inv_session.query(Distributor).filter(Distributor.name == name).all() == [])

def is_distributor(dist_id):
    return not (inv_session.query(Distributor).filter(Distributor.id == dist_id).all() == [])

def is_distributor_item(item,distributor):
    '''returns True if the given item, distributor pair is in the database.  item and distributor should be Item and Distributor objects respectively'''
    return not (inv_session.query(DistributorItem).filter(and_(DistributorItem.item_id == item.id, DistributorItem.dist_id == distributor.id)).all() == [])

def is_item(itemid):
    return not (inv_session.query(Item).filter(Item.id == itemid).all() == [])

def update_item_tax_category(item, taxcat):
    item.tax_category_id = taxcat.id
    inv_session.flush()

def update_distributor_item(di, di_id, price, case_size, units_id):
    di.dist_item_id = di_id
    di.wholesale_price = price
    di.case_size = case_size
    di.case_unit_id = units_id
    inv_session.flush()

def add_distributor_item(item,distributor):
    new_dist_item = DistributorItem(item.id, distributor.id)
    inv_session.add(new_dist_item)
    inv_session.flush()
    return new_dist_item

def get_category_item(item_id,catid):
    return inv_session.query(CategoryItem).filter(and_(CategoryItem.item_id == item_id, CategoryItem.cat_id == catid)).one()

def add_category_item(item,category):
    inv_session.add(CategoryItem(item.id, category.id))
    inv_session.flush()

def remove_barcode_item_byid(bc_item_id):
    to_remove = inv_session.query(BarcodeItem).filter(BarcodeItem.id == bc_item_id).one()
    inv_session.delete(to_remove)
    inv_session.flush()

def remove_category_item_byid(cat_item_id):
    to_remove = inv_session.query(CategoryItem).filter(CategoryItem.id == cat_item_id).one()
    inv_session.delete(to_remove)
    inv_session.flush()

def remove_category_item(item,category):
    to_remove = inv_session.query(CategoryItem).filter(and_(CategoryItem.item_id == item.id, CategoryItem.cat_id == category.id)).one()
    inv_session.delete(to_remove)
    inv_session.flush()

def remove_distributor_item_byid(dist_item_id):
    to_remove = inv_session.query(DistributorItem).filter(DistributorItem.id == dist_item_id).one()
    inv_session.delete(to_remove)
    inv_session.flush()

def remove_distributor_item(item,distributor):
    to_remove = inv_session.query(DistributorItem).filter(and_(DistributorItem.item_id == item.id, DistributorItem.dist_id == distributor.id)).one()
    inv_session.delete(to_remove)
    inv_session.flush()

def get_items(hide_discontinued=False,show_categories=None,show_distributors=None,hide_distributorless=False,hide_categoryless=False,move_discontinued=False, hide_additional_distributors=False):
    '''returns a list of Items sorted by name.  options should come from item_display_form.py and have the same values as there. '''
    if show_categories == None:
        show_categories = get_categories()
    if show_distributors == None:
        show_distributors = get_distributors()
    items = inv_session.query(Item)
    if hide_discontinued:
        items = items.filter(Item.is_discontinued == False)

    if hide_categoryless:
        items = items.filter(Item.categories.any(Category.name.in_(map(lambda cat: cat.name, show_categories))))
    else:
        items = items.filter(or_(Item.categories == None, Item.categories.any(Category.name.in_((map (lambda cat: cat.name, show_categories))))))

    if hide_distributorless:
        items = items.filter(Item.distributors.any(Distributor.name.in_((map(lambda dist: dist.name, show_distributors)))))
    else:
        items = items.filter(or_(Item.distributors.any(Distributor.name.in_((map(lambda dist: dist.name, show_distributors)))), Item.distributors == None))

    if move_discontinued:   # This will put discontinued items at the bottom of the page
        items = items.order_by(Item.is_discontinued)

    items = items.order_by(Item.name)

    return items.all()

def get_items_by_price(price_id):
    '''returns pairs of (item,dist) where the items have a particular price_id'''
    return inv_session.query(Item,Distributor).filter(and_(Item.id == DistributorItem.item_id, Distributor.id == DistributorItem.dist_id, Item.price_id == price_id)).all()

def get_distributor_items(hide_discontinued=False,show_categories=None,show_distributors=None,hide_distributorless=False,hide_categoryless=False, move_discontinued=False,hide_additional_distributors=False):
    '''returns pairs (price,item,dist,dist_item)'''
    if show_categories == None:
        show_categories = get_categories()
    if show_distributors == None:
        show_distributors = get_distributors()

    items = inv_session.query(Price,Item,Distributor,DistributorItem).filter(and_(Item.id == DistributorItem.item_id, Distributor.id == DistributorItem.dist_id, Item.price_id == Price.id))

    if move_discontinued:
        items = items.order_by(Item.is_discontinued)

    items = items.order_by(Price.id).order_by(Item.name).order_by(Distributor.name)

    if hide_discontinued:
        items = items.filter(Item.is_discontinued == False)
    if hide_categoryless:
        items = items.filter(Item.categories.any((Category.name.in_(map(lambda cat: cat.name, show_categories)))))
    else:
        items = items.filter(or_(Item.categories == None, Item.categories.any(Category.name.in_((map (lambda cat: cat.name, show_categories))))))

    if hide_distributorless:
        items = items.filter(Item.distributors.any(Distributor.name.in_(map(lambda dist: dist.name, show_distributors))))
    else:
        items = items.filter(or_(Item.distributors.any(Distributor.name.in_(map(lambda dist: dist.name, show_distributors))), Item.distributors == None))

    return items.all()

def search_for_item(name):
    matches = inv_session.query(Item).filter(Item.name.like('%'+name+'%')).all()
    return matches

def filter_valid_sales (query_obj, start_date=None, end_date=None, slushfund=False):
    '''Takes a query object and filters out Sales that are VOID, SLUSHFUNDED, and SaleItems to 'tab payment' or 'cash back'
    optionally filters out sales that occur between start_date and end_date'''
    query_obj = query_obj.filter(and_(Sale.id == SaleItem.sale_id,  Sale.is_void==0, \
                              not_(SaleItem.item_id.in_([TAB_PAYMENT, CASH_BACK]))))
    if (not slushfund):
        query_obj = query_obj.filter(or_(Sale.customer_id!=SLUSHFUND, Sale.customer_id == None))

    if (start_date != None):
        query_obj = query_obj.filter (Sale.time_ended > start_date)
    if (end_date != None):
        query_obj = query_obj.filter (Sale.time_ended < end_date)

    return query_obj

def get_sales_in_range(item_id, days):
        '''returns the number of units of this item sold in the last "days" number of days'''
        start = datetime.datetime.now() - datetime.timedelta(days = days)
        count = filter_valid_sales(reg_session.query(func.sum(SaleItem.quantity)), start_date=start).filter(SaleItem.item_id==item_id).one()[0]
        if count != None:
            return count
        else:
            return 0

def get_sales_in_multi_range(item_id, *days):
    '''this should be used when we want to call get_sales_in_range for multiple days.  Instead of executing multiple queries over all of the SaleItem table,
    we instead compute the first date to appear in the DAYS list, then get all SaleItems in that range. From there we use a reduce to end up with all of the values
    we want looking over a smaller set of data instead of doing multiple full-table sweeps.'''
    num_days = len(days)
    dates = [datetime.datetime.now() - datetime.timedelta(days = d) for d in days]
    start = min(dates)
    sales = filter_valid_sales(reg_session.query(Sale.time_ended,SaleItem.quantity), start_date=start).filter(SaleItem.item_id==item_id).all()
    results = [0.0 for i in range(num_days)]
    for s in sales:
        val = float(s[1])
        date = s[0]
        for i,d in enumerate(dates):
            if (date > d):
                results[i] += val
    return results #[float(get_sales_in_range(item_id,i)) for i in days]

def add_item_count(item_id, amount):
    '''increases item_id's count by the number amount'''
    item = inv_session.query(Item).filter(Item.id == item_id).one()
    if item != None:
        item.count += amount

        inv_session.flush()
        return item.count

def most_sold_items(number, prev_days):
    '''returns a list of the (number) highest selling items in the previous (prev_days)'''
    # This probably needs to have the query updated to ignore things that are slushfunded or whatever
    start_date = datetime.datetime.now() - datetime.timedelta(days=prev_days)
    return filter_valid_sales(reg_session.query(SaleItem.item_id,func.sum(SaleItem.quantity)),start_date=start_date).group_by(SaleItem.item_id).order_by(desc(func.sum(SaleItem.quantity))).limit(number).all()

def most_dollar_items(number, prev_days):
    '''returns a list of the (number) highest grossing items in the previous (prev_days)'''
    start_date = datetime.datetime.now() - datetime.timedelta(days=prev_days)
    return filter_valid_sales(reg_session.query(SaleItem.item_id,func.sum(SaleItem.cost)),start_date=start_date).group_by(SaleItem.item_id).order_by(desc(func.sum(SaleItem.cost))).limit(number).all()

def merge_items(old_item, new_item, merge_barcodes, merge_deliveries, merge_dist_items, merge_sales):
    new_item_id = new_item.get_id()
    if merge_barcodes:
        barcodes = old_item.get_barcodes()
        for bc in barcodes:
            bc.item_id = new_item_id
    if merge_deliveries:
        deliveries = old_item.get_deliveries()
        for d in deliveries:
            d.item_id = new_item_id
    if merge_dist_items:
        dist_items = old_item.get_distributor_items()
        for di in dist_items:
            di.item_id = new_item_id
    if merge_sales:
        sale_items = old_item.get_sale_items()
        for si in sale_items:
            si.item_id = new_item_id
    inv_session.flush()
    inv_session.delete(old_item)
    inv_session.flush()

def get_item_history(item_id, days):
    '''returns a 4-tuple of:
    total_sales (in units, not slushfunded)
    total_deliveries - in units
    total_slushfuneded  - units
    a sorted list containing all changes to the item's count in the last DAYS days in the following form:
       (date, +/-, type) where type is one of the following:
       'Delivery', 'Sale','Slushfunded', 'Manual Count', 'Auto Count'
    '''
    # Before 2/1/2011, things that are deliveries are also logged in item_count_log so we don't want to double print
    # do this by maintaining a list (time,+/-,string) where the string is Delivery,Manual Count, etc.
    #  then, if when adding something from the item_count_log we find we already have that time in the dict and that has the same +/-
    #  then we know that item_count_log was just logging the delivery so we don't add it

    item = get_item(item_id)
    deliveries = get_recent_item_deliveries(item,days)
    sales = get_recent_item_sales(item,days,True)
    item_log = get_recent_item_count_log(item,days)

    history = []
    total_sales = 0
    total_deliveries = 0
    total_slush = 0
    for d in deliveries:
        time_str = d.get_time_delivered()
        history.append((time_str,d.get_amount(), 'Delivery'))
        total_deliveries += d.get_amount()
    for sale,sale_item in sales:
        time_str = sale.get_time_ended()
        if sale.get_customer_id() != SLUSHFUND:
            history.append((time_str,sale_item.get_quantity(),'Sale'))
            total_sales += sale_item.get_quantity()
        else:
            history.append((time_str,sale_item.get_quantity(),'Slushfunded'))
            total_slush += sale_item.get_quantity()
    for i in item_log:
        time_str = i.get_when_logged()
        diff = i.get_diff()
        if (time_str,diff,'Delivery') not in history:
            if i.get_is_manual_count() == 1:
                history.append((time_str,diff,'Manual Count (%d-->%d)'% i.get_counts()))
            else:
                history.append((time_str,diff,'Auto Count (%d-->%d)' % i.get_counts()))

    return (total_sales,total_deliveries,total_slush,sorted(history,key= lambda t: t[0],reverse=True))  # sort things by time newest first


#  Classes and junk for dealing with hours.py and dash.py etc
#  pretty much anything that needs daily/hourly sales totals
class DailySaleInfo(object):
    def __init__(self, date):
        self.date = date
        self.hours = [HourlySaleInfo(i) for i in range(0,24)]  # the only weird thing here is that the hour 0 actually corresponds to the sales done
                                                               # on the previous day at midnight.  Eg a sale at 0:01 8/30/2010 is logged at hour 0 on 8/31/2010
                                                               # this is done to make printing stuff for hours.py easier

    def get_customers_total(self):
        return reduce(lambda x,y: x + y.get_customers(), self.hours, 0)

    def get_gross_sales(self):
        return reduce(lambda x,y: x + y.get_gross_sales(), self.hours, 0)

    def get_avg_sales(self):
        if self.get_customers_total() == 0:
            return 0
        return self.get_gross_sales() / self.get_customers_total()

    def get_date(self):
        return self.date

    def get_dayname(self):
        if self.date != None:
            return self.date.strftime('%A')
        return ''

    def get_date_str(self):
        if self.date != None:
            return self.date.strftime('%Y-%m-%d')
        return ''

    def get_hourly_sales(self,hours):
        '''returns a list of HourlySaleInfo objects for the hours specified'''
        return [self.hours[i] for i in hours]

    def set_hour_sales(self, hour, gross, customers):
        self.hours[hour].set_gross(gross)
        self.hours[hour].set_customers(customers)

class HourlySaleInfo(object):
    def __init__(self, hour):
        self.hour = hour
        self.customers = 0.0
        self.gross = 0.0

    def get_avg_sales(self):
        if self.customers == 0:
            return 0
        return self.gross / self.customers

    def get_hour(self):
        return self.hour

    def get_customers(self):
        return self.customers

    def get_gross_sales(self):
        return self.gross

    def set_gross(self, gross):
        self.gross = gross

    def set_customers(self, customers):
        self.customers = customers

def get_daily_sales(start_date=FIRST_SALES, end_date=datetime.datetime.now()):
    '''returns a list of DailySaleInfo objects.  This is used by hours.py and other scripts needing sale info on a daily/hourly basis.
    optionally takes a range of dates by start_date and end_date.
    '''

    days = {}

    results = filter_valid_sales(reg_session.query(Sale,func.sum(SaleItem.total),func.count(distinct(Sale.id))),start_date,end_date).group_by(func.date(Sale.time_ended)).group_by(func.hour(Sale.time_ended)).all()

    for result in results:
        sale,total,sale_count = result
        date = sale.time_ended

        if date != None:  # non-null date
            hour = date.hour
            date_key = datetime.datetime(date.year, date.month, date.day)

            if hour in range(0,DAY_START_HOUR):        # put hours midnight - start hour on previous day
                date_key -= datetime.timedelta(days=1)

            if date_key in days: # have the day already
                info = days[date_key]
                info.set_hour_sales(hour, float(result[1]), int(result[2]))
            else:   # day not currently there
                info = DailySaleInfo(date_key)
                info.set_hour_sales(hour, float(result[1]), int(result[2]))
                days[date_key] = info
    return days

def get_sales_tax_report(start_date, end_date):
    '''returns info for sales tax reporting '''

    # Indices into the rows returned by the valid_sales_query
    cost = 0
    total = 1
    tax = 2
    payment = 3
    item_id = 4

#    valid_sales_query = filter_valid_sales(reg_session.query(func.sum(SaleItem.cost),func.sum(SaleItem.total), func.sum(SaleItem.tax),Sale.payment, SaleItem.item_id), start_date + datetime.timedelta(hours = 4), end_date + datetime.timedelta(hours=4))

    valid_sales_query = filter_valid_sales(reg_session.query(func.sum(SaleItem.cost),func.sum(SaleItem.total), func.sum(SaleItem.tax),Sale.payment, SaleItem.item_id), start_date, end_date)
 
    sales = valid_sales_query.group_by(Sale.payment).group_by(SaleItem.item_id).all()        # used to get total values appropriately (need to sum differently for LINK sales

#    sales = valid_sales_query.all()
    # print('<hr />')
    # print(TAB_PAYMENT)
    # print(SLUSHFUND)
    # print(CASH_BACK)
    # print(start_date)
    # print(end_date)
    # print( '<hr />')
    # print(len(list(sales)))
    # print( '<hr />')
    # print(valid_sales_query)
    # print( '<hr />')

    # get items that are sold under high and low tax rates
    taxcats = get_tax_categories ()
#    print(taxcats)

    # map() returns a map object in python3, but we're expecting lists
    zero_rate = list(map(to_id,filter (lambda x: x.get_rate() == .0000, taxcats)))
    food_rate = list(map(to_id,filter (lambda x: x.get_rate() == .0225, taxcats)))
    general_rate = list(map(to_id,filter (lambda x: x.get_rate() > .0225, taxcats)))
    soft_drink_rate = list(map(to_id, filter (lambda x: x.get_name() == 'soda', taxcats)))
    # print("<hr />")
    # print("soft drink rate")
    # print(soft_drink_rate)
    # print("<hr />")
    zero_rate_items = inv_session.query(Item).filter(Item.tax_category_id.in_(zero_rate)).all()
    food_rate_items = inv_session.query(Item).filter(Item.tax_category_id.in_(food_rate)).all()
    general_rate_items = inv_session.query(Item).filter(Item.tax_category_id.in_(general_rate)).all()
    soft_drink_rate_items = inv_session.query(Item).filter(Item.tax_category_id.in_(soft_drink_rate)).all()
    # print("<hr />")
    # print("soft drink rate items")
    # print(soft_drink_rate_items)
    # print("<hr />")

    negative_prices = map(to_id, inv_session.query(Price).filter(Price.unit_cost < 0.0).all())
    refund_items = inv_session.query(Item).filter(Item.price_id.in_(negative_prices)).all()

    # Can make these dicts to improve speed if needed
    zero_rate_ids = list(map(to_id, zero_rate_items))
    food_rate_ids = list(map(to_id, food_rate_items))
    general_rate_ids = list(map(to_id, general_rate_items))
    soft_drink_rate_ids = list(map(to_id, soft_drink_rate_items))
    # print("<hr />")
    # print("soft drink rate ids")
    # print(soft_drink_rate_ids)
    # print("<hr />")

    # there are some sales where the item has been deleted or doesn't have a tax_category_id or something...in this case assume 2.25%
    # -SL 5/18/12
    orphan_rate_ids = list(range(10000)) 
    for x in zero_rate_ids + food_rate_ids + general_rate_ids + soft_drink_rate_ids:
      try:
        orphan_rate_ids.remove(x)
      except:
        pass


    refund_item_ids = list(map(to_id, refund_items))

    def link_only (x,y):
        '''returns the sum where x = cost and y = (cost,total,payment) if y is a LINK transaction.
           otherwise returns the orignal value.  the definition of y is given by the valid_sales_query above.'''
        if int(y[payment]) == LINK_PAYMENT:
            return x + float(y[cost])
        return x

    def non_link (x,y):
        '''sim to link_only but only adds if y is NOT a link transaction'''
        if (int(y[payment]) != LINK_PAYMENT):
            return (x[0]+float(y[total]),x[1]+float(y[tax]))
        return x

    def zero_rate (x,y):
        '''sums up sales of items which are in the zerotax category'''
        if int(y[item_id]) in zero_rate_ids and int(y[payment]) != LINK_PAYMENT:
                return (x[0]+float(y[cost]),x[1]+float(y[tax]))
        return x

    def food_rate (x,y):
        '''sums up sales of items which are in the food tax category'''
        if int(y[item_id]) in food_rate_ids and int(y[payment]) != LINK_PAYMENT:
                return (x[0]+float(y[cost]),x[1]+float(y[tax]))
        return x

    def general_rate (x,y):
        if int(y[item_id]) in general_rate_ids and int(y[payment]) != LINK_PAYMENT:
                return (x[0]+float(y[cost]),x[1]+float(y[tax]))
        return x

    def orphan_rate (x,y):
        if int(y[item_id]) in orphan_rate_ids and int(y[payment]) != LINK_PAYMENT:
                return (x[0]+float(y[cost]),x[1]+float(y[tax]))
        return x

    def link_soft_drink (x,y):
        if int(y[item_id]) in soft_drink_rate_ids and int(y[payment] == LINK_PAYMENT):
                return (x+float(y[cost]))
        return x

    def non_link_soft_drink (x,y):
        if int(y[item_id]) in soft_drink_rate_ids and int(y[payment] != LINK_PAYMENT):
                return (x[0]+float(y[cost]),x[1]+float(y[tax]))
        return x
    
    def refunds (x,y):
        if int(y[item_id]) in refund_item_ids:
            return x + float(y[cost])
        return x

    link_sales = reduce (link_only, sales,0)
    non_link_sales, non_link_tax = reduce (non_link, sales,(0,0))   # non_link sales include the tax value !
    food_sales,food_tax = reduce (food_rate, sales,(0,0))
    general_sales,general_tax = reduce (general_rate, sales, (0,0))
    transit_sales,transit_tax = reduce (zero_rate, sales, (0,0))
    orphan_sales,orphan_tax = reduce (orphan_rate, sales, (0,0))
    link_soft_drink_sales = reduce (link_soft_drink, sales, 0)
    non_link_soft_drink_sales,non_link_soft_drink_tax = reduce (non_link_soft_drink, sales, (0,0))
    other_sales = 0

    refund_sales = -1.0 * reduce(refunds,sales,0)  # refund total is negative, so we flip the sign
    # refunds are already included in one of these groups of sales, so we have to add 2*refund_sales in order to
    # get the $ value of everything rung up at the store
    #sales_dollars = link_sales + non_link_sales + 2*refund_sales
    sales_dollars = link_sales + non_link_sales + refund_sales
    # removing the 2x -SL 5/18/12

    deductions = link_sales + food_tax + general_tax + orphan_tax + refund_sales + transit_sales
#     print("sales size")
#     print(len(sales))

# #    soft_drink_sales = filter(lambda x: x[item_id] in soft_drink_rate_ids, sales)
#     print("soft drink sale size")
#     print((soft_drink_sales))
#     print("<hr />")
#     print("soft drink sales")

#     print("link")
#     print(LINK_PAYMENT)

#     # print(list(sales))
#     # print("<hr />")

    s_d_link = link_soft_drink_sales #reduce (link_only, list(soft_drink_sales),0)
    s_d_non_link, s_d_nl_tax = non_link_soft_drink_sales, non_link_soft_drink_tax #reduce (non_link, list(soft_drink_sales), (0,0))
    # print ("<hr />")
    # print ("sd_link")
    # print(s_d_link)
    # print ("<hr />")
    # print ("sd_non_link")
    # print(s_d_non_link)
    s_d_sales_dollars = s_d_link + (s_d_non_link - s_d_nl_tax) * 1.03   # Don't want to count any taxes other than the 3% soft drink tax
    s_d_deductions = s_d_nl_tax + s_d_link
    s_d_taxable = s_d_sales_dollars - s_d_deductions
    s_d_tax = round(s_d_taxable * .03)
    s_d_discount = round(s_d_tax * .0175)
    s_d_payment = s_d_tax - s_d_discount

    return {'total' : sales_dollars, 'deductions' : deductions, 'general_tax' : general_tax, 'food_tax' : food_tax, 'orphan_tax': orphan_tax, 'refunds' : refund_sales, 'transit' : transit_sales, 'link' : link_sales, 'general_sales' : general_sales, 'food_sales' : food_sales, 'orphan_sales' : orphan_sales, 'other_sales' : other_sales, 'non_link':non_link_sales}, {'total' : s_d_sales_dollars, 'deductions' : s_d_deductions, 'taxable' : s_d_taxable, 'taxdue' : s_d_tax, 'discount' : s_d_discount, 'payment' : s_d_payment}

def get_accounts(order_type, start_date=FIRST_SALES,end_date=datetime.datetime.now()):
    '''used by accounts.py and daily_accounts.py.  returns Total Sales and Tab Payments broken down by payment type.  Also returns a list of total cash in.
    order_type should be one of 'monthly' or 'daily' and determines if results are grouped by month or by day
    '''
    sales = filter_valid_sales(reg_session.query(Sale.time_ended,func.sum(SaleItem.cost),func.sum(SaleItem.total), Sale.payment), start_date + datetime.timedelta(hours=4), end_date + datetime.timedelta(hours=4)).group_by(Sale.payment)

    #if order_type == 'monthly':
        #sales = sales.group_by(func.year(Sale.time_ended)).group_by(func.month(Sale.time_ended)).group_by(func.hour(Sale.time_ended))
    #else:
            #commented out because i don't understand it.  -SL 5/18/12
            #oh thanks. -CR 8/03/21
    sales = sales.group_by(func.date(Sale.time_ended)).group_by(func.hour(Sale.time_ended)).group_by(func.hour(Sale.time_ended)).group_by(Sale.time_ended)

    totals = {}
    tabs = {}
    cash_in = {}
    cards_in = {}

    for row in sales.all():
        day = datetime.datetime(row[0].year, row[0].month, row[0].day, row[0].hour)
        if day.hour < DAY_START_HOUR:         # if it happened before 4am put it on the previous day
            day -= datetime.timedelta(days=1)
            if day < start_date:
                continue

        if order_type == 'monthly':
            #day -= datetime.timedelta(days=day.day-1)
            #commented out because i don't understand it.  -SL 5/18/12
            #i think the goal is to group everything on the first day of that month, so:
            day = datetime.datetime(day.year, day.month, 1)

        date_key = day.date()

        if date_key not in totals:
            totals[date_key] = {}
            totals[date_key]['total'] = 0
            for k, v in PAYMENT.items(): # Have to initialize the each payment type for this day to be 0
                totals[date_key][v] = 0
            cash_in[date_key] = 0            # if it's not in the totals dict then it's also not in the cash_in dict
            cards_in[date_key] = 0

        payment_type = int(row[3])
        payment_name = PAYMENT[payment_type]

        
        if payment_name != 'link':     # if we aren't summing link sales then add total
            totals[date_key][payment_name] += float(row[2])
            if payment_name == 'cash':
                cash_in[date_key] += float(row[2])
            if (payment_name == 'debit/credit' or payment_name == 'manual credit/debit' or payment_name == 'paid online'):
                cards_in[date_key] += float(row[2])
            totals[date_key]['total'] += float(row[2])

        else:                                   # otherwise don't include tax when adding
            totals[date_key][payment_name] += float(row[1])
            cards_in[date_key] += float(row[1])
            totals[date_key]['total'] += float(row[1])

    ### End getting sales
    tab_payments = reg_session.query(Sale.time_ended,func.sum(SaleItem.cost),func.sum(SaleItem.total), Sale.payment).filter(and_(Sale.id == SaleItem.sale_id,  Sale.is_void==0, SaleItem.item_id == TAB_PAYMENT, Sale.time_ended > start_date, Sale.time_ended < end_date)).group_by(Sale.payment)

    if order_type == 'monthly':
        tab_payments = tab_payments.group_by(func.year(Sale.time_ended)).group_by(func.month(Sale.time_ended)).group_by(func.hour(Sale.time_ended)).group_by (Sale.time_ended)
    else:
        tab_payments = tab_payments.group_by(func.date(Sale.time_ended)).group_by(func.hour(Sale.time_ended)).group_by(Sale.time_ended)

    for row in tab_payments.all():
        day = datetime.datetime(row[0].year, row[0].month, row[0].day, row[0].hour)
        if day.hour < DAY_START_HOUR:         # if it happened before 4am put it on the previous day
            day -= datetime.timedelta(days=1)
            if day < start_date:
                continue

        if order_type == 'monthly':
            day -= datetime.timedelta(days=day.day-1)

        date_key = day.date()

        if date_key not in tabs:
            tabs[date_key] = {}
            tabs[date_key]['total'] = 0
            for k,v in PAYMENT.items(): # Have to initialize the each payment type for this day to be 0
                tabs[date_key][v] = 0

        payment_type = int(row[3])
        payment_name = PAYMENT[payment_type]
        tabs[date_key][payment_name] += float(row[2])
        tabs[date_key]['total'] += float(row[2])

        if payment_name == 'cash':          # record cash in
            if date_key not in cash_in:
                cash_in[date_key] = 0
            cash_in[date_key] += float(row[2])
        if ((payment_name == 'manual credit/debit') or (payment_name == 'debit/credit') or (payment_name == 'link')):          # record card in 
            if date_key not in cards_in:
                cards_in[date_key] = 0
            cards_in[date_key] += float(row[2])
    ### End getting tab payments
    cash_back = reg_session.query(Sale.time_ended,func.sum(SaleItem.cost),func.sum(SaleItem.total), Sale.payment).filter(and_(Sale.id == SaleItem.sale_id,  Sale.is_void==0, SaleItem.item_id == CASH_BACK, Sale.time_ended > start_date, Sale.time_ended < end_date)).group_by(Sale.payment)

    if order_type == 'monthly':
        cash_back = cash_back.group_by(func.year(Sale.time_ended)).group_by(func.month(Sale.time_ended)).group_by(func.hour(Sale.time_ended)).group_by(Sale.time_ended)
    else:
        cash_back = cash_back.group_by(func.date(Sale.time_ended)).group_by(func.hour(Sale.time_ended)).group_by(Sale.time_ended)

    for row in cash_back.all():
        day = datetime.datetime(row[0].year, row[0].month, row[0].day, row[0].hour)
        if day.hour < DAY_START_HOUR:         # if it happened before 4am put it on the previous day
            day -= datetime.timedelta(days=1)
            if day < start_date:
                continue

        if order_type == 'monthly':
            day -= datetime.timedelta(days=day.day-1)

        date_key = day.date()

        if payment_name == 'cash':          # record cash in
            if date_key not in cash_in:
                cash_in[date_key] = 0
            cash_in[date_key] -= float(row[2])


    return [totals,tabs,cash_in,cards_in]

def get_category_accounts(start_date=FIRST_SALES,end_date=datetime.datetime.now()):
    '''used by and daily_accounts.py.  returns Total Sales broken down by category.  

    '''
    sale_items = filter_valid_sales(reg_session.query(Sale, SaleItem.id,SaleItem.cost,SaleItem.total,Sale.time_ended,SaleItem.quantity,SaleItem.item_id,Sale.payment), start_date + datetime.timedelta(hours=4), end_date + datetime.timedelta(hours=4))

    # sales = filter_valid_sales(reg_session.query(Sale.time_ended,func.sum(SaleItem.cost),func.sum(SaleItem.total), Sale.id), start_date + datetime.timedelta(hours=4), end_date + datetime.timedelta(hours=4))

    # sale_ids = map((lambda si: si[3]), sales.group_by(Sale.time_ended).group_by(Sale.id).limit(10))

    totals = {}
    tabs = {}
    cash_in = {}

#    sale_items = reg_session.query(Sale, SaleItem.item_id, SaleItem.cost,Sale.time_ended, SaleItem.total,SaleItem.quantity).filter(SaleItem.sale_id.in_(sale_ids))
    
    sale_items = sale_items.group_by(func.date(Sale.time_ended)).group_by(func.hour(Sale.time_ended)).group_by(func.hour(Sale.time_ended)).group_by(Sale.time_ended).group_by(Sale.id).group_by(SaleItem.id)


    ids = map((lambda si: si[6]), sale_items.all())


    cat_rows = inv_session.query(Item.id,Category.name,CategoryItem).filter(Item.id.in_(ids)).filter(and_(CategoryItem.item_id == Item.id, Category.id == CategoryItem.cat_id)).all()
    cat_hash = {}
    cats = ['produce', 'bakery', 'wine', 'beer', 'spirits', 'non-produce']
    for cat_row in cat_rows:
        if (cats.__contains__(cat_row[1]) or (not(cat_hash.__contains__(str (cat_row[0]))))):
            cat_hash[str(cat_row[0])] = cat_row[1]


    for row in sale_items.all():
        # print( "----")
        # print("<br />") 
        # print(row)
        day = datetime.datetime(row[4].year, row[4].month, row[4].day, row[4].hour)
        if day.hour < DAY_START_HOUR:         # if it happened before 4am put it on the previous day
            day -= datetime.timedelta(days=1)
            if day < start_date:
                continue

        date_key = day.date()

        if date_key not in totals:
            totals[date_key] = {}
            totals[date_key]['total'] = float(0)

        if cat_hash.__contains__(str(row[6])):

            cat = cat_hash[str(row[6])]
            if cats.__contains__(cat):
                cat_key = cat
            else:
                cat_key = 'non-produce'
        else:
            cat_key = 'non-produce'


        if cat_key not in totals[date_key]:
            totals[date_key][cat_key] = float(0)
            
        payment_type = int(row[7])
        payment_name = PAYMENT[payment_type]


        
        if payment_name != 'link':     # if we aren't summing link sales then add total
            totals[date_key][cat_key] += (float(row[3])) 
            totals[date_key]['total'] += (float(row[3]))
        else:
            totals[date_key][cat_key] += (float(row[2])) 
            totals[date_key]['total'] += (float(row[2]))

    return totals


#####################################################
#
# Classes for interacting with inventory database
#
# Note: the classes that have data imported from marzipan
#  have an optional paramter id in the constructor.
#  This is because I wanted to make sure that the ids from the old
#  database are exactly the same as the ones in the new database
#  if this is ignored then it will be auto-incremented from whatever
#  the previous value was.
#  Classes that are new do not have this as the id should
#  not be set manually.
#  This also holds for classes for register_tape
#
#  Additionally note that the names for variables in the classes
#    need to be the same as the columns in the database
#####################################################

class Item(object):
    """something the store sells"""
    def __init__(self, name, price_id, count, tax_category,
                 plu=None, size="", size_unit=None, is_discontinued=False,last_count=None, id=None, notes=None,description=None,display_name=None):

        self.name = name
        self.price_id = price_id
        self.is_discontinued = is_discontinued
        self.tax_category_id = tax_category
        self.plu = plu
        self.size = size
        self.count = count
        self.display_name = display_name
        self.description = description
        self.last_manual_count = count
        self.notes = notes
        if (last_count != None):
            self.last_manual_count_timestamp = last_count
            self.count_timestamp = last_count
        self.size_unit_id = size_unit
        if id != None:
            self.id = id

    def __repr__(self):
        return "<Item('%s','%s',%s,%d)>"%(
            self.name, self.plu,
            str(self.size),
            self.is_discontinued)

    def __str__(self):
        if self.size_unit_id != None:
            return "%s [%.2f %s]" % (self.name, self.size, units_dict[self.size_unit_id])
        else:
            return "%s []" % self.name

    def get_price_id(self):
        return self.price_id

    def get_id(self):
        return self.id

    def get_name(self):
        return self.name

    def get_display_name(self):
        if self.display_name != None:
            return self.display_name
        else:
            return ''

    def get_weight_string(self):
        if self.weight == None:
            return ''
        else:
            return "%.2f" % self.weight

    def get_description(self):
        if self.description == None:
            return ''
        else:
            return self.description
        
    def get_price(self):
        return float(inv_session.query(Price.unit_cost).filter(Price.id == self.price_id).one()[0])

    
    def get_count(self):
        '''Returns count + (deliveries since count_timestamp) - (sales since last_manual_count_timestamp)
        This will become slow unless count_timestamp is updated on a regular basis'''

        if self.count_timestamp != None:
            count_starting = self.count_timestamp
        else:
            count_starting = MARZIPAN_OPEN

        deliveries = inv_session.query(func.sum(Delivery.amount)).filter(Delivery.item_id == self.id).filter(Delivery.time_delivered > count_starting).one()[0]
        if deliveries == None:
            deliveries = 0

        item_sales = reg_session.query(func.sum(SaleItem.quantity)).filter(and_(SaleItem.sale_id == Sale.id, Sale.time_ended > count_starting, SaleItem.item_id == self.id, Sale.is_void == 0)).one()[0]
        if item_sales == None:
            item_sales = 0
        return int(self.count) + int(deliveries) - int(item_sales) 

    def get_is_discontinued(self):
        return self.is_discontinued

    def get_distributor_count(self):
        '''returns the number of distributors that an item has'''
        return inv_session.query(func.count('*')).filter(DistributorItem.item_id  == self.id).one()[0]

    def get_distributors(self):
        return inv_session.query(DistributorItem).filter(DistributorItem.item_id == self.id).all()

    def get_distributors_str(self):
        distributors = list(map(str,[dist_dict[di.dist_id] for di in self.get_distributors()]))  # convert between the distributor item to distributor then apply str to all of them
        distributors.sort()
        return ','.join(distributors)

    def get_distributor_items(self):
        d_items = inv_session.query(DistributorItem).filter(DistributorItem.item_id == self.id).all()
        return d_items

    def get_distributor_ids_str(self):
        distributors = inv_session.query(DistributorItem.dist_id).filter(DistributorItem.item_id == self.id).all()
        dist_list = [str(d[0]) for d in distributors]
        return ','.join(dist_list)

    def get_barcodes(self):
        return inv_session.query(BarcodeItem).filter(BarcodeItem.item_id == self.id).all()

    def get_unit_size(self):
        return self.size

    def get_size_unit_id(self):
        return self.size_unit_id

    def get_sale_unit_id(self):
        price = get_price(int(self.price_id))
        return price.sale_unit_id

    def get_size_str(self):
        return '''%.2f %s''' % (self.size, units_dict[self.size_unit_id])

    def get_price_str(self):
        price = inv_session.query(Price.unit_cost, Price.sale_unit_id).filter(Price.id == self.price_id).one()
        unit_cost = price[0]
        price_unit = units_dict[price[1]]

        return '''%.2f %s''' % (unit_cost, price_unit)

    def get_first_barcode(self):
        '''returns the first barcode found for this item. necessary so that manage_items doesn't
           haven't to display multiple textboxes'''
        barcodes = inv_session.query(BarcodeItem).filter(BarcodeItem.item_id == self.id).all()
        if barcodes == []:
            return None
        return barcodes[0]

    def get_barcodes_str(self):
        barcodes = self.get_barcodes()
        return ', '.join(map(BarcodeItem.get_barcode, barcodes))

    def get_category_items(self):
        c_items = inv_session.query(CategoryItem).filter(CategoryItem.item_id == self.id).all()
        return c_items

    def get_categories(self):
        return inv_session.query(Category).filter(and_(Category.id == CategoryItem.cat_id, CategoryItem.item_id == self.id)).all() 

    def get_categories_str(self):
        categories = list(map(str,self.get_categories()))
        categories.sort()
        return ','.join(categories)

    def get_tax_category(self):
        if self.tax_category_id == None:
            return ''
        tax_cat = inv_session.query(TaxCategory).filter(TaxCategory.id== self.tax_category_id).one()
        return tax_cat

    def get_tax_value(self):
        price = inv_session.query(Price).filter(Price.id == self.price_id).one()
        tax_rate = inv_session.query(TaxCategory.rate).filter(TaxCategory.id == self.tax_category_id).one()[0]
        return float(price.unit_cost) - float(price.unit_cost)/(1.0 + float(tax_rate))

    def get_deliveries(self):
        '''used when merging items'''
        return inv_session.query(Delivery).filter(Delivery.item_id == self.id).all()

    def get_sale_items(self):
        '''used when merging items'''
        return reg_session.query(SaleItem).filter(SaleItem.item_id == self.id).all()

    def get_notes(self):
        if self.notes == None:
            return ''
        return self.notes

    def set_notes(self, new_notes):
        self.notes = new_notes
        inv_session.flush()

    def set_count(self, newcount):
        '''This is a manual count, so we update all columns'''
        self.count = newcount
        self.count_timestamp = datetime.datetime.now()
        self.last_manual_count = newcount
        self.last_manual_count_timestamp = self.count_timestamp
        inv_session.flush()

    def auto_count(self, newcount):
        '''This is an automatic count, so we do not change last_manual_count'''
        self.count = newcount
        self.count_timestamp = datetime.datetime.now()
        inv_session.flush()

class Price(object):
    """how much money an item costs"""
    def __init__(self, sale_unit, unit_cost, is_tax_flat, id=None):
        self.sale_unit_id = sale_unit
        self.unit_cost = unit_cost
        self.is_tax_flat = is_tax_flat
        if id != None:
            self.id = id

    def __repr__(self):
        return "<Price('%s',%s,%s,%d)>"%(
            self.sale_unit_id, self.unit_cost, self.tax, self.is_tax_flat)
    def get_id(self):
        return self.id
    def get_unit_cost(self):
        return self.unit_cost
    def get_sale_unit_id(self):
        return self.sale_unit_id

class SaleUnit(object):
    """measure by which item is sold"""
    def __init__(self, name, type, id=None):
        self.name = name
        self.unit_type = type
        if id != None:
            self.id = id

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.name

    def get_id(self):
        return self.id

    def get_time_ended(self):
        return self.get_time_ended

    def get_name(self):
        return self.name

class PriceChange(object):
    """alteration of price (possibly due to special)"""
    def __init__(self, old_price, new_price, special=None, id=None):
        self.old_price = old_price
        self.new_price = new_price
        self.special = special
        if id != None:
            self.id = id

    def __repr__(self):
        return "<PriceChange(%s,%s,%d)>"%(
            self.old_price, self.new_price, self.special_id)

class Special(object):
    """named set of price changes"""
    def __init__(self, name, is_active=True, id=None):
        self.name = name
        self.is_active = is_active
        if id != None:
            self.id = id

    def __repr__(self):
        return "<Special('%s',%d)>"%(self.name, self.is_active)

    def __str__(self):
        return self.name

class Clerk(object):
    """person who sells stuff"""
    def __init__(self, name, is_valid=True, id=None):
        self.name = name
        self.is_valid = is_valid
        if id != None:
            self.id = id

    def __str__(self):
        return self.name

class Delivery(object):
    """logging when stuff gets delivered - hasn't been used correctly"""
    def __init__(self, time_delivered, item_id, amount, dist_id=None, id=None):
        self.time_delivered = time_delivered
        self.item_id = item_id
        self.amount = amount
        self.dist_id = dist_id
        if id != None:
            self.id = id

    def get_time_delivered(self):
        return self.time_delivered

    def get_amount(self):
        return self.amount

class Category(object):
    """a category for grouping items"""
    def __init__(self, name, id=None):
        self.name = name
        if id != None:   # otherwise will auto-increment
            self.id = id

    def get_name(self):
        return self.name

    def get_id(self):
        return self.id

    def __str__(self):
        return self.name

# Begin new classes for tables not found in marzipan
class CategoryItem(object):
    """one item of a particular category"""
    def __init__(self, item_id, cat_id):
        self.item_id = item_id
        self.cat_id = cat_id

    def get_id(self):
        return self.id

    def get_cat_id(self):
        return self.cat_id

class TaxCategory(object):
    """categories for taxing items"""
    def __init__(self, name, rate):
        self.name = name
        self.rate = rate
    def __str__(self):
        return '%s (%.2f%%)' % (self.name, self.rate*100)
    def get_name(self):
        return self.name
    def get_rate(self):
        return float(self.rate)
    def get_id(self):
        return self.id

class Distributor(object):
    """someone who delivers items to the store"""
    def __init__(self,name, phone="", id=None):
        self.name = name
        self.phone = phone
        if id != None:
            self.id = id

    def __str__(self):
        return self.name
    def get_id(self):
        return self.id
    def get_name(self):
        return self.name
    def get_phone(self):
        return self.phone

class DistributorItem(object):
    """one item from a distributor"""
    def __init__(self, item_id, dist_id, dist_item_id=0, wholesale_price=0, case_size=0, case_unit_id=1,id=None):
        self.item_id = item_id
        self.dist_id = dist_id
        self.dist_item_id = dist_item_id
        self.wholesale_price = wholesale_price
        self.case_size = case_size
        self.case_unit_id = case_unit_id
        if id != None:
            self.id = id

    def __str__(self):
        return '%s. Dist Item ID: %s. Case: $%.2f for %.2f %s.' % (dist_dict[self.dist_id], self.dist_item_id, self.wholesale_price, self.case_size, units_dict[self.case_unit_id])

    def get_item_id(self):
        return self.item_id

    def get_dist_id(self):
        return self.dist_id

    def get_distributor(self):
        return dist_dict[self.dist_id]

    def get_id(self):
        return self.id

    def get_dist_item_id(self):
        return self.dist_item_id

    def set_dist_item_id(self,newid):
        self.dist_item_id = newid
        inv_session.flush()

    def get_wholesale_price(self):
        return self.wholesale_price

    def get_case_size(self):
        return self.case_size

    def get_case_unit_id(self):
        return self.case_unit_id

    def get_case_unit(self):
        unit = inv_session.query(SaleUnit).filter(SaleUnit.id == self.case_unit_id)
        if unit.all() ==[]:
            return ''
        return unit.one()

    def get_each_cost(self):
        if self.case_size != 0:
            return float(self.wholesale_price / self.case_size)
        else:
            return 0

class BarcodeItem(object):
    """item<->barcode mapping"""
    def __init__(self, item_id, barcode, id=None):
        self.item_id = item_id
        self.barcode = barcode
        if id != None:
            self.id = id

    def __str__(self):
        return self.barcode

    def get_barcode(self):
        return self.barcode

    def get_id(self):
        return self.id

#####################################################
#
# Classes for interacting with register_tape database
# All of these have a corresponding something in marzipan
#
#####################################################
class Sale(object):
    """transaction where customer exchanges items for payment"""
    def __init__(self, clerk_id, customer_id, id=None, items=[], payment=0, is_void=False,
                 total=Decimal('0.00'),time_started=datetime.datetime.now(),time_ended=None,
                 cc_trans='', cc_last4='', cc_name=''):
        self.clerk_id = clerk_id
        self.items = items
        self.customer_id = customer_id
        self.payment = payment
        self.is_void = is_void
        self.total = total
        self.time_started = time_started
        self.time_ended = time_ended
        self.cc_trans = cc_trans
        self.cc_last4 = cc_last4
        self.cc_name = cc_name
        if id != None:
            self.id = id

    def __str__(self):
        return str(self.time_ended)

    def get_customer_id(self):
        return self.customer_id

    def get_time_ended(self):
        return self.time_ended

    def get_payment(self):
        return self.payment

class SaleItem(object):
    """record of item exchanged in a sale"""
    def __init__(self, sale, item, quantity, unit_cost,
                 cost, tax, total, is_refund=False):
        self.sale = sale
        self.item_id = item
        self.quantity = quantity
        self.unit_cost = unit_cost
        self.cost = cost
        self.tax = tax
        self.total = total
        self.is_refund = is_refund

    def __str__(self):
        return '%d, %.2f' %(self.item_id,self.quantity)

    def get_unit_cost(self):
        return self.unit_cost

    def get_cost(self):
        return self.cost

    def get_quantity(self):
        return  self.quantity

class Customer(object):
    """someone who buys stuff"""
    def __init__(self, code="", name="", email="", tel="",
        postal="", balance=Decimal('0.00'), credit=Decimal('0.00'), id=None):
        self.name = name
        self.code = code
        self.email = email
        self.tel = tel
        self.postal = postal
        self.balance = balance
        self.credit = credit
        if id != None:
            self.id = id

class TabLog(object):
    """record of a customer's tab"""
    def __init__(self, cust_id, old_balance=None, new_balance=None,when_logged=None, id=None):
        self.customer_id = cust_id
        self.old_balance = old_balance
        self.new_balance = new_balance
        self.when_logged = when_logged
        if id != None:
            self.id = id

class ItemCountLog(object):
    """record of an item's count changing either manually, or deducted via POS"""
    def __init__(self, item_id, old_count=None, new_count=None,when_logged=None, id=None,is_manual_count=0):
        self.item_id = item_id
        self.old_count = old_count
        self.new_count = new_count
        self.is_manual_count = is_manual_count
        self.when_logged = when_logged
        if id != None:
            self.id = id

    def get_when_logged(self):
        return self.when_logged

    def get_diff(self):
        if self.old_count != None:
            return self.new_count - self.old_count
        return self.new_count

    def get_is_manual_count(self):
        return self.is_manual_count

    def get_counts(self):
        # Added check that old_count is not NULL which happens when the item is new
        if self.old_count == None:
            old = 0
        else:
            old = self.old_count
        return (old,self.new_count)

# After making any changes/queries etc with the session objects, need to do session.flush() to save the changes
reg_engine = create_engine(register_tape_loc)#,echo=True)
reg_session = sessionmaker(bind=reg_engine)()

register_md = MetaData(reg_engine)

sales = Table('sales', register_md,
              Column('id',Integer, primary_key=True),
              Column('clerk_id',Integer), #, ForeignKey('inventory.clerks.id')
              Column('customer_id',Integer), #, ForeignKey('customers.id')),
              Column('payment',Integer),
              Column('is_void',Boolean),
              Column('total',Numeric(8,2)),
              Column('time_started',DateTime),
              Column('time_ended',DateTime),
              Column('cc_trans',String(18)),
              Column('cc_last4',String(4)),
              Column('cc_name',String(64))
              )

sale_items = Table('sale_items', register_md,
                   Column('id',Integer, primary_key=True),
                   Column('sale_id',Integer, ForeignKey('sales.id'), nullable=False),
                   Column('item_id',Integer, nullable=False), # ForeignKey('items.id')
                   Column('quantity',Numeric(10,4)),
                   Column('unit_cost',Numeric(10,4)),
                   Column('cost',Numeric(8,2), nullable=False),
                   Column('tax',Numeric(8,2), nullable=False),
                   Column('total',Numeric(8,2), nullable=False),
                   Column('is_refund',Boolean, nullable=False),
                   )

customers = Table('customers', register_md,
                  Column('id',Integer, primary_key=True),
                  Column('code',String(13), nullable=False),
                  Column('name',String(255), nullable=False),
                  Column('email',String(255),default=None),
                  Column('tel',String(16),default=None),
                  Column('postal',String(1024),default=None),
                  Column('balance',Numeric(8,2),default=0.00),
                  Column('credit',Numeric(8,2),default=None),
                  )

tab_log = Table('tab_log', register_md,
                Column('id',Integer,primary_key=True),
                Column('customer_id',Integer,nullable=False),
                Column('old_balance',Numeric(8,2),default=None),
                Column('new_balance',Numeric(8,2)),
                Column('when_logged',DateTime)
                )


mapper(Sale, sales)
mapper(SaleItem, sale_items)
mapper(Customer, customers)
mapper(TabLog,tab_log)

register_md.create_all()


inv_engine = create_engine(inventory_loc)#,echo=True)
inv_md = MetaData(inv_engine)

items = Table('items', inv_md,
              Column('id', Integer, primary_key=True),
              Column('name',String(255), nullable=False),
              Column('price_id',Integer, ForeignKey('prices.id'), nullable=False),
              Column('tax_category_id',Integer, ForeignKey('tax_categories.id'), nullable=False),
              Column('plu',String(5)),
              Column('size',Numeric(8,4)),
              Column('size_unit_id',Integer, ForeignKey('sale_units.id')),
              Column('count', Integer, nullable=False),
              Column('count_timestamp',DateTime),
              Column('last_manual_count',Integer),
              Column('last_manual_count_timestamp',DateTime),
              Column('is_discontinued',Boolean, nullable=False),
              Column('notes', Text),
              Column('display_name', Text),
              Column('weight', Numeric(8,4)),
              Column('description', Text),
              Column('popularity', Integer)
              )

prices = Table('prices', inv_md,
               Column('id',Integer, primary_key=True),
               Column('sale_unit_id',Integer, ForeignKey('sale_units.id'),       nullable=False),
               Column('unit_cost',Numeric(10,4), nullable=False),
               Column('is_tax_flat',Boolean, nullable=False)
               )

sale_units = Table('sale_units', inv_md,
                   Column('id',Integer, primary_key=True),
                   Column('name',String(20), nullable=False),
                   Column('unit_type',Integer, nullable=False)
                   )

price_changes = Table('price_changes', inv_md,
                      Column('id',Integer, primary_key=True),
                      Column('old_price_id',Integer, nullable=False),
                      Column('new_price_id',Integer, nullable=False),
                      Column('special_id',Integer, ForeignKey('specials.id'))
                      )

specials = Table('specials', inv_md,
                 Column('id',Integer, primary_key=True),
                 Column('name',String(255), nullable=False),
                 Column('is_active',Boolean, nullable=False)
                 )

clerks = Table('clerks', inv_md,
               Column('id',Integer, primary_key=True),
               Column('name',String(255), nullable=False),
               Column('is_valid',Boolean)
               )

deliveries = Table('deliveries', inv_md,
                   Column('id',Integer, primary_key=True),
                   Column('time_delivered',DateTime),
                   Column('item_id',Integer, nullable=False),
                   Column('amount',Numeric(8,2)),
                   Column('dist_id',Integer, ForeignKey("distributors.id"))
                   )

tax_categories = Table('tax_categories', inv_md,
                       Column('id',Integer, primary_key=True),
                       Column('name',String(255), nullable=False),
                       Column('rate',Numeric(4,4))
                       )

distributors = Table('distributors', inv_md,
                     Column('id',Integer, primary_key=True),
                     Column('name',String(255), nullable=False),
                     Column('phone',String(10))
                     )

categories = Table('categories', inv_md,
                   Column('id',Integer, primary_key=True),
                   Column('name',String(255), nullable=False)
                   )

category_items = Table('category_items', inv_md,
                       Column('id',Integer, primary_key=True),
                       Column('item_id',Integer,  ForeignKey('items.id'),nullable=False),
                       Column('cat_id',Integer, ForeignKey('categories.id'),nullable=False)
                       )

distributor_items = Table('distributor_items', inv_md,
                          Column('id',Integer, primary_key=True),
                          Column('item_id',Integer, ForeignKey('items.id'), nullable=False),
                          Column('dist_id',Integer, ForeignKey('distributors.id'), nullable=False),
                          Column('dist_item_id', Integer),
                          Column('wholesale_price', Numeric(8,2)),
                          Column('case_size', Numeric(8,2)),
                          Column('case_unit_id',Integer, ForeignKey('sale_units.id'))
                          )

barcode_items = Table('barcode_items', inv_md,
                      Column('id', Integer, primary_key=True),
                      Column('item_id', Integer, ForeignKey('items.id'),nullable=False),
                      Column('barcode', String(16))
                      )

item_count_log = Table('item_count_log', inv_md,
                       Column('id', Integer, primary_key=True),
                       Column('item_id',Integer,ForeignKey('items.id'),nullable=False),
                       Column('old_count', Integer,default=None),
                       Column('new_count', Integer),
                       Column('is_manual_count',Integer),
                       Column('when_logged', DateTime)
                       )

# map classes to the tables defined above
mapper(Item, items, properties = {'categories' :
                                  relation(Category,secondary=category_items,
                                           primaryjoin=items.c.id==category_items.c.item_id,
                                           secondaryjoin=category_items.c.cat_id==categories.c.id,
                                           foreign_keys=[category_items.c.item_id,category_items.c.cat_id]),
                                  'distributors' :
                                  relation(Distributor, secondary=distributor_items,
                                           primaryjoin=items.c.id==distributor_items.c.item_id,
                                           secondaryjoin=distributor_items.c.dist_id==distributors.c.id,
                                           foreign_keys=[distributor_items.c.item_id,distributor_items.c.dist_id])

})
mapper(ItemCountLog, item_count_log)
mapper(Price, prices)
mapper(PriceChange,price_changes)
mapper(SaleUnit,sale_units)
mapper(BarcodeItem,barcode_items)
mapper(Category, categories)
mapper(CategoryItem, category_items)
mapper(Clerk, clerks)
mapper(Delivery, deliveries)
mapper(Special, specials)
mapper(Distributor, distributors)
mapper(DistributorItem,distributor_items)
mapper(TaxCategory, tax_categories)

inv_md.create_all()

inv_session = sessionmaker(bind=inv_engine)()

# To reduce queries to the database we cache some things in memory
# Eg Item.__str__ needs to query the database to get unit names, but instead we use the units_dict to get the unit_name
#  by looking up item.size_unit_id
units_objs = get_units()
units_dict = dict( [(int(si.get_id()), si.get_name()) for si in units_objs])

dist_objs = get_distributors()
dist_dict = dict ([(int(d.get_id()), d) for d in dist_objs])
