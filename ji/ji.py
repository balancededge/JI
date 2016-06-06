# Author: Eric Buss (ejrbuss@shaw.ca) June 2016
title = """
          ______
         // /  _/
    __  // // /    A Java shell and lightweight build tool
   // /_/ // /                Version 0.0.3
   \\\\____/___/
"""
#======================================================================================================================#
# IMPORTS
#======================================================================================================================#
import re
import os
import sys
import subprocess
#======================================================================================================================#
# CONFIGURATION
#======================================================================================================================#
# This is the directory that will be used by JI to store code created while running the interpretor. Expressions and
# functions will be evaluated and defined in a JI.java file which can be viewed after use. Class definitions will create
# additional .java files.
dir = os.path.join(os.path.dirname(__file__), 'tmp')
# This should be the path to your javac.exe file located in your JDK bin (typically C:/Program Files/jdk/bin ). If the
# JDK bin has been added to the PATH environment variable you can just use "javac".
javac = 'javac'
# This should be the path to your java.exe file located in your JDK bin (typically C:/Program Files/jdk/bin ). If the
# JDK bin has been added to the PATH environment variable you can just use "java".
java = 'java'
# Disable color display for terminals that do not cooperate with colorama.
nocolor = False
# Enable debug to print details while parsing.
debug = False
#======================================================================================================================#
# DEPENDENCIES
#======================================================================================================================#
try:
    import colorama
except ImportError:
    exit('JI requires colorama to run. To install colorama run:\n\t\pip install colorama')
#======================================================================================================================#
# GLOBALS
#======================================================================================================================#
# The template format for JI.java
template = """
`imports`
public class JI {

    public static void main( String[] args ) {
        `statements`
        `expression`
    }

    `methods`
}
"""
#======================================================================================================================#
# API
#======================================================================================================================#
def ji(args=None):
    """
    Takes a list of .java files. Compiles the list of files and if all files compiled successfully runs the first file
    in the list. If the list is empty this function will start up a CodeInstance similar to the Python interpreter.

    :param args: A list of .java files
    """
    if args:
        compiled = True
        for file in args:
            compiled &= run(javac + ' ' + file, colorama.Fore.MAGENTA) == 0
        if compiled:
            run(java + ' ' + args[0].replace('.java', ''), colorama.Fore.GREEN)
    else:
        ci = CodeInstance()
        while True:
            ci.listen()

def log(arg):
    """
    Prints the passed arg when in debug mode. Debug messages appear in read.

    :param arg: The debug message
    """
    if debug:
        color_print(colorama.Fore.RED, arg)

def color_print(color, arg, newline=True):
    """
    Prints the passed arg with a given foreground color from colorama. The foreground color will be reset after the arg
    has been printed. By default a newline will be added after the arg but this can be disabled by setting newline to
    False.

    :param color: The foreground color to print arg in
    :param arg: The message to print
    :param newline: A flag indicating if a newline should be appended to arg
    """
    if nocolor:
        sys.stdout.write(arg + ('\n' if newline else ''))
    else:
        sys.stdout.write(color + arg + colorama.Fore.RESET + ('\n' if newline else ''))

def run(cmd, color=colorama.Fore.RESET, cwd=os.curdir):
    """
    Runs a command using subprocess. A color can be specified for the output of the command and it will be reset when
    the function returns. Returns the exit code of the command.

    :param cmd: The command to run
    :param color: The color to display the output in
    :param cwd: The cwd of the command
    :return: The command's exit code
    """
    if nocolor:
        exit_code = subprocess.call(cmd, cwd=cwd)
    else:
        sys.stdout.write(color)
        exit_code = subprocess.call(cmd, cwd=cwd)
        sys.stdout.write(colorama.Fore.RESET)
    return exit_code

