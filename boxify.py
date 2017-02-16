#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SYNOPSIS

    python3 boxify.py

DESCRIPTION

    Concisely describe the purpose this script serves.

EXAMPLE

    $ python3 boxify.py
    ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
    ┃                                                                              ┃
    ┃ In west Philadelphia, born and raised! on the playground was where I spent   ┃
    ┃ most of my days. Chillin' out, maxin', relaxin' all cool, and all shootin'   ┃
    ┃ some b-ball outside of the school when a couple of guys who were up to no    ┃
    ┃ good started making trouble in my neighborhood. I got in one little fight    ┃
    ┃ and my mom got scared. She said 'You're movin' with your auntie and uncle in ┃
    ┃ Bel Air'.                                                                    ┃
    ┃                                                                              ┃
    ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

AUTHOR

    Doug McGeehan <djmvfb@mst.edu>


LICENSE

    GNU GPLv3


TODO

    Allow files to be read in.
    Allow files to be written out.
    Add command-line arguments to specify box type.
    Given multiple paragraphs, don't throw away newlines.
    Given text with tabs or spaces of importance (e.g. "O_Captain!_My_Captain!"
        by Walt Whitman), preserve whitespaces.
    Add more box types for other existing box unicode characters.

"""

class Defaults(object):
    default_max_line_length = 80
    default_border_width = 0
    default_padding_width = 1


class TextBox(object):
    # Note: all spaces in this class are Em Spaces (U+2003)
    border_char = ' '

    def __init__(self, paragraph=None,
                       max_line_length=Defaults.default_max_line_length,
                       border_width=Defaults.default_border_width,
                       padding_width=Defaults.default_padding_width):
        assert 9 == len(self.box), '{class}.chars static variable'\
                                   ' is not 3x3'.format(
                                   self.__class__.__name__)
        self.max_line_length = max_line_length
        self.border_width = border_width
        self.padding_width = padding_width
        self.paragraph = paragraph if paragraph is not None else ''

        ( self.top_left,
          self.top_center,
          self.top_right,
          self.line_prefix,
          self.line_pad,
          self.line_suffix,
          self.bottom_left,
          self.bottom_center,
          self.bottom_right ) = self.box

        self.unpadded_internal_line_length = max_line_length \
                                           - (self.padding_width+1)*2 
        self.padded_internal_line_length = max_line_length - 2

    def boxify(self, long_lines=None):
        if long_lines is None:
            return str(self)
        
        self.long_lines = long_lines
        return str(self)

    def __str__(self):
        box = [
            self._top_line(),
            *self._boxified_horizontal_padding_lines(),
            *[ self._boxify_line(l) 
               for l in self._paragraph_to_compliant_lines() ],
            *self._boxified_horizontal_padding_lines(),
            self._bottom_line(),
        ]
        return '\n'.join(box)

    def _paragraph_to_compliant_lines(self):
        words = self.paragraph.split()
        lines = []
        line = words.pop(0)
        while words:
            word = words.pop(0)
            if len(line) + 1 + len(word) > self.unpadded_internal_line_length:
                lines.append(line)
                line = word
            else:
                line = '{line} {word}'.format(line=line, word=word)
        lines.append(line)
        return lines

    ##########################################################################
    # Barriers
    def _top_line(self):
        return self._horizontal_barrier(self.top_left,
                                        self.top_center,
                                        self.top_right)

    def _bottom_line(self):
        return self._horizontal_barrier(self.bottom_left,
                                        self.bottom_center,
                                        self.bottom_right)

    def _horizontal_barrier(self, left_corner, center_char, right_corner):
        """
        border left_corner pad center_line pad right_corner
        |--------------------- max_line_length -----------|
        """
        center_line_length = self.max_line_length - 2 - self.border_width
        line ='{b}{lc}{center}{rc}'.format(
            b=' '*self.border_width,
            lc=left_corner,
            center=center_char*center_line_length,
            rc=right_corner)
        assert self._compliant_line(line)
        return line

    #
    ##########################################################################

    ##########################################################################
    # Padding
    def _boxified_horizontal_padding_lines(self):
        return [ self._boxify_line(line=self.line_pad)\
                 for i in range(self.padding_width) ]

    def _pad_line(self, line):
        """Padded line inside of the box"""
        assert self.unpadded_internal_line_length >= len(line),\
               'Line too long for inside of box:\n'\
               '  expected = {0}\n'\
               '  actual   = {1}\n'\
               '\t"{2}"'.format(self.unpadded_internal_line_length,
                                len(line),
                                line)
        return '{padding}{filled_line}{padding}'.format(
            padding=self._padding(),
            filled_line=line.ljust(self.unpadded_internal_line_length)
        )

    def _horizontal_padded_line(self):
        """Goes above or below our textual content, but is inside the box"""
        return self.line_pad*self._internal_padded_line_length

    def _padding(self):
        return self.line_pad*self.padding_width
    #
    ##########################################################################

    ##########################################################################
    # Boxifying
    def _boxify_line(self, line):
        return '{border}{prefix}{padded_line}{suffix}'.format(
            border=self._border(),
            prefix=self.line_prefix,
            padded_line=self._pad_line(line),
            suffix = self.line_suffix)

    def _border(self):
        return self.border_char*self.border_width

    def _compliant_line(self, line):
        actual_length = len(line)
        if self.max_line_length != actual_length:
           if self.max_line_length < actual_length:
                descriptor = 'long'
           else:
                descriptor = 'short'

           error_msg = 'Line is too {descriptor}:\n'\
                        '    expected = {exp}\n'\
                        '    actual = {act}\n'\
                        '"{line}"'.format(descriptor=descriptor,
                                          exp=self.max_line_length,
                                          act=actual_length,
                                          line=line)
           return False, error_msg

        else:
            return True, None
    #
    ##########################################################################


class HeavyTextBox(TextBox):
    box = '┏━┓'\
          '┃ ┃'\
          '┗━┛'

    def __init__(self, *args, **kwargs):
        super(HeavyTextBox, self).__init__(*args, **kwargs)


class LightTextBox(TextBox):
    box = '┌─┐'\
          '│ │'\
          '└─┘'
 
    def __init__(self, *args, **kwargs):
        super(LightTextBox, self).__init__(*args, **kwargs)

# TODO: A lot of the ones below can be subclasses of the two ones above.
# They share corners or sides.
class HeavyDoubleDashTextBox(TextBox):
    box = '┏╍┓'\
          '╏ ╏'\
          '┗╍┛'

    def __init__(self, *args, **kwargs):
        super(HeavyDoubleDashTextBox, self).__init__(*args, **kwargs)


class LightDoubleDashTextBox(TextBox):
    box = '┌╌┐'\
          '╎ ╎'\
          '└╌┘'

    def __init__(self, *args, **kwargs):
        super(LightDoubleDashTextBox, self).__init__(*args, **kwargs)


class HeavyTripleDashTextBox(TextBox):
    box = '┏┅┓'\
          '┇ ┇'\
          '┗┅┛'
    def __init__(self, *args, **kwargs):
        super(HeavyTripleDashTextBox, self).__init__(*args, **kwargs)


class LightTripleDashTextBox(TextBox):
    box = '┌┄┐'\
          '┆ ┆'\
          '└┄┘'

    def __init__(self, *args, **kwargs):
        super(LightTripleDashTextBox, self).__init__(*args, **kwargs)


class HeavyQuadDashTextBox(TextBox):
    box = '┏┉┓'\
          '┋ ┋'\
          '┗┉┛'

    def __init__(self, *args, **kwargs):
        super(HeavyQuadDashTextBox, self).__init__(*args, **kwargs)


class LightQuadDashTextBox(TextBox):
    box = '┌┈┐'\
          '┊ ┊'\
          '└┈┘'

    def __init__(self, *args, **kwargs):
        super(LightQuadDashTextBox, self).__init__(*args, **kwargs)


class DoubleBarTextBox(TextBox):
    box = '╔═╗'\
          '║ ║'\
          '╚═╝'

    def __init__(self, *args, **kwargs):
        super(DoubleBarTextBox, self).__init__(*args, **kwargs)


class ArcCornerTextBox(TextBox):
    box = '╭─╮'\
          '│ │'\
          '╰─╯'

    def __init__(self, *args, **kwargs):
        super(ArcCornerTextBox, self).__init__(*args, **kwargs)



DefaultTextBox = HeavyTextBox
def it(paragraph=None, line_length=Defaults.default_max_line_length):
    if paragraph is None:
        paragraph = ''
    return DefaultTextBox(paragraph=paragraph, max_line_length=line_length)


if __name__ == '__main__':
    import sys
    if 1 < len(sys.argv):
        n = int(sys.argv[-1])
    else:
        n = Defaults.default_max_line_length

    paragraph = "In west Philadelphia, born and raised! On the playground was where I spent most of my days. Chillin' out, maxin', relaxin' all cool, and all shootin' some b-ball outside of the school when a couple of guys who were up to no good started making trouble in my neighborhood. I got in one little fight and my mom got scared. She said 'You're movin' with your auntie and uncle in Bel Air'."
    print(it(paragraph=paragraph, line_length=n))
