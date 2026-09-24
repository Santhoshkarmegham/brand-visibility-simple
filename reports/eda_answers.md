# EDA - 30 answers

Sources: {'csv': 1226}. Rows: 1226. Observed rankings: 0. Known discounts: 0. Missing metrics are unavailable.


NaN, <NA>, or empty results mean insufficient observed data, not zero. Correlation does not establish causation. Lower position is better, so a negative position correlation indicates association with better ranking.

## 01 Products Per Keyword

```text
keyword
microwave oven convection    262
men running shoes            244
power bank fast charging     243
air fryer india              240
office chair ergonomic       237
```


## 02 Overall Average Price

```text
33006.58482871125
```


## 03 Price Distribution

```text
count      1226.000000
mean      33006.584829
std       49839.354672
min         509.000000
25%       14169.750000
50%       24365.000000
75%       36045.000000
max      383160.000000
```


## 04 Average Rating

```text
3.7929411764705883
```


## 05 Review Distribution

```text
count         1206.0
mean     2419.168325
std      1434.393147
min             14.0
25%          1129.25
50%           2333.0
75%           3643.0
max           4997.0
```


## 06 Most Frequent Brand

```text
HP
```


## 07 Brand Highest Visibility

```text
Unavailable: no observed values
```


## 08 Average Position By Brand

```text
brand
Boat       <NA>
Dell       <NA>
HP         <NA>
LG         <NA>
Nike       <NA>
Philips    <NA>
Puma       <NA>
Samsung    <NA>
Sony       <NA>
```


## 09 Brands Most In Top 10

```text
Series([], )
```


## 10 Brand Highest Rating

```text
brand
Sony       3.872222
HP         3.867153
Puma       3.827642
Boat       3.825210
Philips    3.806349
Dell       3.782759
Nike       3.764000
LG         3.746809
Samsung    3.636364
```


## 11 Price By Brand

```text
         count          mean           std     min       25%      50%       75%       max
brand
Boat     135.0  40829.711111  71636.340672  1312.0  12986.50  23854.0  37437.00  383160.0
Dell     125.0  37854.568000  65164.343529   580.0  15091.00  25576.0  35292.00  383160.0
HP       157.0  31656.754777  44280.367714  1014.0  15909.00  24658.0  38318.00  383160.0
LG       152.0  29057.944079  33216.202792  1377.0  14384.75  24365.0  36334.50  320280.0
Nike     135.0  33180.633333  55259.019487   509.0  14307.00  23979.0  33801.00  383160.0
Philips  139.0  29327.528777  39899.454002   545.0  13125.00  24365.0  32635.00  383160.0
Puma     136.0  37497.705882  46388.402964   889.0  16054.00  25335.0  42077.00  286470.0
Samsung  128.0  26779.691406  28083.385220   712.0  14093.00  24365.0  32456.75  289730.0
Sony     119.0  31528.760504  51496.527856  1095.0  12566.00  24365.0  35393.50  383160.0
```


## 12 Price Range Distribution

```text
price_range
1,000+        1218
500-999.99       8
Under 50         0
50-149.99        0
150-499.99       0
```


## 13 Price Position Correlation

```text
nan
```


## 14 Average Price By Platform

```text
platform
Flipkart            30291.846831
Croma               30991.883333
Amazon              34733.514151
Reliance Digital    35556.685185
```


## 15 Highest Price By Keyword

```text
                        keyword                                     title     price
1212            air fryer india            Nike air fryer India Model 162  383160.0
266           men running shoes            HP men running shoes Model 483  383160.0
34    microwave oven convection  Dell microwave oven convection Model 272  383160.0
282      office chair ergonomic     Boat office chair ergonomic Model 324  383160.0
374    power bank fast charging   Nike power bank fast charging Model 406  383160.0
```


## 16 Percent Discounted

```text
nan
```


## 17 Discounted Vs Ranking

```text
Series([], )
```


## 18 Brand Highest Discount

```text
brand
Boat      NaN
Dell      NaN
HP        NaN
LG        NaN
Nike      NaN
Philips   NaN
Puma      NaN
Samsung   NaN
Sony      NaN
```


## 19 Platform Highest Discount

```text
platform
Amazon             NaN
Croma              NaN
Flipkart           NaN
Reliance Digital   NaN
```


## 20 Discount Rating Correlation

```text
nan
```


## 21 Platform Most Products

```text
platform
Reliance Digital    324
Amazon              318
Croma               300
Flipkart            284
```


## 22 Platform Highest Rating

```text
platform
Croma               3.829474
Flipkart            3.807480
Amazon              3.800000
Reliance Digital    3.736268
```


## 23 Platform Lowest Price

```text
platform
Flipkart            30291.846831
Croma               30991.883333
Amazon              34733.514151
Reliance Digital    35556.685185
```


## 24 Average Position By Platform

```text
platform
Amazon              <NA>
Croma               <NA>
Flipkart            <NA>
Reliance Digital    <NA>
```


## 25 Brand By Platform

```text
brand             Boat  Dell  HP  LG  Nike  Philips  Puma  Samsung  Sony
platform
Amazon              45    31  45  32    27       38    38       36    26
Croma               29    28  40  36    37       33    31       29    37
Flipkart            25    39  32  33    38       32    35       22    28
Reliance Digital    36    27  40  51    33       36    32       41    28
```


## 26 Position Distribution

```text
count     0.0
mean     <NA>
std      <NA>
min      <NA>
25%      <NA>
50%      <NA>
75%      <NA>
max      <NA>
```


## 27 Highest Visibility Products

```text
Empty DataFrame
Columns: [title, brand, visibility_score]
Index: []
```


## 28 Rating Position Correlation

```text
nan
```


## 29 Reviews Position Correlation

```text
nan
```


## 30 Top Rank Factor Comparison

```text
         top_10_mean  other_mean
price           <NA>        <NA>
rating          <NA>        <NA>
reviews         <NA>        <NA>
```
