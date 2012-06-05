from __future__ import with_statement
# -*- coding: utf8 -*-
"""
.. module:: lesscpy.scripts.compiler
    CSS/LESSCSS run script

    http://lesscss.org/#docs
    
    Copyright (c)
    See LICENSE for details
.. moduleauthor:: Jóhann T. Maríusson <jtm@robot.is>
"""
import os
import sys
import glob
import copy
import optparse
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
from lesscpy.lessc import parser
from lesscpy.lessc import lexer
from lesscpy.lessc import formatter

VERSION_STR = 'Lesscpy compiler 0.9d'

def ldirectory(inpath, outpath, options, scope):
    """Compile all *.less files in directory
    Args:
        inpath (str): Path to compile
        outpath (str): Output directory
        options (object): Argparse Object
        scope (Scope): Scope object or None
    """
    yacctab = 'yacctab' if options.debug else None
    if not outpath:
        sys.exit("Compile directory option needs -o ...")
    else:
        if not os.path.isdir(outpath):
            if options.verbose:
                print("Creating '%s'" % outpath)
            if not options.dry_run:
                os.mkdir(outpath)
    less = glob.glob(os.path.join(inpath, '*.less'))
    f = formatter.ArgsFormatter(options)
    for lf in less:
        outf = os.path.splitext(os.path.basename(lf))
        minx = '.min' if options.min_ending else ''
        outf = "%s/%s%s.css" % (outpath, outf[0], minx) 
        if not options.force and os.path.exists(outf):
            recompile = os.path.getmtime(outf) < os.path.getmtime(lf)
        else: 
            recompile = True
        if recompile:
            print('%s -> %s' % (lf, outf))
            p = parser.LessParser(yacc_debug=(options.debug),
                                  lex_optimize=True,
                                  yacc_optimize=(not options.debug),
                                  scope=scope,
                                  tabfile=yacctab,
                                  verbose=options.verbose)
            p.parse(filename=lf, debuglevel=0)
            css = f.format(p)
            if not options.dry_run:
                with open(outf, 'w') as outfile:
                    outfile.write(css)
        elif options.verbose: print('skipping %s, not modified' % lf)
        sys.stdout.flush()
    if options.recurse:
        [ldirectory(os.path.join(inpath, name), os.path.join(outpath, name), args, scope) 
         for name in os.listdir(inpath) 
         if os.path.isdir(os.path.join(inpath, name))
         and not name.startswith('.')
         and not name == outpath]
#
#    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# 
def run():
    """Run compiler
    """
    aparse = optparse.OptionParser(description='LessCss Compiler', 
                                     epilog='<< jtm@robot.is @_o >>', 
                                     version=VERSION_STR)
    aparse.add_option('-I', '--include', action="store", type=str,
                        help="Included less-files (comma separated)")
    aparse.add_option('-V', '--verbose', action="store_true", 
                        default=False, help="Verbose mode")
    fgroup = aparse.add_option_group('Formatting options')
    fgroup.add_option('-x', '--minify', action="store_true", 
                        default=False, help="Minify output")
    fgroup.add_option('-X', '--xminify', action="store_true", 
                        default=False, help="Minify output, no end of block newlines")
    fgroup.add_option('-t', '--tabs', help="Use tabs", action="store_true")
    fgroup.add_option('-s', '--spaces', help="Number of startline spaces (default 2)", default=2)
    dgroup = aparse.add_option_group('Directory options', 
                                       'Compiles all *.less files in directory that '
                                       'have a newer timestamp than it\'s css file.')
    dgroup.add_option('-o', '--out', action="store", help="Output directory")
    dgroup.add_option('-r', '--recurse', action="store_true", help="Recursive into subdirectorys")
    dgroup.add_option('-f', '--force', action="store_true", help="Force recompile on all files")
    dgroup.add_option('-m', '--min-ending', action="store_true", 
                        default=False, help="Add '.min' into output filename. eg, name.min.css")
    dgroup.add_option('-D', '--dry-run', action="store_true", 
                        default=False, help="Dry run, do not write files")
    group = aparse.add_option_group('Debugging')
    group.add_option('-g', '--debug', action="store_true", 
                        default=False, help="Debugging information")
    group.add_option('-S', '--scopemap', action="store_true", 
                        default=False, help="Scopemap")
    group.add_option('-L', '--lex-only', action="store_true", 
                        default=False, help="Run lexer on target")
    group.add_option('-N', '--no-css', action="store_true", 
                        default=False, help="No css output")
    aparse.add_option('--target', help="less file or directory")
    options, args = aparse.parse_args()
    
    try:
        #
        #    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # 
        if options.lex_only:
            lex = lexer.LessLexer()
            ll = lex.file(options.target)
            while True:
                tok = ll.token()
                if not tok: break
                print(tok)
            print('EOF')
            sys.exit()
        #
        #    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # 
        yacctab = 'yacctab' if options.debug else None
        scope = None
        if options.include:
            for u in options.include.split(','):
                if os.path.exists(u):
                    p = parser.LessParser(yacc_debug=(options.debug),
                                          lex_optimize=True,
                                          yacc_optimize=(not options.debug),
                                          tabfile=yacctab,
                                          verbose=options.verbose)
                    p.parse(filename=u, debuglevel=0)
                    if not scope:
                        scope = p.scope
                    else:
                        scope.update(p.scope)
                else:
                    sys.exit('included file `%s` not found ...' % u)
                sys.stdout.flush()
        p = None
        f = formatter.ArgsFormatter(options)
        if not os.path.exists(options.target):
            sys.exit("Target not found '%s' ..." % options.target)
        if os.path.isdir(options.target):
            ldirectory(options.target, options.out, options, scope)     
            if options.dry_run:
                print('Dry run, nothing done.')  
        else:
            p = parser.LessParser(yacc_debug=(options.debug),
                                  lex_optimize=True,
                                  yacc_optimize=(not options.debug),
                                  scope=copy.deepcopy(scope),
                                  verbose=options.verbose)
            p.parse(filename=options.target, debuglevel=0)
            if options.scopemap:
                options.no_css = True
                p.scopemap()
            if not options.no_css and p:
                out = f.format(p)
                print(out)
    except (KeyboardInterrupt, SystemExit, IOError):
        sys.exit('\nAborting...')
    