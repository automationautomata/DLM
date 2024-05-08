from fractions import Fraction
from math import gcd, ceil
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt

class Line:
    def __init__(self, x1, y1, x2, y2):
        self.x1, self.x2 = x1, x2
        self.y1, self.y2 = y1, y2
    
    def calc(self, number):
        x = np.linspace(self.x1, self.x2, number)
        k = (self.y2 - self.y1) / (self.x2 - self.x1)
        b = self.y1 - self.x1*k
        y = x*k + b
        return x, y
    
class LiniarFunction:
    def __init__(self, slopecoef, freecoef):
        self(slopecoef, freecoef, 0)
        return
    def __init__(self, slopecoef, freecoef, precision):
        self.precision = precision
        self.slopecoef_rat = Fraction(slopecoef)
        self.freecoef_rat = Fraction(freecoef)
        self.slopecoef_2adic = self.fractionTo2adic(self.slopecoef_rat)
        self.freecoef_2adic = self.fractionTo2adic(self.freecoef_rat)
        return
    
    def fractionTo2adic(self, rational):
        result = 0b00000000
        numer = rational.numerator
        denom = rational.denominator
        i = 0
        numbers = dict()

        tmp = (numer - denom)/2
        if tmp % 1 == 0:
            result += 1 << i
            numer = tmp
        else: 
            numer /= 2
        i+=1

        while int(numer) not in numbers.keys():
            numbers[int(numer)] = i
            tmp = (numer - denom)/2
            if tmp % 1 == 0:
                result += 1 << i
                numer = tmp
            else: 
                numer /= 2
            i+=1
        cycle = result >> numbers[int(numer)]
        return bin(result^(cycle << numbers[int(numer)]))[2:], bin(cycle)[2:], i - numbers[int(numer)], numbers[int(numer)]
    
    def multiplicativeOrder(self, A, N) :
        if (gcd(A, N ) != 1) :
            return -1
        # result store power of A that raised 
        # to the power N-1
        result = 1
        K = 1
        while (K < N) :
            # modular arithmetic
            result = (result * A) % N 
            # return smallest + ve integer
            if (result == 1) :
                return K
            # increment power
            K = K + 1
        return -1

    def knotnum(self):
        e = gcd(self.freecoef_rat.denominator, self.slopecoef_rat.denominator)
        return self.multiplicativeOrder(2, int(self.freecoef_rat.denominator/e))
    
    def info(self):
        format = lambda s: f"...({(s[2] - len(s[1]))*'0'}{s[1]}){(s[3] - len(s[0]))*'0'}{s[0]}"

        numbers_info = f"{self.freecoef_rat} = {format(self.freecoef_2adic)}\
                        \n{self.slopecoef_rat} = {format(self.slopecoef_2adic)}"
        knot_info = f"number of knots: {self.knotnum()}\n" #knot turns around the inner circle: {}"
        return f"{numbers_info}\n\n{knot_info}"
    
    def divideonlines(self, freecoef_rat):
        freecoef = float(freecoef_rat)
        slopecoef = float(self.slopecoef_rat)

        x_prev = -freecoef/slopecoef
        y_prev = 0
        points = [(x_prev, y_prev)]
        step = 1
        if slopecoef < 0:
            step = -1
        x_prev = ceil(x_prev) if x_prev % 1 != 0 else x_prev + step
        y_prev += 1
        y_tmp = set()

        for i in range(0, self.slopecoef_rat.denominator*step, step):
            cur_y = freecoef + slopecoef*(i+x_prev)
            cur_x = (cur_y - freecoef)/slopecoef
            if cur_y % 1 == 0:
                y_tmp.add(cur_y)
            points.append((round(cur_x, 5), round(cur_y , 5)))
        
        limit = abs(self.slopecoef_rat.numerator) - 1 
        for i in range(limit): 
            if i+y_prev not in y_tmp:
                cur_x = (i+y_prev - freecoef)/slopecoef
                cur_y = slopecoef*cur_x + freecoef
                points.append((round(cur_x, 5), round(cur_y, 5)))
            else:
                limit+=1

        points = sorted(points, key=lambda vec: (vec[0]**2 + vec[1]**2)**0.5, reverse=self.slopecoef_rat.numerator<0)
        lines = []
        data = []
        mod1 = lambda val: val%1 if val%1 != 0 else 1
        for i in range(1, len(points)):
            if points[i][1] < points[i-1][1]:
                start_y = mod1(points[i-1][1])
                end_y = points[i][1]%1
            else:
                end_y = mod1(points[i][1])
                start_y = points[i-1][1]%1
            start_x = points[i-1][0]%1
            end_x = mod1(points[i][0])
            lines.append(Line(start_x, start_y, end_x, end_y))
            data.append(lines[i-1].calc(self.precision))
        #     plt.plot(data[0], data[1])
        # plt.legend()
        # plt.grid(True)
        # plt.show()
        self.lines = lines
        return data
    
    def divideonknots(self):
        knots = []
        for i in range(self.knotnum()):
            knots.append(self.divideonlines((-self.freecoef_rat*2**i)%1))  
        return knots


