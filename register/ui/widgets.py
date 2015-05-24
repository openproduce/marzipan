#!/usr/bin/env python
import curses
import curses.panel
import curses.ascii
from font import big34
from colors import *
from keys import *
from layout import add_frame

class Widget:
    """a widget is a ui element that reacts to input and draws itself."""
    def __init__(self, name, y, x, width, height, color_id=0):
        self.name = name
        self.y = y # frame (window)-relative
        self.x = x
        self.base_width = self.width = width
        self.base_height = self.height = height
        self.color_id = color_id

        # these are set by the Frame constructor.
        self.frame = None
        self.layout = None
        self.selected = False

    def has_children(self):
        return False

    def accepts_input(self):
        return True # most widgets accept input, labels do not.

    def input(self, c):
        assert 'unimplemented'

    def grow(self, dw, dh):
        pass

    def show(self):
        assert 'unimplemented'


def _dec_wrap(x, n):
    if x == 0:
        return n
    return x - 1

def _inc_wrap(x, n):
    if x == n:
        return 0
    return x + 1

class Frame:
    """frames group widgets, track focus and focus order."""
    V_BORDER = 1
    H_BORDER = 1

    def __init__(self, widgets, layout, border=True):
        (self.h_border, self.v_border) = (Frame.H_BORDER, Frame.V_BORDER)
        if not border:
            (self.h_border, self.v_border) = (0, 0)

        self.focus_order = widgets
        self.focus_index = None
        self.set_focus_first()

        self.widgets = {}
        self.layout = layout
        for widget in widgets:
            widget.frame = self
            widget.layout = self.layout
            if widget.name is not None:
                self.widgets[widget.name] = widget
            if widget.has_children():
                for child in widget.children():
                    child.x += self.h_border
                    child.y += self.v_border
            widget.y += self.v_border
            widget.x += self.h_border

        add_frame(self)
        self._pack()

    def _pack(self):
        (self.width, self.height) = (0, 0)
        for widget in self.focus_order:
            self.width = max(widget.x + widget.width, self.width)
            self.height = max(widget.y + widget.height, self.height)
        self.width = self.width+1 + 2 * self.h_border
        self.height = self.height + 2 * self.v_border
        self.layout.set_base_size(self.width, self.height)
        self.layout.pack()

    def get(self, name):
        return self.widgets[name]

    def set_focus_first(self):
        for i, widget in enumerate(self.focus_order):
            if widget.accepts_input():
                self.focus_index = i
                widget.selected = True
                return True
        return False

    def set_focus(self, widget):
        if widget is None:
            if self.focus_index is not None:
                self.focus_order[self.focus_index].selected = False
            self.focus_index = None
        else:
            for i in xrange(0,len(self.widgets)):
                if self.focus_index is None:
                    break
                if self.focus_order[self.focus_index] == widget:
                    return True
                self.set_focus_next()
        return False

    def get_focus(self):
        if self.focus_index is not None:
            return self.focus_order[self.focus_index]
        return None

    def search_new_focus(self, iterate):
        if not self.focus_order or self.focus_index is None:
            return False # nothing to focus _on_ or no old focus.
        next = iterate(self.focus_index)
        while not self.focus_order[next].accepts_input():
            if next == self.focus_index:
                return False # nothing else to focus on.
            next = iterate(next)

        # mark next widget in focus order as selected.
        self.focus_order[self.focus_index].selected = False
        self.focus_order[next].selected = True
        self.focus_index = next
        return True

    def set_focus_prev(self):
        return self.search_new_focus(
            lambda x: _dec_wrap(x, len(self.focus_order) - 1))

    def set_focus_next(self):
        return self.search_new_focus(
            lambda x: _inc_wrap(x, len(self.focus_order) - 1))

    def input(self, c):
        focus = self.get_focus()
        if focus is not None:
            focus.input(c)

    def show(self):
        if self.layout.fill:
            for y in xrange(0, self.layout.height-1):
                self.layout.window.addstr(y, 0, " "*self.layout.width,
                    curses.color_pair(FRAME_BG))
                if self.h_border:
                    self.layout.window.addstr(y, 0, '|',
                        curses.color_pair(FRAME_BG))
                    self.layout.window.addstr(y, self.layout.width-1, '|',
                        curses.color_pair(FRAME_BG))
            if self.v_border:
                self.layout.window.addstr(0, 0, "-"*self.layout.width,
                    curses.color_pair(FRAME_BG))
                self.layout.window.addstr(self.height-2, 0,
                    "-"*self.layout.width,
                    curses.color_pair(FRAME_BG))
            self.layout.fill = False

        for widget in self.focus_order:
            widget.show()


