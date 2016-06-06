<pre style='background: #404040; color: #c84080; font-family: consolas, monospace; font-weight: bold;'>
          ______
         // /  _/  
    __  // // /    A Java shell and lightweight build tool  
   // /_/ // /                Version 0.0.3  
   \\____/___/  
   
</pre>

Java Interrupted or JI is a lightweight build tool that provides a shell for running short Java
scripts similar to the Python shell. Additionally JI can be used to quickly compile and run
local Java files. In practice this means you can do stuff like
```java
>>int[] A = {1, 2, 3,4 };
>>A.length
4
>>
```
and this
```bash
$ ji --quiet Example.java
Hello World
```

## Installation

JI expects you to be running python 3 or later. Additionally the colorama package is required. 
You can install colorama with pip
```bash
$ pip install colorama
```
JI has no tother dependencies!

## Configuration

To test to see if the default configuration of JI is right for you open a terminal in the directory
where you installed JI
```bash
$ pwd
.../ji
```
Navigate to the code folder
```bash
$ cd ji
```
And run the Example.java file
```bash
$ python ji.py --quiet Example.java
```
If you see the words "Hello World" you are in the clear! Otherwise you are going to have to open up
ji.py and change adjust some variables in the configuration section at the top of the file. This should
only be necessary if javac.exe and java.exe are not in your PATH. See the description of each configuration
variable in ji.py for more details.

## Usage

JI has a small set of command line options 

- `-h` or `--help` displays a list of the command line options
- `-v` or `--version` displays the version number
- `-q` or `--quiet` disables the ascii title and version number
- `-a` or `--all` will compile all .java files in the cwd 
- `-d` or `--debug` will enable debug printouts

To start the JI shell run the command
```bash
$ python ji.py 
```
The following sections detail how to write expressions, statments, methods, and classes in the shell.

#### Expressions

An expression can be any piece of Java code that has a toString method. If you type a Java expression without
a semicolon the expression will automatically be echoed back at you from the command line. For example

```java
>>1 + 2 * 3
7
```

Expressions are discarded after they are evaluated. **Note:** if you change mutable data in an expression 
it will revert after the expression is evaluated. This is because not all valid expressions in Java are valid
lines of code.

#### Statements

Statements are like expressions but permanent. Statements are indicated by a semicolon at the end of an 
expression. Statements will only echo a value if a print call is made within the statment. Below is an example
of using a statement to define a variable and then using an expression to get the value of that variable.

```java
>>int x = 4;
>>x
4
```

#### Imports

Imports are treated as special statments. An import is permanent and maintained as long as the JI shell is open.
An example of importing `java.util.*` and then using a class and method from the import.

```java
>>import java.util.*;

>>int[] A = {1, 2, 3, 4};
>>Arrays.toString( A )
[1, 2, 3, 4]
```

#### Methods

Static and non static methods can be defined for the JI shell. Defining methods is a lot like defining functions
in the python shell. The shell will allow you to continue to add code to the function until a final curly brace is
added. Here is an example of a simple static method.

```java
>>static int squared( int x ) {
>>    return x * x;
>>}

>>squared( 12 )
144
```

You can also define non static functions and then access then through the JI class.

```java
>>int increment( int x ) {
>>    return x + 1;
>>}

>>new JI().increment( 7 )
8
```

#### Classes

JI allows you to define public classes. Unlike with methods you cannot create private classes. To modify a 
class simply define another class with the same name. The new definition will overwrite the old. Below is 
an example of implementing a simple Point class.

```java
>>class Point {
>>    
>>    int x, y;
>>    
>>    public String toString() {
>>        return "(" + x + ", " + y + ")";
>>    }
>>}

>>Point p = new Point();
>>p
(0, 0)
```

Interfaces can also be defined and used just like classes are.

#### Built-ins

There are a couple built in functions to help improve the shell experience. The first is the `source()` or
`src()` function which allows you to view previous definitions of methods and classes. Below is an example 
of this function in use.

```java
>>src( increment )
int increment( int x ) {
    return x + 1;
}
```

The `clear()` or `clr()` function will remove all statements from the Shell leaving only method and class
definitions. This is useful if you have statements which are printing information everytime you enter a new 
expression.

```java
>>System.out.println( "Hello World" );
Hello World
>>1 + 1
Hello World
2
>>clr()

>>
```

Additionally you can exit the shell by typing `exit()` or `System.out.exit()`.
## Changelog

**0.0.1** 

- Initial release

**0.0.2**

- Added support for loops as statements
- Added support for interfaces
- Improved formatting when printing source and proper tab expansion
- Added a clear command for removing statments 
- The source command will now return JI source when no arguments are passed
- Improved method and class/interface regexes
- Fixed minor color bugs
- Added unit tests

**0.0.3**

- Statements are now followed by a newline
- Fixed bug where having a whitespace in the src command would cause a crash
- Unbraced if statmenets are now supported
- If expressions (without braces) are now supported
- Only recompiles additional java files when necessary
- Added new tests

## Contact

JI is maintained by Eric Buss. You can send questions and bug reports to ejrbuss@shaw.ca