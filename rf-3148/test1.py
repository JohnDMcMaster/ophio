#!/usr/bin/env python3

"""
~90
    vendor list
    90 lines follow
#0,35
    a vendor follows
    35 total entries follow
    It will have nested products
$0,4
    a product follows
    4 total entries

"""


"""
75,Actrans,0,0,1,0,0,0
78,AdvanceGroup,0,1,0,0,0,1
73,ALI,0,0,1,0,0,1


....
?
V2007.01
"""

class RFDB:
    def __init__(self, fn=None):
        self.fn = "RF.INF"
        self.f = open(self.fn, "r")
        self.lines = [l.strip() for l in self.f]
        self.vendors = self.parse_segment("~")
        self.parse_segment("!")
        self.parse_segment("@")
        print("")
        print("")
        print("")
        # these appear to be catagories, not vendors
        while True:
            if self.peek_line()[0] != "#":
                break
            # print("")
            # print("New vendor %u / %u" % (vendori + 1, len(self.vendors)))
            self.parse_category()
        print("")
        print("")
        print("")
        l = self.pop_line()
        assert l == "?", l
        l = self.pop_line()
        assert l == "V2007.01", l

    def peek_line(self):
        return self.lines[0]

    def pop_line(self):
        ret = self.lines[0]
        del self.lines[0]
        return ret

    def parse_segment(self, expect_mode):
        """
        ~90
        !93
        """
        l = self.pop_line()
        print(l)
        mode = l[0]
        assert mode == expect_mode, l
        nlines = int(l[1:])
        ret = []
        for linei in range(nlines):
            l = self.pop_line()
            print("  ", l)
            if not l:
                raise Exception("oops")
            parts = l.split(",")
            ret.append(l)
        return ret

    def parse_category(self):
        """
        #0,35
        $0,4
        """
        l = self.pop_line()
        print(l)
        mode = l[0]
        assert mode == "#", l
        v1, v2 = l[1:].split(",")
        # v1 increments
        v1 = int(v1)
        # v2 is random
        # I thought it was number of lines at first
        v2 = int(v2)

        while True:
            if self.peek_line()[0] != "$":
                break

            # $0,4
            l = self.pop_line()
            print(l)
            assert l[0] == "$"
            some_id, some_lines = l[1:].split(",")
            some_id = int(some_id)
            some_lines = int(some_lines)
            for linei in range(some_lines):
                l = self.pop_line()
                print("  ", l)
                parts = l.split(",")
                assert len(parts) == 6 or len(parts) == 5

print("Parsing...")
db = RFDB()
print("ok")

