# Brand Visibility - 30 EDA Answers

## 01 Products Per Keyword

```text
keyword
laptop        45
phone         45
headphones    45
smartwatch    45
Name: count, dtype: int64
```

## 02 Overall Average Price

```text
437.9017233333333
```

## 03 Price Distribution

```text
count     180.000000
mean      437.901723
std       310.925909
min        59.610000
25%       183.165000
50%       321.475000
75%       691.635000
max      1226.170100
Name: price, dtype: float64
```

## 04 Average Rating

```text
4.273333333333333
```

## 05 Review Distribution

```text
count      180.000000
mean      1018.938889
std       1630.439390
min          4.000000
25%        128.250000
50%        467.500000
75%       1160.750000
max      13888.000000
Name: reviews, dtype: float64
```

## 06 Most Frequent Brand

```text
Apple
```

## 07 Brand Highest Visibility

```text
Bose
```

## 08 Average Position By Brand

```text
brand
Garmin        17.300000
Dell          17.875000
Bose          18.428571
Google        19.105263
Apple         19.933333
Acer          21.200000
Sony          21.400000
Samsung       21.428571
HP            22.571429
JBL           23.750000
OnePlus       24.400000
Fitbit        27.250000
Motorola      27.285714
Sennheiser    28.375000
Lenovo        29.750000
Asus          30.142857
Amazfit       31.125000
Beats         32.000000
Xiaomi        35.500000
Name: position, dtype: float64
```

## 09 Brands Most In Top 10

```text
brand
Apple       8
Google      5
Samsung     4
OnePlus     4
Acer        3
JBL         3
Garmin      3
Dell        2
Bose        2
Asus        1
HP          1
Motorola    1
Sony        1
Beats       1
Amazfit     1
Name: count, dtype: int64
```

## 10 Brand Highest Rating

```text
brand
Dell          4.487500
Motorola      4.414286
Apple         4.310000
Xiaomi        4.300000
Amazfit       4.300000
Asus          4.300000
Sony          4.300000
HP            4.300000
OnePlus       4.273333
Acer          4.260000
Beats         4.257143
Google        4.236842
Samsung       4.235714
JBL           4.225000
Sennheiser    4.212500
Garmin        4.200000
Fitbit        4.200000
Bose          4.185714
Lenovo        4.125000
Name: rating, dtype: float64
```

## 11 Price By Brand

```text
            count        mean         std     min       25%      50%        75%        max
brand                                                                                     
Acer         10.0  855.551000  254.319522  490.64  643.3825  811.440  1091.6225  1223.6900
Amazfit       8.0  262.396250   68.057117  137.70  221.5925  285.760   310.2125   329.2700
Apple        30.0  434.948333  337.772044   59.61  153.6200  307.890   761.2975  1149.0200
Asus          7.0  685.435729  316.895090  307.48  488.1050  556.180   866.0050  1226.1701
Beats         7.0  138.462857   50.047200   78.88   99.2600  133.200   170.6300   217.3800
Bose          7.0  156.608571   74.839610   68.95  122.7000  138.050   167.8850   308.0900
Dell          8.0  815.595000  137.466026  607.61  715.0050  844.155   931.6775   960.8900
Fitbit        4.0  231.537500   81.115851  111.75  217.4475  263.650   277.7400   287.1000
Garmin       10.0  197.238000   94.351204   71.16  122.1900  197.840   233.3075   381.2600
Google       19.0  385.216316  220.004055  127.56  224.4650  308.050   540.8350   808.1600
HP            7.0  865.425729  314.802461  428.19  642.9600  985.930  1065.8850  1226.1701
JBL           8.0  173.087500   69.567197   91.10  137.9700  159.040   194.0300   313.2600
Lenovo        4.0  772.432500  112.803453  675.91  713.6125  739.550   798.3700   934.7200
Motorola      7.0  627.792857  178.546511  324.42  538.4050  710.140   736.4450   810.2900
OnePlus      15.0  540.206667  174.561799  245.98  450.3850  523.480   600.1700   967.4500
Samsung      14.0  364.401429  296.257822   86.45  132.8850  285.935   430.5650  1061.6100
Sennheiser    8.0  210.410000   29.723299  174.23  191.8050  204.960   223.1500   267.7900
Sony          5.0  146.204000   66.663456   92.92  109.2800  127.000   140.8300   260.9900
Xiaomi        2.0  483.625000  126.338769  394.29  438.9575  483.625   528.2925   572.9600
```

## 12 Price Range Distribution

```text
price_range
$150-$499    82
$500-$999    55
$50-$149     33
$1,000+      10
Name: count, dtype: int64
```

