#!/usr/bin/env python
# 1/31/2011
# Patrick McQuighan

# This file is part of Marzipan, an open source point-of-sale system.
# Copyright (C) 2011 Open Produce LLC
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# This is sort of an experimental class thing where I try to prevent myself from typing out the
# same sort of javascript a million times.  
#The first class here is a simple KeyHandler class
# which is supposed to print out a javascript function (which I use all over the place) which
# when the enter key is pressed will take the value from the textbox, and the id # from the
# textbox's .id field and pass that to one of the update_ scripts and then do something on 
# a succesfull update

# Instead of passing a whole bunch of params like '' have macros eg NO_ARGS, EMPTY_FUNC

TEXTBOX_VALUE = 0
TEXTBOX_ID = 1
ENTER_KEY = 13

SELECT_VALUE = 0
SELECT_ID = 1

class KeyHandler():
    def __init__(self,name, doc, key_pressed, post_to, 
                 post_vars,on_success,element):
        '''post_vars is a dictionary of var_name : string which gets passed to post_to as post_to?var_name=string
        element is the corresponding CLASS name to which this handler is added'''
        self.documentation = doc
        self.name = name
        self.key_pressed = key_pressed
        self.post_to = post_to
        self.post_vars = post_vars
        self.on_success = on_success
        self.element = element 

    def print_function(self):
        to_print = ''
        to_print += '''
//%s''' % self.documentation
        to_print += '''
function %s(e) {''' % self.name
        to_print += '''
  if (e.which == %d) {''' % self.key_pressed
        to_print += '''
    var box = this;
    box.disabled = true;
    $(box).removeClass('default').removeClass('complete').addClass('submitting');
    var value = this.value;
    var id = parseInt(this.id);'''
        to_print += '''
    $.post('%s', {''' % self.post_to
        varcount = len(self.post_vars.keys())
        for i,(varname,value) in enumerate(self.post_vars.iteritems()):
            if value == TEXTBOX_VALUE:
                to_print += '''%s:%s''' % (varname,'value')
            elif value == TEXTBOX_ID:
                to_print += '''%s:%s''' % (varname,'id')
            else:
                to_print += '''%s:'%s' ''' % (varname,value)
            if i + 1 < varcount:
                to_print += ','
        to_print += '''},'''
        to_print += '''
      function(data){
        box.disabled = false;
        if(data.indexOf('Error:') != -1) { alert(data);}
        else{ $(box).removeClass('default').removeClass('submitting').addClass('complete'); %s}''' % self.on_success
        to_print += '''
      },'text');
  }
  setTimeout(function(box) { $(box).removeClass('submitting').removeClass('complete').addClass('default');}, 4000, box);
}'''
        print to_print

    def print_ready(self):
        print '''  $('.%s').keypress(%s); ''' % (self.element, self.name)


class SelectHandler():
    def __init__(self,name,doc,post_to,post_vars,on_success,element):
        ''' here element is the id of a html select element '''
        self.documentation = doc
        self.name = name
        self.post_to = post_to
        self.post_vars = post_vars
        self.on_success = on_success
        self.element = element 
    
    def print_function(self):
        to_print = ''
        to_print += '''
// %s ''' % self.documentation
        to_print += '''
function %s(){''' % (self.name)
        to_print += '''
  var id = parseInt(this.id);
  var selected = this.value;'''
        to_print += '''
  $.post('%s', { ''' % self.post_to
        varcount = len(self.post_vars.keys())
        for i,(varname,value) in enumerate(self.post_vars.iteritems()):
            if value == SELECT_VALUE:
                to_print += '''%s:%s''' % (varname,'selected')
            elif value == SELECT_ID:
                to_print += '''%s:%s''' % (varname,'id')
            else:
                to_print += '''%s:'%s' ''' % (varname,value)
            if i + 1 < varcount:
                to_print += ','
        to_print += '''},'''
        to_print += '''
    function(data){
      if(data.indexOf('Error:') != -1) { alert(data); }'''
        to_print += '''
      else { %s}''' % self.on_success
        to_print += '''
    }, 'text');
}'''
        print to_print

    def print_ready(self):
        print '''  $('.%s').change(%s); ''' % (self.element,self.name)
