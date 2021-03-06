# -*- coding: utf8 -*-
"""
.. module:: lesscpy.plib.variable
    :synopsis: Variable declaration
    
    Copyright (c)
    See LICENSE for details.
.. moduleauthor:: Jóhann T. Maríusson <jtm@robot.is>
"""
from .node import Node

class Variable(Node):
    def parse(self, scope):
        """ Parse function
        args:
            scope (Scope): Scope object
        returns:
            self
        """
        self.name, _, self.value = self.tokens
        if type(self.name) is tuple:
            if len(self.name) > 1:
                self.name, pad = self.name
                self.value.append(pad)
            else:
                self.name = self.name[0]
        scope.add_variable(self)
    
    def fmt(self, fills):
        return ''
        
