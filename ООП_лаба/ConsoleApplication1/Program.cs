using System;

namespace ConsoleApplication1
{
    internal class Program
    {
        public static void Main(string[] args)
        {
            Shape[] shapes = new Shape[] { new Circle("c1", 10), new Circle("c2", -10), 
                new Circle("c3", 6), new Rect("r1", 15, 20), new Rect("r2", -10, 5),
                new Rect("r3", 5, 0), new Triangle("t1", 1,5,2), 
                new Triangle("t2", 1, 5, -4), new Triangle("t3", 6, 7,8)};
            Console.WriteLine("Perimetrs:");
            foreach (var VARIABLE in shapes)
            {
                VARIABLE.print_perimetr();
            }
            Console.WriteLine("\n\nSquares:");
            foreach (var VARIABLE in shapes)
            {
                if(VARIABLE is Circle)
                    VARIABLE.print_square();
            }
            Console.WriteLine("\n\n");
            Square kvadr = new Square("k1", 5, 5);
            kvadr.print_diagonal();
            kvadr.print_number_of_corners();
        }
    }

    public interface ICorners
    {
        void print_number_of_corners();
    }
    public abstract class Shape
    {
        public string name;
        public abstract void print_square();
        public abstract void print_perimetr();
        public Shape(string name)
        {
            this.name = name;
        }
    }
    
    // Специализация
    public class Circle : Shape
    {
        private int radius;
        public override void print_square()
        {
            if (radius < 0)
            {
                Console.WriteLine($"{name} error: wrong radius");
            }
            else
            {
                Console.WriteLine($"{name} square={3.14*radius*radius}");
            }
        }

        public void print_diametr()
        {
            if (radius < 0)
            {
                Console.WriteLine($"{name} error: wrong radius");
            }
            else
            {
                Console.WriteLine($"{name} diametr={2*radius}");
            }
        }
        
        public override void print_perimetr()
        {
            if (radius < 0)
            {
                Console.WriteLine($"{name} error: wrong radius");
            }
            else
            {
                Console.WriteLine($"{name} square={2*3.14*radius}");
            }
        }

        public Circle(string name, int radius) : base(name)
        {
            this.radius = radius;
        }
    }

    // Спецификация
    public class Rect : Shape, ICorners
    {
        protected int side1;
        protected int side2;
        private int corners = 4;
        public Rect(string name, int side1, int side2) : base(name)
        {
            this.side1 = side1;
            this.side2 = side2;
        }

        public override void print_square()
        {
            if (side1 < 0 || side2 < 0)
            {
                Console.WriteLine($"{name} error: wrong sides");
            }
            else
            {
                Console.WriteLine($"{name} square={side1*side2}");
            }
        }

        public override void print_perimetr()
        {
            if (side1 < 0 || side2 < 0)
            {
                Console.WriteLine($"{name} error: wrong sides");
            }
            else
            {
                Console.WriteLine($"{name} square={2 * (side1 + side2)}");
            }
        }

        public void print_number_of_corners()
        {
            Console.WriteLine($"{name} have {corners} corners");
        }
    }

    // Расширение
    public class Square : Rect
    {
        public void print_diagonal()
        {
            if (side1 < 0 || side2 < 0)
            {
                Console.WriteLine($"{name} error: wrong sides");
            }
            else if (side1 != side2)
            {
                Console.WriteLine("It's not Square");
            }
            else
            {
                Console.WriteLine($"{name} diagonal={Math.Sqrt(2)*side1}");
            }
        }
        public Square(string name, int side1, int side2) : base(name, side1, side2)
        {
        }
    }
    
    // Спецификация
    public class Triangle : Shape
    {
        public int side1;
        public int side2;
        public int side3;
        private float p;
        public Triangle(string name, int side1, int side2, int side3) : base(name)
        {
            this.side1 = side1;
            this.side2 = side2;
            this.side3 = side3;
            // ReSharper disable once PossibleLossOfFraction
            p = (float)((side1 + side3 + side2)) / 2;
        }

        public override void print_square()
        {
            if (side1 < 0 || side2 < 0 || side3 < 0 || (side1+side2<side3) || (side1+side3<side2) || (side3+side2<side1))
            {
                Console.WriteLine($"{name} error: wrong sides");
            }
            else
            {
                Console.WriteLine($"{name} square={Math.Sqrt(p*(p-side1)*(p-side2)*(p-side3))}");
            }
        }

        public override void print_perimetr()
        {
            if (side1 < 0 || side2 < 0 || side3 < 0 || (side1+side2<side3) || (side1+side3<side2) || (side3+side2<side1))
            {
                Console.WriteLine($"{name} error: wrong sides");
            }
            else
            {
                Console.WriteLine($"{name} square={side1+side2+side3}");
            }
        }
    }
}