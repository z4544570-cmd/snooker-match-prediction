from datetime import datetime

# 获取当前年份
current_year = datetime.now().year

players_dict = {
    "Ronnie O'Sullivan": {
        "date_of_birth": "1975-01-16",
        "career_centuries": 1324,
        "maximum_147s": 17
    },
    "Judd Trump": {
        "date_of_birth": "1989-08-09",
        "career_centuries": 1149,
        "maximum_147s": 9
    },
    "John Higgins": {
        "date_of_birth": "1975-05-18",
        "career_centuries": 1063,
        "maximum_147s": 13
    },
    "Neil Robertson": {
        "date_of_birth": "1982-01-11",
        "career_centuries": 1038,
        "maximum_147s": 5
    },
    "Mark Selby": {
        "date_of_birth": "1983-06-19",
        "career_centuries": 961,
        "maximum_147s": 6
    },
    "Shaun Murphy": {
        "date_of_birth": "1982-08-10",
        "career_centuries": 788,
        "maximum_147s": 10
    },
    "Ding Junhui": {
        "date_of_birth": "1987-04-01",
        "career_centuries": 723,
        "maximum_147s": 7
    },
    "Mark Allen": {
        "date_of_birth": "1986-02-20",
        "career_centuries": 694,
        "maximum_147s": 5
    },
    "Mark Williams": {
        "date_of_birth": "1975-03-21",
        "career_centuries": 691,
        "maximum_147s": 3
    },
    "Stuart Bingham": {
        "date_of_birth": "1980-05-26",
        "career_centuries": 634,
        "maximum_147s": 9
    },
    "Kyren Wilson": {
        "date_of_birth": "1992-03-06",
        "career_centuries": 557,
        "maximum_147s": 5
    },
    "Marco Fu": {
        "date_of_birth": "1978-01-09",
        "career_centuries": 555,
        "maximum_147s": 5
    },
    "Stephen Maguire": {
        "date_of_birth": "1986-05-15",
        "career_centuries": 538,
        "maximum_147s": 3
    },
    "Barry Hawkins": {
        "date_of_birth": "1983-04-06",
        "career_centuries": 529,
        "maximum_147s": 3
    },
    "Ryan Day": {
        "date_of_birth": "1982-05-22",
        "career_centuries": 480,
        "maximum_147s": 4
    },
    "Ali Carter": {
        "date_of_birth": "1979-07-25",
        "career_centuries": 464,
        "maximum_147s": 4
    },
    "David Gilbert": {
        "date_of_birth": "1981-07-10",
        "career_centuries": 449,
        "maximum_147s": 3
    },
    "Ricky Walden": {
        "date_of_birth": "1981-09-08",
        "career_centuries": 392,
        "maximum_147s": 0
    },
    "Jack Lisowski": {
        "date_of_birth": "1992-10-22",
        "career_centuries": 386,
        "maximum_147s": 0
    },
    "Xiao Guodong": {
        "date_of_birth": "1989-09-08",
        "career_centuries": 362,
        "maximum_147s": 3
    },
    "Matthew Stevens": {
        "date_of_birth": "1977-09-04",
        "career_centuries": 361,
        "maximum_147s": 1
    },
    "Tom Ford": {
        "date_of_birth": "1985-10-28",
        "career_centuries": 319,
        "maximum_147s": 5
    },
    "Gary Wilson": {
        "date_of_birth": "1986-01-19",
        "career_centuries": 311,
        "maximum_147s": 6
    },
    "Liang Wenbo": {
        "date_of_birth": "1987-01-26",
        "career_centuries": 284,
        "maximum_147s": 3
    },
    "Anthony McGill": {
        "date_of_birth": "1992-04-12",
        "career_centuries": 263,
        "maximum_147s": 0
    },
    "Graeme Dott": {
        "date_of_birth": "1977-05-16",
        "career_centuries": 263,
        "maximum_147s": 2
    },
    "Zhou Yuelong": {
        "date_of_birth": "1997-07-31",
        "career_centuries": 258,
        "maximum_147s": 3
    },
    "Michael Holt": {
        "date_of_birth": "1980-12-09",
        "career_centuries": 254,
        "maximum_147s": 0
    },
    "Martin Gould": {
        "date_of_birth": "1981-11-21",
        "career_centuries": 253,
        "maximum_147s": 1
    },
    "Zhao Xintong": {
        "date_of_birth": "1997-01-29",
        "career_centuries": 240,
        "maximum_147s": 1
    },
    "Matthew Selt": {
        "date_of_birth": "1984-02-04",
        "career_centuries": 230,
        "maximum_147s": 1
    },
    "Luca Brecel": {
        "date_of_birth": "1994-09-08",
        "career_centuries": 228,
        "maximum_147s": 1
    },
    "Jimmy Robertson": {
        "date_of_birth": "1985-04-27",
        "career_centuries": 222,
        "maximum_147s": 0
    },
    "Thepchaiya Un-Nooh": {
        "date_of_birth": "1989-07-03",
        "career_centuries": 222,
        "maximum_147s": 7
    },
    "Robert Milkins": {
        "date_of_birth": "1981-08-06",
        "career_centuries": 206,
        "maximum_147s": 3
    },
    "Kurt Maflin": {
        "date_of_birth": "1987-10-01",
        "career_centuries": 203,
        "maximum_147s": 2
    },
    "Zhang Anda": {
        "date_of_birth": "1996-02-16",
        "career_centuries": 199,
        "maximum_147s": 5
    },
    "Ben Woollaston": {
        "date_of_birth": "1985-04-28",
        "career_centuries": 183,
        "maximum_147s": 1
    },
    "Noppon Saengkham": {
        "date_of_birth": "1993-10-25",
        "career_centuries": 175,
        "maximum_147s": 2
    },
    "Jamie Jones": {
        "date_of_birth": "1988-02-15",
        "career_centuries": 175,
        "maximum_147s": 1
    },
    "Jak Jones": {
        "date_of_birth": "1994-07-05",
        "career_centuries": 169,
        "maximum_147s": 1
    },
    "Hossein Vafaei": {
        "date_of_birth": "1993-03-05",
        "career_centuries": 165,
        "maximum_147s": 1
    },
    "Chris Wakelin": {
        "date_of_birth": "1988-09-29",
        "career_centuries": 143,
        "maximum_147s": 1
    },
    "Yuan Sijun": {
        "date_of_birth": "1999-08-21",
        "career_centuries": 138,
        "maximum_147s": 0
    },
    "Yan Bingtao": {
        "date_of_birth": "2000-02-26",
        "career_centuries": 150,
        "maximum_147s": 0
    },
    "Wu Yize": {
        "date_of_birth": "2002-05-09",
        "career_centuries": 146,
        "maximum_147s": 1
    },
    "Si Jiahui": {
        "date_of_birth": "2002-11-11",
        "career_centuries": 114,
        "maximum_147s": 1
    },
    "Lyu Haotian": {
        "date_of_birth": "1998-08-18",
        "career_centuries": 111,
        "maximum_147s": 0
    },
    "Scott Donaldson": {
        "date_of_birth": "1993-11-29",
        "career_centuries": 103,
        "maximum_147s": 0
    },
    "Joe O'Connor": {
        "date_of_birth": "1997-02-13",
        "career_centuries": 122,
        "maximum_147s": 1
    },
    "Pang Junxu": {
        "date_of_birth": "2002-07-23",
        "career_centuries": 93,
        "maximum_147s": 0
    },
    "Aaron Hill": {
        "date_of_birth": "1996-09-23",
        "career_centuries": 50,
        "maximum_147s": 2
    },
    "Jackson Page": {
        "date_of_birth": "2002-12-04",
        "career_centuries": 65,
        "maximum_147s": 2
    },
    "Xu Si": {
        "date_of_birth": "1993-01-05",
        "career_centuries": 77,
        "maximum_147s": 3
    },
    "Fan Zhengyi": {
        "date_of_birth": "2001-11-28",
        "career_centuries": 70,
        "maximum_147s": 2
    },
    "Louis Heathcote": {
        "date_of_birth": "1997-03-04",
        "career_centuries": 71,
        "maximum_147s": 0
    },
    "Elliot Slessor": {
        "date_of_birth": "1993-10-30",
        "career_centuries": 116,
        "maximum_147s": 0
    },
    "Daniel Wells": {
        "date_of_birth": "1989-04-07",
        "career_centuries": 118,
        "maximum_147s": 0
    },
    "Jordan Brown": {
        "date_of_birth": "1987-10-14",
        "career_centuries": 80,
        "maximum_147s": 0
    },
    "He Guoqiang": {
        "date_of_birth": "1997-08-15",
        "career_centuries": 50,
        "maximum_147s": 0
    },
    "Cao Yupeng": {
        "date_of_birth": "1989-04-02",
        "career_centuries": 81,
        "maximum_147s": 1
    },
    "Lei Peifan": {
        "date_of_birth": "2004-04-26",
        "career_centuries": 47,
        "maximum_147s": 0
    },
    "Mark Davis": {
        "date_of_birth": "1972-08-14",
        "career_centuries": 303,
        "maximum_147s": 2
    },
    "David Lilley": {
        "date_of_birth": "1975-10-12",
        "career_centuries": 48,
        "maximum_147s": 0
    },
    "Long Zehuang": {
        "date_of_birth": "2001-05-13",
        "career_centuries": 35,
        "maximum_147s": 0
    },
    "Anthony Hamilton": {
        "date_of_birth": "1971-01-16",
        "career_centuries": 316,
        "maximum_147s": 0
    },
    "Sanderson Lam": {
        "date_of_birth": "1993-10-21",
        "career_centuries": 34,
        "maximum_147s": 0
    },
    "Ben Mertens": {
        "date_of_birth": "2005-01-02",
        "career_centuries": 43,
        "maximum_147s": 0
    },
    "Luca Brecel": {
        "date_of_birth": "1994-09-08",
        "career_centuries": 228,
        "maximum_147s": 1
    },
    "Zak Surety": {
        "date_of_birth": "1993-09-14",
        "career_centuries": 46,
        "maximum_147s": 2
    },
    "Euan Henderson": {
        "date_of_birth": "2001-07-10",
        "career_centuries": 45,
        "maximum_147s": 0
    },
    "Dylan Emery": {
        "date_of_birth": "2001-08-09",
        "career_centuries": 40,
        "maximum_147s": 0
    },
    "Chang Bingyu": {
        "date_of_birth": "2002-08-08",
        "career_centuries": 79,
        "maximum_147s": 2
    },
    "Ross Muir": {
        "date_of_birth": "1997-06-22",
        "career_centuries": 41,
        "maximum_147s": 1
    },
    "Michael Georgiou": {
        "date_of_birth": "1990-03-17",
        "career_centuries": 41,
        "maximum_147s": 1
    },
    "Sam Craigie": {
        "date_of_birth": "1993-07-15",
        "career_centuries": 116,
        "maximum_147s": 0
    },
    "Oliver Lines": {
        "date_of_birth": "1996-11-09",
        "career_centuries": 63,
        "maximum_147s": 0
    },
    "Liam Highfield": {
        "date_of_birth": "1992-04-28",
        "career_centuries": 123,
        "maximum_147s": 0
    },
    "Robbie Williams": {
        "date_of_birth": "1978-04-30",
        "career_centuries": 100,
        "maximum_147s": 0
    },
    "Martin O'Donnell": {
        "date_of_birth": "1988-06-29",
        "career_centuries": 78,
        "maximum_147s": 0
    }
}
