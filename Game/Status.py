class StatCalc:
    ''' 
    Contains helper functions for calculations of score and multiplier.
    Expect that the score variable is 'a' in string format.
    '''
    functions = []
    expression = "a"

    # Math operators
    @classmethod
    def evaluate(cls, score):
        ''' Evaluates the score using the stored functions and current expression. '''
        # concatenates with addition operators 
        return eval("+".join(cls.expression.join(cls.functions)).replace("a", str(score)))

    @classmethod
    def fixed(cls, value):
        cls.expression += f"+{value}"

    @classmethod
    def multiply(cls, factor):
        cls.expression = f"({cls.expression})*{factor}"

    @classmethod
    def divide(cls, divisor):
        if divisor != 0:
            cls.expression = f"({cls.expression})/{divisor}"
        else:
            return 1
        
    @classmethod
    def exponentiate(cls, power):
        cls.expression = f"({cls.expression})**{power}"
    
    
    # Data functions
    @classmethod
    def stack_expression(cls):
        cls.functions.append(cls.expression)

    @classmethod
    def clear(cls):
        cls.functions = []
        cls.expression = "a"