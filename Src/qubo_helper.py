from itertools import product

# Simple class helping creating qubo dict.
class Qubo:
    def __init__(self):
        self.dict = dict()

    def create_field(self, field):
        if field not in self.dict:
            self.dict[field] = 0

    def add_only_one_constraint(self, variables, const):
        """ Enforces sum(variables) == 1. """
        # Linear terms: -C * v_i
        for var in variables:
            self.create_field((var, var))
            self.dict[(var, var)] -= const

        # Quadratic terms: +2C * v_i * v_j
        # We use 'const' here because product() generates (i,j) and (j,i)
        for field in product(variables, variables):
            if field[0] == field[1]:
                continue
            self.create_field(field)
            self.dict[field] += const


    def add_at_most_one_constraint(self, variables, const):
        """ Enforces sum(variables) <= 1. """
        # There are NO linear terms for an "at most one" constraint.
        # We only penalize pairs of variables being on at the same time.
        for field in product(variables, variables):
            if field[0] >= field[1]: # Use >= to avoid duplicates and self-loops
                continue
            self.create_field(field)
            self.dict[field] += const

    def add(self, field, value):
        self.create_field(field)
        self.dict[field] += value

    def merge_with(self, qubo, const1, const2):
        for field, value in qubo.dict.items():
            self.add(field, value * const2)
        

    def get_dict(self):
        return self.dict.copy()