class CodeInstance:
    """
    A class that manages Java code to simulate a Java interpreter.
    """

    def __init__(self):
        """
        Initializes a new CodeInstance with no imports, statements, or methods.
        """
        self._nested_ = 0
        self._buffer_ = ''
        self._imports_ = ''
        self._cached_imports_ = ''
        self._statements_ = ''
        self._cached_statements_ = ''
        self._expression_ = ''
        self._methods_ = ''
        self._cached_methods_ = ''
        self._source_ = {'': str(self)}

    def __repr__(self):
        return str(template
            .replace('`imports`', self._imports_)
            .replace('`statements`', self._statements_.replace('\n', '\n\t\t').expandtabs(4))
            .replace('`expression`', self._expression_.replace('\n', '\n\t\t').expandtabs(4))
            .replace('`methods`', self._methods_.replace('\n', '\n\t').expandtabs(4))
        )

    def listen(self):
        """
        Listens to the command line and parses the response. Will collect multi-line Java definitions (classes, methods)
        together and then calls out() to send the input to a file, javac() to compile all the relevant .java files, and
        java() to run the main JI class.
        """
        color_print(colorama.Fore.MAGENTA, '>>', newline=False)
        line = str(input()).rstrip()
        self._buffer_ += line + '\n'
        if line.strip().endswith('}') or line.strip().startswith('}'):
            self._nested_ -= 1
        if line.strip().endswith('{'):
            self._nested_ += 1
        if self._nested_ == 0 and not re.match(r'\s*((if)|(for)|(while))\s*\(.*\)\s*', line):
            self.out()
            self.javac()
            self.java()
        log('nested[' + str(self._nested_) + ']')

    def out(self):
        """
        Checks the first line of the buffer to see where it should be sent to file. If it is an import it is added to
        the top of the JI.java file. If it is a method it is added as a method to the JI.java file. If it is a class
        it is given its own file. The source and exit functions are also checked for here, source() returns the source
        code of a class or function with the given name, exit() ends the JI process.
        """
        pop = self._buffer_.split('\n')[0].strip()
        if re.match(r'(source)|(src)\(.*\);?', pop):
            identifier = re.sub(r'.*\((.*)\);?', r'\1', pop).strip()
            log('source[' + pop + ']')
            color_print(colorama.Fore.GREEN, self._source_[identifier].expandtabs(4), newline=False)
            self._buffer_ = ''
        elif re.match(r'(clr)|(clear)|(clear\(\));?', pop):
            self._statements_ = ''
            self._cached_statements_ = ''
            self._expression_ = ''
            self._buffer_ = ''
        elif re.match(r'(exit)|(exit\(\))|(System.exit\(\));?', pop):
            color_print(colorama.Fore.MAGENTA, '\n\tGoodbye ^.^')
            exit()
        elif re.match(r'\s*import.*;', pop):
            imports = re.sub(r'\s*import\s*(.*);', r'\1', pop)
            log('import[' + imports + ']')
            self._imports_ += self._buffer_ + '\n'
            self._expression_ = ''
        elif not re.match(r'(if)|(for)|(do)|(while).*', pop) and re.match(r'.*\(.*\)\s*\{', pop):
            method_name = re.sub(r'.*\s+(.*)\(.*', r'\1', pop)
            log('method[' + method_name + ']')
            self._methods_ += self._buffer_ + '\n'
            self._source_[method_name] = self._buffer_
            self._expression_ = ''
        elif re.match(r'.*((class)|(interface))\s+.*\{', pop):
            class_name = re.sub(r'.*((class)|(interface))\s+([^\s]*)\s*.*\{', r'\4', pop)
            log('class[' + class_name + ']')
            self._source_[class_name] = self._buffer_
            with open(dir + '/' + class_name + '.java', 'w') as writer:
                writer.write(self._buffer_)
            if run(javac + ' ' + class_name + '.java', colorama.Fore.MAGENTA, cwd=dir) != 0:
                os.remove(os.path.join(dir, file))
            self._expression_ = ''
        else:
            self._expression_ = self._buffer_.rstrip()

    def javac(self):
        """
        Fills the code template with imports, statements, and expressions. Compiles all necessary .java files.
        Expressions are identified as strings not ending in a semicolon. Statements are identified as strings ending in
        a semicolon. All class files are recompiled. If JI.java fails to compile the last successful imports, methods,
        and statements (cached) are retrieved and recompiled.
        """
        if self._expression_.endswith(';') or self._expression_.endswith('}'):
            log('statement[ ' + self._expression_ + ']')
            self._statements_ += self._expression_ + '\n'
            self._expression_ = 'System.out.println();'
        elif self._expression_.strip().startswith('if'):
            log('expression[' + self._expression_ + ']')
            self._expression_ = self._expression_.split('\n')[0] + '\n\tSystem.out.println( ' + self._expression_.split('\n')[1] + ' );'
        else:
            log('expression[' + self._expression_ + ']')
            self._expression_ = 'System.out.println( ' + self._expression_ + ' );'
        with open(dir + '/JI.java', 'w') as writer:
            writer.write(str(self))
        if run(javac + ' JI.java', colorama.Fore.MAGENTA, dir) != 0:
            self._imports_ = self._cached_imports_
            self._methods_ = self._cached_methods_
            self._statements_ = self._cached_statements_
            self._expression_ = ''
            self.javac()

    def java(self):
        """
        Runs JI.class. If the code returns an exit code other than 0 the last successful imports, methods, and
        statements (cached) are retrieved.
        """
        if run(java + ' JI', colorama.Fore.GREEN, dir) != 0:
            self._imports_ = self._cached_imports_
            self._methods_ = self._cached_methods_
            self._statements_ = self._cached_statements_
        self._cached_imports_ = self._imports_
        self._cached_methods_ = self._methods_
        self._cached_statements_ = self._statements_
        self._buffer_ = ''
        self._source_[''] = str(self)
#======================================================================================================================#
# SCRIPT
#======================================================================================================================#
if __name__ == '__main__':
    # Parse command line options
    if '-q' not in sys.argv and '--quiet' not in sys.argv:
        colorama.init()
        color_print(colorama.Fore.MAGENTA, title)
    if '-v' in sys.argv or '--version' is sys.argv:
        exit()
    if '-h' in sys.argv or '--help' in sys.argv:
        color_print(colorama.Fore.MAGENTA, """
        Usage: $ ji [options][java files...]

    -v --version      Print the version number
    -q --quiet        Run in quiet mode
    -a --all          Compile all .java files in the cwd
    -d --debug        Enable debug mode
        """)
        exit()
    if '-a' in sys.argv or '--all' in sys.argv:
        for file in [file for file in os.listdir(os.path.curdir) if str(file).endswith('.java')]:
            run(javac + ' ' + file, colorama.Fore.MAGENTA)
    if '-d' in sys.argv or '--debug' in sys.argv:
        debug = True
    ji([arg for arg in sys.argv if str(arg).endswith('.java')])