class Label(Widget):
    """a label is just some text.  it's only a type of widget
       so that it can piggyback on the generalized drawing support
       for groups of widgets."""
    def __init__(self, y, x, width, text, color_id=LABEL_COLOR,
        name=None, height=1):
        # width = num_chars
        Widget.__init__(self, name, y, x, width, height, color_id)
        self.set_text(text)

    def _pad_line(self, line):
        if self.width > len(line):
            return line + ' '*(self.width - len(line))
        else:
            return line[0:self.width]

    def set_text(self, text):
        i = 0
        self.lines = []
        for line in text.split('\n'):
            self.lines.append(self._pad_line(line))
            i = i + 1
        for j in xrange(i,self.height):
            self.lines.append(self._pad_line(''))

    def get_text(self):
        return '\n'.join(self.lines)

    def accepts_input(self):
        return False

    def input(self, c):
        assert 'labels should not get input'

    def show(self):
        for i, line in enumerate(self.lines):
            self.layout.window.addstr(self.y+i, self.x, line,
                curses.color_pair(self.color_id))


class CheckBox(Widget):
    """binary selection."""
    LEFT_MARGIN = 4

    def __init__(self, name, y, x, width, text, state=False,
        color_id=LABEL_COLOR, height=1):
        Widget.__init__(self, name, y, x, width, height, color_id)
        self.state = state
        self.set_text(text)

    def _pad_line(self, line):
        width = max(self.width, CheckBox.LEFT_MARGIN)
        if width > len(line):
            return line + ' '*(width - len(line))
        else:
            return line[0:width-CheckBox.LEFT_MARGIN]

    def set_state(self, state):
        self.state = state

    def get_state(self):
        return self.state

    def set_text(self, text):
        i = 0
        self.lines = []
        for line in text.split('\n'):
            self.lines.append(self._pad_line(line))
            i = i + 1
        for j in xrange(i,self.height):
            self.lines.append(self._pad_line(''))

    def accepts_input(self):
        return True

    def input(self, c):
        if c == ord(' '):
            self.state = not self.state
        elif c == KEY_TAB or c == KEY_RETURN or c == curses.KEY_ENTER or \
             c == curses.KEY_DOWN or c == curses.KEY_RIGHT:
            if self.frame:
                self.frame.set_focus_next()
        elif c == curses.KEY_UP or c == curses.KEY_LEFT:
            if self.frame:
                self.frame.set_focus_prev()

    def show(self):
        self.layout.window.addstr(self.y, self.x, '[ ] ',
            curses.color_pair(self.color_id))
        x_color_id = self.color_id
        if self.selected:
            x_color_id = ACTIVE_SEL_COLOR
        if self.state:
            self.layout.window.addstr(self.y, self.x+1, 'X',
                curses.color_pair(x_color_id))
        else:
            self.layout.window.addstr(self.y, self.x+1, ' ',
                curses.color_pair(x_color_id))
        for i, line in enumerate(self.lines):
            self.layout.window.addstr(self.y+i, self.x + CheckBox.LEFT_MARGIN,
                line, curses.color_pair(self.color_id))


