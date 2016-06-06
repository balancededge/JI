# Author: Eric Buss (ejrbuss@shaw.ca) June 2016
#======================================================================================================================#
# IMPORTS
#======================================================================================================================#
import ji
import io
import sys
import unittest
import subprocess
#======================================================================================================================#
# TESTS
#======================================================================================================================#
class TestJI(unittest.TestCase):

    def setUp(self):
        """
        Hooks subprocess.call in order to store output from running Java files. Silences stdout and stdin. Disables JI
        colors to make analysis of the output simpler.
        """
        self.stdout = []
        subprocess.call = self.call
        sys.stdout = io.StringIO()
        sys.stderr = io.StringIO()
        ji.nocolor = True

    def call(self, args, cwd):
        """
        Wraps subprocess.check_output. Stores the value of the output in self.stdout so that it may be accessed later.
        Still Returns the exit code.

        :param args: The command to run
        :param cwd: The current working directory of the subprocess
        :return: The exit code
        """
        try:
            self.stdout.append(subprocess.check_output(args, cwd=cwd).decode())
            return 0
        except subprocess.CalledProcessError:
            return 1

    def parse(self):
        """
        Cleans up and returns the sum output of self.call(). All whitespace is removed.

        :return: the output of call
        """
        return ''.join(''.join(self.stdout).split())

    def run_code(self, input, output):
        """
        Runs a code snippet and checks to see if the result is equals to the provided output.

        :param input: The code to run
        :param output: The expected output
        """
        sys.stdin = io.StringIO(input)
        try:
            ji.ji()
        except EOFError:
            pass
        self.assertEqual(output, self.parse())

    def test_file(self):
        """
        Tests to see if JI can successfully compile and run an Example java file.
        :return:
        """
        ji.ji(['Example.java'])
        self.assertEqual('HelloWorld', self.parse())
    #==================================================================================================================#
    # CODE TESTS
    #==================================================================================================================#
    def test_expression(self):
        self.run_code(
            """
            1 + 2 * 3
            """,
            '7'
        )

    def test_if_expression(self):
        self.run_code(
            """
            int x = 7;
            if ( x == 7 )
                x
            """,
            '7'
        )

    def test_statement(self):
        self.run_code(
            """
            int x = 4;
            x
            """,
            '4'
        )

    def test_if(self):
        self.run_code(
            """
            boolean x = true;
            if ( x ) {
                System.out.println( x );
            }""",
            'true'
        )

    def test_unbraced_if(self):
        self.run_code(
            """
            int x = 12;
            if ( x < 5 )
                System.out.println( x );
            """,
            ''
        )

    def test_try_catch(self):
        self.run_code(
            """
            int[] A = {1, 2, 3, 4};
            static int test( int[] A ) {
                try {
                    int a = A[-1];
                } catch( Exception e ) {
                    return 1;
                }
                return 0;
            }
            test( A )
            """,
            '1'
        )

    def test_braced_for(self):
        self.run_code(
            """
            for( int i = 0; i < 4; i++ ) {
                System.out.println( i );
            }""",
            '0123'
        )

    def test_unbraced_for(self):
        self.run_code(
            """
            for( int i = 7; i < 12; i++ )
                System.out.println( i );""",
            '7891011'
        )

    def test_braced_while(self):
        self.run_code(
            """
            int i = 7;
            while( i > 1 ) {
                System.out.println( i );
                i--;
            }""",
            '765432'
        )

    def test_unbraced_while(self):
        self.run_code(
            """
            int i = 12;
            while( i-- >= 8 )
                System.out.println( i );""",
            '1110987'
        )

    def test_do_while(self):
        self.run_code(
            """
            int i = 3;
            do {
                System.out.println( i );
            } while ( i-- > 0 );""",
            '3210'
        )

    def test_static_method(self):
        self.run_code(
            """
            public static int sqr( int x ) {
                return x * x;
            }
            sqr(12)
            """,
            '144'
        )

    def test_instance_method(self):
        self.run_code(
            """
            private int increment( int x ) {
                return x + 1;
            }
            new JI().increment( 11 )
            """,
            '12'
        )

    def test_class(self):
        self.run_code(
            """
            public class Point {

                int x, y;

                public String toString() {
                    return "(" + x + ", " + y + ")";
                }

            }
            Point p = new Point();
            p.x = 12;
            p.y = 3;
            p
            """,
            '(12,3)'
        )

    def test_interface(self):
        self.run_code(
            """
            public interface TestInterface {

                public int get();

            }
            public class TestClass implements TestInterface {

                public int get() {
                    return 42;
                }

            }
            TestInterface test = new TestClass();
            test.get()
            """,
            '42'
        )

    def test_import(self):
        self.run_code(
            """
            import java.util.*;
            int[] A = {1, 2, 3, 4};
            Arrays.toString( A )
            """,
            '[1,2,3,4]'
        )

    def test_clear(self):
        self.run_code(
            """
            System.out.println("test");
            1 + 1
            clr();
            1 + 2
            """,
            'testtest23'
        )
#======================================================================================================================#
# SCRIPT
#======================================================================================================================#
if __name__ == '__main__':
    unittest.main()