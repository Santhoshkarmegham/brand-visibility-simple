# Data cleaning - 30 answers

Sources: {'csv': 1226}. Rows: 1226. Observed rankings: 0. Known discounts: 0. Missing metrics are unavailable.


## 01. Dataset size

Input: 1320 rows. Original input column counts: [7]. Aligned columns: 13. Output: 1226 rows, 21 columns.


## 02. Original data types

[{'keyword': 'str', 'title': 'str', 'price': 'str', 'rating': 'float64', 'reviews': 'str', 'platform': 'str', 'delivery': 'str'}]


## 03. Numeric columns stored as text

['price', 'raw_price', 'reviews', 'position']


## 04. Columns containing missing values

[{'keyword': 0, 'title': 0, 'price': 126, 'rating': 131, 'reviews': 0, 'platform': 0, 'delivery': 0}]


## 05. Missing percentages

[{'keyword': 0.0, 'title': 0.0, 'price': 9.55, 'rating': 9.92, 'reviews': 0.0, 'platform': 0.0, 'delivery': 0.0}]


## 06. Handling missing price, rating and reviews

Price uses the keyword median then global median; 207 retained prices were imputed. Unobserved ratings/reviews remain null and are excluded from means; they are not zero satisfaction/engagement.


## 07. Missing delivery

Fill blank/missing delivery with Unknown.


## 08. Incorrect numeric types

Original numeric-as-text columns: ['price', 'raw_price', 'reviews', 'position']; final types: {'keyword': 'string', 'title': 'str', 'price': 'float64', 'raw_price': 'float64', 'rating': 'float64', 'reviews': 'Int64', 'platform': 'string', 'position': 'Int64', 'delivery': 'string', 'link': 'object', 'thumbnail': 'object', 'product_id': 'object', 'source': 'string', 'price_imputed': 'bool', 'discount_pct': 'float64', 'price_before_cap': 'float64', 'brand': 'str', 'visibility_score': 'float64', 'top_10': 'Int64', 'price_range': 'category', 'rating_range': 'category'}


## 09. Safe numeric conversion

Strip currency symbols, grouping commas and whitespace; require a complete numeric value; parse with errors=coerce. Do not extract a misleading partial number from a monthly installment string.


## 10. Invalid text values

Not Available, many and other invalid numeric text become missing. Counts: {'price': 66, 'raw_price': 0, 'rating': 0, 'reviews': 26, 'position': 0}


## 11. Duplicate rows

Exact duplicates before cleaning: 34.


## 12. Duplicate identity

keyword + cleaned title + standardized platform + uncapped numeric price; retain the first occurrence. Different platform offers remain distinct.


## 13. Duplicate treatment

Removed 94 duplicate offers after normalization and before price capping.


## 14. Negative and zero prices

Found 26; treat them as missing, then apply the documented median policy.


## 15. Outlier detection

Use the 99th price percentile (383160.0); 13 prices exceed it.


## 16. Other invalid values

Invalid ratings: 0; reviews: 0; positions: 0. Set invalid observations to null. Original price below selling price: 0; exclude from discount calculations.


## 17. Price distribution

{'count': 1226.0, 'mean': 33543.5, 'std': 53882.63, 'min': 509.0, '25%': 14169.75, '50%': 24365.0, '75%': 36045.0, 'max': 498050.0}


## 18. Extreme prices

13 values above the percentile cap. See price_before_cap for their original cleaned amounts.


## 19. Remove or cap outliers

Cap price at the 99th percentile. Keep price_before_cap for audit. Discounts use observed pre-cap prices so capping does not invent a promotion. This pooled cap can compress legitimate expensive categories.


## 20. Title noise

136 input titles contain characters outside the allowed title character set.


## 21. Title standardization

Remove punctuation noise such as !!!; collapse repeated spaces and trim. Preserve useful product punctuation and model numbers.


## 22. Text formatting inconsistencies

{'platform': ['AMAZON', 'CROMA', 'FLIPKART', 'RELIANCE DIGITAL', 'amazon', 'croma', 'flipkart', 'reliance digital'], 'delivery': ['2 Days', '5 Days', 'Free Delivery']}


## 23. Platform consistency

Trim/collapse whitespace and title-case names; normalize eBay and Best Buy spellings. amazon and AMAZON become Amazon.


## 24. Categorical normalization

Keywords are lowercase; platforms and delivery use title case. Missing categories are Unknown.


## 25. Delivery consistency

Original delivery labels: ['2 Days', '5 Days', 'Free Delivery']. Standardize case/whitespace; preserve the actual delivery claim.


## 26. Remaining missing values

{'price': 0, 'raw_price': 1226, 'rating': 121, 'reviews': 20, 'position': 1226}. These unknown observations are intentional, not fabricated.


## 27. Numeric usability

Prices and ratings are numeric; reviews and position are nullable integers. SQL stores absent values as NULL.


## 28. Business validity

Removed 0 rows without usable title/price. Retained prices are positive, ratings bounded 0-5, observed ranks positive integers, and discounts derived only from valid observed prices. Currency is not encoded in CSV; do not combine different currencies.


## 29. Unrated/unreviewed products

Retain them for assortment analysis. Exclude missing observations from rating/review averages; report observed coverage. Never fabricate search positions.


## 30. Additional features

Infer brand from known brand names or first title token; derive 100/position visibility, top-10 indicator, exact-boundary price/rating ranges, discount percentage, price_imputed and price_before_cap. Brand inference is heuristic.