class ScrollDimension:
    """generic logic for marching a scroll cursor through a
       virtual window from [0,virt_size-1] within a physical window
       of size [0,real_size-1]"""

    def __init__(self, real_size, virtual_size,
        leading_context=0, trailing_context=0):
        self.real_size = real_size
        self.virtual_size = virtual_size
        self.base = 0
        self.offset = 0
        self.leading_context = leading_context
        self.trailing_context = trailing_context

    def set_virtual_size(self, max):
        self.virtual_size = max

    def get(self):
        return self.base + self.offset

    def home(self):
        self.base = 0
        self.offset = 0

    def end(self):
        if self.virtual_size > self.real_size:
            self.base = self.virtual_size - self.real_size
            self.offset = self.real_size - 1
        else:
            self.base = 0
            self.offset = self.virtual_size - 1

    def prev(self):
        if self.base == 0 and self.offset == 0:
            return False
        elif self.offset > self.leading_context:
            self.offset -= 1
        elif self.base > 0:
            self.base -= 1
        elif self.offset > 0:
            self.offset -= 1
        return True

    def next(self):
        if self.get() >= self.virtual_size - 1:
            return False
        elif self.offset < self.real_size - self.trailing_context:
            self.offset += 1
        elif self.base < self.virtual_size - self.real_size:
            self.base += 1
        elif self.offset < self.real_size-1:
            self.offset += 1
        return True

    def scrollby(self, n):
        if n >= 0:
            for k in xrange(n):
                self.next()
        else:
            for k in xrange(abs(n)):
                self.prev()


class ListBox(Widget):
    """a list box displays a scrollable list of labels"""
    TOP_CONTEXT = 2 # entries to keep on top when scrolling up
    BOTTOM_CONTEXT = 2 # entries to keep on bottom when scrolling down

    def __init__(self, name, y, x, width, height, label_kv,
        color_id=TEXT_ENTRY_COLOR, sel=None, label_height=1):
        Widget.__init__(self, name, y, x, width, height*label_height,
            color_id)
        self.label_height = label_height
        self.set_labels(label_kv)
        self.hit_enter = False
        if sel is not None:
            self.set_selection(sel)

    def accepts_input(self):
        return len(self.labels) != 0

    def has_children(self):
        return True

    def children(self):
        return self.labels

    def set_labels(self, label_kv):
        self.labels = []
        i = 0
        for key, s in label_kv:
            label = Label(i, self.x, self.width, s, self.color_id,
                height=self.label_height)
            label.key = key
            self.labels.append(label)
            i += 1
        self.scroll = ScrollDimension(self.height/self.label_height,
            len(label_kv),
            leading_context=ListBox.TOP_CONTEXT,
            trailing_context=ListBox.BOTTOM_CONTEXT)

    def delete_label(self, key):
        index = None
        for i, label in enumerate(self.labels):
            if label.key == key:
                index = i
                break
        if index is not None:
            del(self.labels[index])
            self.scroll.prev()
            self.scroll.virtual_size -= 1

    def set_selection(self, key):
        scrolled = True
        (orig_base, orig_offs) = (self.scroll.base, self.scroll.offset)
        self.scroll.base = self.scroll.offset = 0
        while scrolled and key != self.labels[self.scroll.get()].key:
            scrolled = self.scroll.next()
        found = key == self.labels[self.scroll.get()].key
        if not found: # restore scroll position
            (self.scroll.base, self.scroll.offset) = (orig_base, orig_offs)
        return found

    def grow(self, dw, dh):
        self.width += dw
        self.height += dh
        self.scroll.physical_size = self.height/self.label_height
        for lbl in self.labels:
            lbl.width += dw
            lbl.set_text(lbl.get_text())

    def get_selection(self):
        if self.labels:
            return self.labels[self.scroll.get()].key
        return None

    def get_hit_enter(self):
        return self.hit_enter

    def reset_hit_enter(self):
        self.hit_enter = False

    def input(self, c):
        if c == curses.KEY_UP:
            self.scroll.prev()
            if not self.labels and self.frame:
                self.frame.set_focus_prev()
        elif c == curses.KEY_DOWN:
            self.scroll.next()
            if not self.labels and self.frame:
                self.frame.set_focus_next()
        elif c == curses.KEY_NPAGE or c == curses.KEY_RIGHT:
            self.scroll.scrollby(10)
            if not self.labels and self.frame:
                self.frame.set_focus_next()
        elif c == curses.KEY_PPAGE or c == curses.KEY_LEFT:
            self.scroll.scrollby(-10)
            if not self.labels and self.frame:
                self.frame.set_focus_next()
        elif c == KEY_TAB:
            if self.frame:
                self.frame.set_focus_next()
        elif c == curses.KEY_ENTER or c == KEY_RETURN:
            self.hit_enter = True
            if self.frame:
                self.frame.set_focus_next()

    def show(self):
        vis_labels = self.height/self.label_height
        first = self.scroll.base
        last = min(len(self.labels), first + vis_labels)
        for i, label in enumerate(self.labels[first:last]):
            label.y = self.y + (i*self.label_height)
            label.layout = self.layout
            if i == self.scroll.offset:
                if self.selected:
                    label.color_id = ACTIVE_SEL_COLOR
                else:
                    label.color_id = INACTIVE_SEL_COLOR
            else:
                label.color_id = self.color_id
            label.show()

        while last-first < vis_labels: # pad list up to height.
            for i in xrange(0,self.label_height):
                self.layout.window.addstr(self.y +
                    self.label_height*(last-first) + i,
                    self.x, self.width*' ',
                    curses.color_pair(self.color_id))
            last += 1


