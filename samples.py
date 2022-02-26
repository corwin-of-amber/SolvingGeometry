SAMPLES = {
    "test": ["angle(a,b,c)=90"],
    "triangle": ["dist(X,Y)=136",
                "X!=Y",
                "X=Point(0,0)",
                "dist(Z,Y)=136",
                "X!=Z",
                "Z=Point(136,0)",
                        "?(Y)"],
    "myTriangle": ["?(W)",
                    "?(Y)",
                    "X=Point(0, 0)",
                    "Z=Point(1, 0)",
                    "W!=X",
                    "dist(X,Y)=1",
                    "dist(Z,Y)=1",
                    "dist(W,Y)=1",
                    "dist(Z,W)=1"
                    ],
    "square": ["dist(A,B)=d",
               "dist(B,C)=d",
               "dist(C,D)=d",
               "dist(D,A)=d",
               "A!=B",
               "A!=C",
               "B!=D",
               "angle(A,D,C)=90",
               "A=Point(0,0)",
               "B=Point(1,0)",
               "?(C)",
               "?(D)"
    ],
    "square2": [#"MakeLine(A, B)",
                #"MakeLine(B, C)",
                "dist(A,B)=1",
                "dist(B,C)=1",
                "dist(C,D)=1",
                "angle(A,B,C)=90",
                "A=Point(0,0)",
                "B=Point(1,0)",
                "?(C)", "?(D)"
    ],
    "pentagon": ["dist(A,B)=d", "dist(B,C)=d", "dist(C,D)=d",
                "dist(D,E)=d", "dist(E,A)=d",
                "angleCcw(A,B,C)=a", "angleCcw(B,C,D)=a",
                "angleCcw(C,D,E)=a", "angleCcw(D,E,A)=a",
                "angleCcw(E,A,B)=a",
                # TODO: Implement intersect2segmentsQ, realnot
                #"intersect2segmentsQ(A,B,C,D,q)",
                #"realnot(q)",
                "D!=A", "A!=C",
                "A=Point(0, 0)", "C=Point(2,0)",
                "?(B)", "?(D)", "?(E)"],
    "pentagon2": ["d=1.23606",
                "dist(A,B)=d", "dist(B,C)=d", "dist(C,D)=d",
                "dist(D,E)=d", "dist(E,A)=d",
                "angleCcw(A,B,C)=108", "angleCcw(B,C,D)=108",
                "angleCcw(C,D,E)=108", "angleCcw(D,E,A)=108",
                "angleCcw(E,A,B)=108",
                # TODO: Implement intersect2segmentsQ, realnot
                #"intersect2segmentsQ(A,B,C,D,q)",
                #"realnot(q)",
                "D!=A", "A!=C",
                "A=Point(0, 0)", "C=Point(2,0)",
                "?(B)", "?(D)", "?(E)"],
    "9gon": ["dist(A,B)=d", "dist(B,C)=d", "dist(C,D)=d",
            "dist(D,E)=d", "dist(E,F)=d", "dist(F,G)=d",
            "dist(G,H)=d", "dist(H,I)=d", "dist(I,A)=d", "angleCcw(A,B,C)=a",
            "angleCcw(B,C,D)=a", "angleCcw(C,D,E)=a",
            "angleCcw(D,E,F)=a", "angleCcw(E,F,G)=a",
            "angleCcw(F,G,H)=a", "angleCcw(G,H,I)=a",
            "angleCcw(H,I,A)=a", "angleCcw(I,A,B)=a",
            "A=Point(0,0)", "B=Point(1,1)", "D!=A",
            "?(C)", "?(D)", "?(E)", "?(F)", "?(G)", "?(H)", "?(I)"
            #realont(q1), realnot(q2), intersect_2_segments
            ],
    "square-in-square":
          ["dist(A,B)=d", "dist(B,C)=d", "dist(C,D)=d", "dist(D,A)=d", "A!=B", "A!=C", "B!=D",
          #"angleCw(A,D,C)=90",
           "angleCcw(A,D,C)=90",
           "segment(A,B,AB)","in(E,AB)", "dist(A,E)=15",
           "segment(B,C,BC)","in(F,BC)","!in(F,CD)",
           "segment(C,D,CD)", "in(G,CD)", "!in(G,DA)",
           "segment(D,A,DA)", "in(H,DA)",
           "angle(E,F,G)=90",
           "angle(F,G,H)=90",
           "angle(G,H,E)=90",
           "A=Point(0,0)", "B=Point(60,0)","?(C)", "?(D)"
           "?(E)", "?(F)", "?(G)", "?(H)"
           ],
   "square-in-triangle":
            ["A=Point(0,0)", "B=Point(2,0)",
            "C=Point(1,1)",
             "segment(A,B,AB)", "in(D,AB)",
             "in(E,AB)",
             "segment(A,C,AC)", "in(F,AC)",
             "segment(B,C,BC)", "in(G,BC)",
             "angle(D,E,F,90)",
             "angle(E,D,G,90)",
             "angle(D,G,F,90)",
             "dist(D,E,d)", "dist(E,F,d)",
             "D!=E", "D!=A", "D!=B", "E!=B", "E!=A",
             "!colinear(A,C,D)",
             "!colinear(A,B,C)",
             "!colinear(D,E,F)", "!colinear(D,E,C)","!colinear(E,F,C)",
             "!colinear(D,G,B)",
#                 "[!colinear](G,A,C)",
             #"dist(E,D,x) & dist(E,F,x)",
             "?(D)", "?(E)", "?(F)","?(G)"
             ],
    'tut:middle-1': # This is where I got so far (it doesnt work)
            ["segment(A,B,AB)", "in(E,AB)", "dist(A,E,a)",
            "dist(E,B,a)", "segment(B,C,BC)", "in(D,BC)",
            "dist(B,D,b)", "dist(D,C,b)",
             "segment(C,A,CA)", "in(F,CA)", "dist(C,F,c)",
             "dist(F,A,c)", "dist(A,B,d)", "dist(A,C,d)",
            "A!=D",
            "A=Point(2,2)","B=Point(0,0)",
            "?(C)", "?(D)", "?(E)", "?(F)"],
     'SAT:angles-1': [
            "dist(O,A,100)", "dist(O,R,100)",
            "O!=B", "O!=L",
            "angleCcw(B,O,A,40)", "angleCcw(R,O,L,25)",
             "middle(L,A,O)", "middle(K,B,O)",
             "O=Point(0,0)", "B=Point(10, 0)",
             #TODO: Make known an option"known(O)", "known(B)", 
             "?(A)", "?(R)", "?(L)", "?(K)"],
     'SAT:clover': [
            "angleCcw(D,A,B,50)", "angleCcw(C,D,A,45)",
            "angleCcw(A,B,F,50)", "angleCcw(B,F,E,60)",
           "angleCcw(F,E,C,90)", "segment(A,B,AB)",
            "segment(C,D,CD)", "in(P,AB)", "in(P,CD)",
            "C!=D",
            # & [!=](AB,CD)",
           "segment(E,F,EF)", "in(P,EF)", # & [!=](AB,EF) & [!=](CD,EF)",
           "A=Point(0,0)", "B=Point(5, 0)",
           "?(C)", "?(D)", "?(E)", "?(F)", "?(P)"]
}