## 13 Price Position Correlation

```text
-0.0351740394570901
```

## 14 Average Price By Platform

```text
platform
Ebay        395.626000
Amazon      428.983190
Target      440.048889
Walmart     447.242002
Best Buy    489.617895
Name: price, dtype: float64
```

## 15 Highest Price By Keyword

```text
        keyword                          title      price
109  headphones  Apple Essential Headphones 66   359.6000
9        laptop         HP Essential Laptop 64  1226.1701
45        phone     Samsung Essential Phone 76  1061.6100
147  smartwatch       Garmin Pro Smartwatch 84   381.2600
```

## 16 Percent Discounted

```text
76.11111111111111
```

## 17 Discounted Vs Ranking

```text
discount_pct
False    18.186047
True     24.510949
Name: position, dtype: float64
```

## 18 Brand Highest Discount

```text
brand
Sony          20.000000
Beats         19.285714
Lenovo        17.500000
Asus          16.452857
Fitbit        16.250000
JBL           15.000000
Apple         13.000000
Garmin        12.900000
Amazfit       12.500000
OnePlus       12.400000
Dell          11.875000
Samsung       11.714286
Motorola      10.571429
Xiaomi        10.000000
Acer           9.700000
Google         9.263158
HP             6.682857
Sennheiser     6.500000
Bose           5.571429
Name: discount_pct, dtype: float64
```

## 19 Platform Highest Discount

```text
platform
Amazon      13.561739
Best Buy    13.105263
Ebay        12.800000
Target      10.703704
Walmart      9.870889
Name: discount_pct, dtype: float64
```

## 20 Discount Rating Correlation

```text
0.11810901261181819
```

## 21 Platform Most Products

```text
platform
Amazon      69
Walmart     45
Target      27
Ebay        20
Best Buy    19
Name: count, dtype: int64
```

## 22 Platform Highest Rating

```text
platform
Best Buy    4.300000
Walmart     4.282222
Amazon      4.279710
Target      4.266667
Ebay        4.215000
Name: rating, dtype: float64
```

## 23 Platform Lowest Price

```text
platform
Ebay        395.626000
Amazon      428.983190
Target      440.048889
Walmart     447.242002
Best Buy    489.617895
Name: price, dtype: float64
```

## 24 Average Position By Platform

```text
platform
Best Buy    19.368421
Ebay        21.050000
Target      23.481481
Amazon      23.550725
Walmart     24.266667
Name: position, dtype: float64
```

## 25 Brand By Platform

```text
brand     Acer  Amazfit  Apple  Asus  Beats  Bose  Dell  Fitbit  Garmin  Google  HP  JBL  Lenovo  Motorola  OnePlus  Samsung  Sennheiser  Sony  Xiaomi
platform                                                                                                                                              
Amazon       4        5     12     1      5     1     1       2       4       6   5    3       1         2        6        4           3     3       1
Best Buy     3        0      2     1      1     1     1       0       1       2   0    1       0         1        2        2           1     0       0
Ebay         1        0      3     2      0     0     0       1       3       1   0    2       1         0        3        2           1     0       0
Target       0        0      6     1      1     2     2       1       1       2   1    1       0         1        2        4           0     1       1
Walmart      2        3      7     2      0     3     4       0       1       8   1    1       2         3        2        2           3     1       0
```

## 26 Position Distribution

```text
count    180.0000
mean      23.0000
std       13.0234
min        1.0000
25%       12.0000
50%       23.0000
75%       34.0000
max       45.0000
Name: position, dtype: float64
```

## 27 Highest Visibility Products

```text
                              title    brand  visibility_score
0                Acer Max Laptop 21     Acer            100.00
45       Samsung Essential Phone 76  Samsung            100.00
90         Bose Ultra Headphones 89     Bose            100.00
135        Garmin Pro Smartwatch 74   Garmin            100.00
1         Apple Essential Laptop 79    Apple             50.00
46               Apple Max Phone 86    Apple             50.00
91        Apple Ultra Headphones 46    Apple             50.00
136  Google Essential Smartwatch 89   Google             50.00
2               Dell Plus Laptop 37     Dell             33.33
47           OnePlus Ultra Phone 67  OnePlus             33.33
```

## 28 Rating Position Correlation

```text
-0.023950658976585378
```

## 29 Reviews Position Correlation

```text
0.047342423392799336
```

## 30 Top Rank Factor Comparison

```text
         top_10_mean   other_mean
price     444.606753   435.986001
rating      4.305000     4.264286
reviews   961.375000  1035.385714
```