class TextBox(Widget):
    """single-line text entry field with keyboard movements"""
    LEFT_CONTEXT = 3 # characters to keep when scrolling left
    RIGHT_CONTEXT = 3

    def __init__(self, name, y, x, width, text="",
        color_id=TEXT_ENTRY_COLOR, clear_on_insert=False):
        Widget.__init__(self, name, y, x, width, 1, color_id)
        self.scroll = ScrollDimension(width, 1 + len(text),
            leading_context=TextBox.LEFT_CONTEXT,
            trailing_context=TextBox.RIGHT_CONTEXT)
        self.text = text
        self.clear_on_insert = clear_on_insert
        self.hit_enter = False

    def set_text(self, text):
        self.text = text
        self.adjust_size()
        self.scroll.home()

    def get_text(self):
        return self.text

    def get_hit_enter(self):
        return self.hit_enter

    def reset_hit_enter(self):
        self.hit_enter = False

    def adjust_size(self):
        self.scroll.set_virtual_size(
            1 + len(self.text)) # leave room for 1 new character.

    def delete_char(self, pos):
        if pos >= 0 and pos < len(self.text):
            self.text = self.text[0:pos] + self.text[pos+1:]
            self.adjust_size()
            return True
        return False

    def insert_char(self, c):
        if self.clear_on_insert:
            self.set_text('')
        pos = self.scroll.get()
        self.text = self.text[0:pos] + c + self.text[pos:]
        self.adjust_size()
        self.scroll.next()

    def input(self, c):
        if c == curses.KEY_RIGHT or c == KEY_CTRL_F:
            self.scroll.next()
        elif c == curses.KEY_LEFT or c == KEY_CTRL_B:
            self.scroll.prev()
        elif c == curses.KEY_HOME or c == KEY_CTRL_A:
            self.scroll.home()
        elif c == curses.KEY_END or c == KEY_CTRL_E:
            self.scroll.end()
        elif c == curses.KEY_BACKSPACE or c == KEY_CTRL_H:
            if self.delete_char(self.scroll.get() - 1):
                self.scroll.prev()
        elif c == curses.KEY_DC or c == KEY_CTRL_D:
            self.delete_char(self.scroll.get())
        elif c == curses.KEY_DL or c == KEY_CTRL_K:
            pos = self.scroll.get()
            self.text = self.text[0:pos]
            self.adjust_size()
        elif c == KEY_CTRL_U:
            pos = self.scroll.get()
            self.text = self.text[pos:]
            self.adjust_size()
            self.scroll.home()
        elif c == curses.KEY_ENTER or c == KEY_RETURN:
            self.hit_enter = True
            self.scroll.home()
            if self.frame:
                self.frame.set_focus_next()
        elif c == curses.KEY_DOWN or c == KEY_TAB:
            self.scroll.home()
            if self.frame:
                self.frame.set_focus_next()
        elif c == curses.KEY_UP:
            self.scroll.home()
            if self.frame:
                self.frame.set_focus_prev()
        elif curses.ascii.isprint(c):
            self.insert_char(chr(c))
        self.clear_on_insert = False
        # debug:
        #else:
        #    self.layout.window.addstr(self.y + 1, self.x, str(c))

    def show(self):
        first = self.scroll.base
        last = min(len(self.text), first + self.width)
        padding = max(self.width - (last - first), 0)
        text = self.text[first:last] + ' '*padding
        self.layout.window.addstr(self.y, self.x, text,
            curses.color_pair(self.color_id))
        if self.selected: # show terminal cursor at insertion point.
            curs = ' '
            if len(self.text) < self.scroll.get():
                curs = self.text[self.scroll.get()]
            self.layout.window.addstr(self.y, self.x + self.scroll.offset,
                curs, curses.color_pair(ACTIVE_SEL_COLOR))


