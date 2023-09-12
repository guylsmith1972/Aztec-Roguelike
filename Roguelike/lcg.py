class LCG:
    def __init__(self, seed=0, a=1664525, c=1013904223, m=2**32):
        self.state = seed
        self.a = a
        self.c = c
        self.m = m

    def random(self):
        self.state = (self.a * self.state + self.c) % self.m
        return self.state / self.m

    def random_range(self, low, high):
        return self.random() * (high-low) + low