class Searcher(TextBox):
    """textbox ganged to listbox displaying incremental search results."""

    def __init__(self, name, y, x, width, height, label_kv,
            text="", color_id=TEXT_ENTRY_COLOR):
        TextBox.__init__(self, name, y, x, width, text, color_id)
        self.matches = ListBox(name+'_results', y+2, x,
            width, height, label_kv, color_id)
        self.height = self.base_height = 2+height
    
    def has_children(self):
        return True

    def children(self):
        wl = [self.matches]
        wl.extend(self.matches.labels)
        return wl

    def get_hit_enter(self):
        return self.matches.get_hit_enter()

    def reset_hit_enter(self):
        self.matches.reset_hit_enter()

    def get_selection(self):
        return self.matches.get_selection()

    def set_labels(self, label_kv):
        self.matches.set_labels(label_kv)

    def grow(self, dw, dh):
        self.matches.grow(dw, dh)

    def input(self, c):
        if c == curses.KEY_UP or c == curses.KEY_DOWN or\
           c == curses.KEY_ENTER or c == KEY_RETURN:
            self.matches.frame = self.frame
            self.matches.input(c)
        else:
            TextBox.input(self, c)

    def show(self):
        TextBox.show(self)
        self.matches.selected = self.selected
        self.matches.layout = self.layout
        self.matches.show()


class BigNumberBox(Widget):
    """enter numbers in big font."""

    def __init__(self, name, y, x, width, text="", color_id=TEXT_ENTRY_COLOR,
            font=big34, clear_on_insert=False):
        Widget.__init__(self, name, y, x,
            width*(font.kern+font.width),
            font.height, color_id)
        self.scroll = ScrollDimension(width, 1 + len(text),
            leading_context=0, trailing_context=1)
        self.clear_on_insert = clear_on_insert
        self.font = font
        self.text = text
        self.hit_enter = False

    def set_text(self, text):
        self.text = text

    def get_text(self):
        return self.text

    def get_hit_enter(self):
        return self.hit_enter

    def reset_hit_enter(self):
        self.hit_enter = False

    def adjust_size(self):
        self.scroll.set_virtual_size(len(self.text)+1) # overstrike

    def delete_char(self, pos):
        if pos >= 0 and pos < len(self.text):
            self.text = self.text[0:pos] + self.text[pos+1:]
            self.adjust_size()
            return True
        return False

    def insert_char(self, c):
        if self.clear_on_insert:
            self.set_text('')
        pos = self.scroll.get()
        text = list(self.text)
        if pos < len(text):
            text[pos] = c
        else:
            text.append(c)
        self.text = ''.join(text)
        self.adjust_size()
        self.scroll.next()

    def input(self, c):
        if c == curses.KEY_RIGHT or c == KEY_CTRL_F:
            self.scroll.next()
        elif c == curses.KEY_LEFT or c == KEY_CTRL_B:
            self.scroll.prev()
        elif c == curses.KEY_HOME or c == KEY_CTRL_A:
            self.scroll.home()
        elif c == curses.KEY_END or c == KEY_CTRL_E:
            self.scroll.end()
        elif c == curses.KEY_BACKSPACE or c == KEY_CTRL_H:
            if self.delete_char(self.scroll.get() - 1):
                self.scroll.prev()
        elif c == curses.KEY_DC or c == KEY_CTRL_D:
            self.delete_char(self.scroll.get())
        elif c == curses.KEY_DL or c == KEY_CTRL_K:
            pos = self.scroll.get()
            self.text = self.text[0:pos]
            self.adjust_size()
        elif c == KEY_CTRL_U:
            pos = self.scroll.get()
            self.text = self.text[pos:]
            self.adjust_size()
            self.scroll.home()
        elif c == curses.KEY_ENTER or c == KEY_RETURN:
            self.hit_enter = True
            self.scroll.home()
            if self.frame:
                self.frame.set_focus_next()
        elif c == curses.KEY_DOWN or c == KEY_TAB:
            self.scroll.home()
            if self.frame:
                self.frame.set_focus_next()
        elif c == curses.KEY_UP:
            self.scroll.home()
            if self.frame:
                self.frame.set_focus_prev()
        elif (ord('0') <= c <= ord('9')) or c == ord('.'):
            self.insert_char(chr(c))
        self.clear_on_insert = False
        # debug:
        #else:
        #    self.layout.window.addstr(self.y + 1, self.x, str(c))

    def show(self):
        first = self.scroll.base
        last = min(len(self.text), first +\
            self.width/(self.font.width+self.font.kern))
        padding = max(self.width/(self.font.width+self.font.kern) -\
            (last - first), 0)
        text = self.text[first:last] + ' '*padding
        for i in xrange(0, len(text)):
            x = i * (self.font.width + self.font.kern)
            color_id = self.color_id
            if self.selected and i == self.scroll.offset:
                color_id = ACTIVE_SEL_COLOR
            for y in xrange(0, self.font.height):
                self.layout.window.addstr(self.y+y, self.x+x,
                self.font.get_row(text[i], y)+' '*self.font.kern,
                    curses.color_pair(color_id))


def _center(text, width):
    n = len(text)
    if width <= n:
        return text[0:width]

    left_pad = width/2 - n/2
    right_pad = width - left_pad - n
    return ' '*left_pad + text + ' '*right_pad


class Button(Widget):
    """buttons select an action"""

    def __init__(self, name, y, x, width, text, color_id=BUTTON_COLOR):
        Widget.__init__(self, name, y, x, width, 1, color_id)
        self.text = text
        self.is_pushed = False

    def set_text(self, text):
        self.text = text

    def get_text(self):
        return self.text

    def get_pushed(self):
        return self.is_pushed

    def reset_pushed(self):
        self.is_pushed = False

    def input(self, c):
        if c == KEY_TAB or c == curses.KEY_RIGHT or c == curses.KEY_DOWN:
            if self.frame:
                self.frame.set_focus_next()
        elif c == curses.KEY_LEFT or c == curses.KEY_UP:
            if self.frame:
                self.frame.set_focus_prev()
        elif c == curses.KEY_ENTER or c == KEY_RETURN:
            self.is_pushed = True

    def show(self):
        text = _center(self.text, self.width)
        if self.selected:
            color_id = ACTIVE_SEL_COLOR
        else:
            color_id = self.color_id
        self.layout.window.addstr(self.y, self.x, text, curses.color_pair(color_id))


